"""Interface for Github Actions pipeline."""
import os
import logging
import argparse
import subprocess  # noqa:S404 # Use of sls required
from typing import Tuple, List, Union, Dict, Any
from pathlib import Path
from collections import defaultdict
from eb7_sls_helper.src.sls_function import Lambda

Deployment = Lambda._Deployment
Endpoints_Dict = Dict[str, List[str]]
Deployment_Dict = Dict[str, Union[str, Endpoints_Dict]]


def setup_logging(verbosity: int, base_loglevel: int) -> logging.Logger:
    """Sets up logger.

    Args:
        verbosity (int): verbosity level as count of -v in CLI; min value 0
        base_loglevel (int): base log_level as set in env params; values
            between 0 and 50 are expected.  # noqa:301 # Flake8 error?

    Returns:
        logging.Logger: Configured logger instance
    """
    loglevel = max(base_loglevel - (verbosity * 10), 10)
    logging.basicConfig(level=loglevel, format="%(message)s")
    return logging.getLogger()


def get_cli_input() -> Dict[str, Union[bool, str, int]]:
    """Reads cli inputs.

    Returns:
        Dict: cli paramters
    """
    cli = argparse.ArgumentParser()
    cli.add_argument(
        "--filename",
        type=str,
        default="serverless.yml",
        help="The filename to search for in discovery mode",
    )
    cli.add_argument(
        "-v",
        action="count",
        dest="verbosity",
        default=0,
        help="verbose output (repeat for increased verbosity)",
    )
    return vars(cli.parse_args())


def get_args() -> Dict[str, Union[str, int]]:
    """Reads enviroment parameters or sets default value.

    Returns:
        Tuple[str, str, str, str, int, str, str]: Type-casted values
    """
    return {
        "changes": os.environ.get("INPUT_CHANGES", ""),
        "stage": os.environ.get("INPUT_STAGE", ""),
        "profile": os.environ.get("INPUT_PROFILE", ""),
        "validator_path": os.environ.get("INPUT_VALIDATOR_PATH", ""),
        "postman_api_key": os.environ.get("INPUT_POSTMAN_API_KEY", ""),
        "globals_file": os.environ.get("INPUT_VALIDATOR_PATH", "globals.json"),
        "log_level": int(os.environ.get("INPUT_LOGLEVEL", 30)),
        "mode": os.environ.get("INPUT_MODE", ""),
        "aws_key": os.environ.get("INPUT_AWS_ACCESS_KEY_ID", ""),
        "aws_secret": os.environ.get("INPUT_AWS_SECRET_ACCESS_KEY", ""),
    }


def discover_file(paths: List[str], fname: str) -> List[str]:
    """Searches recursively for specific files in paths provided.

    Args:
        paths (List[str]): Paths to files/directories to search for file
        fname (str): Filename to search for

    Returns:
        List[str]: Paths to discovered files
    """
    files: List[str] = []
    for changed_file in paths:
        filepath = Path(changed_file).parts
        for i in range(len(filepath)):
            tmp_path = "/".join(filepath[:-i])
            if os.path.isfile(f"{tmp_path}/{fname}"):
                files.append(f"{tmp_path}/{fname}")
                break
    return list(set(files))


def set_output(output_name: str, output_value: str) -> None:
    """Sets output of GH actions.

    Args:
        output_name (str): name of the step output
        output_value (str): value of the step output
    """
    # See https://github.community/t5/GitHub-Actions/set-output-Truncates-Multiline-Strings/td-p/37870
    output_value = output_value.replace("\n", "%0A").replace("\r", "%0D")
    print(f"::set-output name={output_name}::{output_value}")


def output_endpoints(deployments: List[Deployment_Dict]) -> None:
    """Generates human-readible output.

    Args:
        deployments (List): Deployed lambda services
    """
    message: str = "The following services were deployed:\n"
    for deployment in deployments:
        message += f'Service name: `{deployment["service"]}`\n'
        message += f'stage: `{deployment["stage"]}`\n'
        message += "Endpoints:\n"
        a = ""
        assert isinstance(deployment["endpoints"], dict)
        for method, endpoints in deployment["endpoints"].items():
            a += "\n".join([f"{method} {x}" for x in endpoints])
        for x in a:
            message += x
        message += (
            "\nTo retrieve API keys run "
            + "`aws apigateway get-api-keys "
            + f'--name-query {deployment["stage"]}-{deployment["service"]} '
            + "--include-values`\n\n"
        )
    set_output(f"formatted", message)


def set_profile() -> None:
    """Sets up sls profile.

    Raises:
        subprocess.CalledProcessError: Raised if setting up the profile fails. # noqa: DAR402 # false positive
    """
    cmd = (
        f"sls config credentials --provider aws"
        + f" --key {os.environ.get('INPUT_AWS_KEY')}"
        + f" --secret {os.environ.get('INPUT_AWS_SECRET')}"
    )
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True  # noqa: S602
    )  # TODO: Sanitze inputs mark@ebot7.com
    output, error = process.communicate()
    return_code = process.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def validate():
    """Validates the sls definitions."""
    pass


def deploy(
    sls: List[str],
    inputs: Dict[str, Union[str, int]],
    args: Dict[str, Union[bool, str, int]],
) -> List[Deployment_Dict]:
    """Deploys the sls definitions."""
    log.info("Setting up sls profile")
    set_profile()
    deployments: List[Deployment_Dict] = []
    for service in sls:
        current_fn = Lambda(service)
        current_deployment = current_fn.Deployment(
            inputs["stage"], "eu-central-1", inputs["profile"]
        )
        log.info(f"Deploying service.")
        current_deployment.deploy()
        log.info(f"Deployment successful.")
        deployment: Deployment_Dict = {}
        assert current_deployment.stage
        assert current_fn.service
        deployment["endpoints"] = defaultdict(list)
        deployment["stage"] = current_deployment.stage
        deployment["service"] = current_fn.service
        stage = current_deployment.stage if current_deployment.stage else ""
        info = current_deployment.get_info()
        assert info
        urls = info[stage]["urls"]["byMethod"]
        assert isinstance(deployment["endpoints"], dict)
        for key, value in urls.items():
            deployment["endpoints"][key] += value
            log.info(f"Endpoint deployed:  {key} {value}")
        deployments.append(deployment)
    return deployments


def test(
    sls: List[str],
    inputs: Dict[str, Union[str, int]],
    args: Dict[str, Union[bool, str, int]],
) -> List[Deployment_Dict]:
    """Tests the sls definitions."""
    deployments: List[Deployment_Dict] = []
    for service in sls:
        current_fn = Lambda(service)
        current_deployment = current_fn.Deployment(
            inputs["stage"], "eu-central-1", inputs["profile"]
        )
        log.info(f"Testing service service.")
        print(
            current_deployment.test(
                inputs["postman_api_key"], inputs["globals_file"]
            )[0]
        )


if __name__ == "__main__":  # pragma: no cover
    args = get_cli_input()
    inputs = get_args()
    assert isinstance(args["verbosity"], int)  # noqa: 501 # mypy only
    log = setup_logging(args["verbosity"], inputs["log_level"])
    log.info("e-bot7 Serverless Helper")
    log.info("Setup")
    log.info(f"Current CWD: {os.getcwd()}")
    log.info(f"Current CWD content : {os.listdir(os.getcwd())}")

    log.info("The following args were passed:")
    for k, v in args.items():
        log.info(f"  {k}: {v}")

    changes_list = (
        inputs["changes"].split()
        if len(inputs["changes"].split()) > len(inputs["changes"].split(","))
        else inputs["changes"].split(",")
    )

    log.info("The following inputs were set:")
    log.info(
        f"  CHANGES: {len(changes_list)} files - {' '.join(changes_list)}"
    )
    log.info(f"  STAGE: {inputs['stage']}")
    log.info(f"  PROFILE: {inputs['profile']}")
    log.info(f"  VALIDATOR_PATH: {inputs['validator_path']}")

    assert isinstance(args["filename"], str)  # noqa: 501 # mypy only
    sls = discover_file(changes_list, args["filename"])
    sls = discover_file(changes_list, args["filename"])
    log.info(f"Discovered: {' '.join(sls)}")

    if inputs["mode"] == "validate":
        validate()
    elif inputs["mode"] == "deploy":
        deployments = deploy(sls, inputs, args)
        log.info(f"Setting outputs")
        output_endpoints(deployments)
    elif inputs["mode"] == "test":
        test(sls, inputs, args)
    else:
        raise ValueError("mode must be in validate, deploy or test")
