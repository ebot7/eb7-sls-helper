"""Definition of sls function class"""
from __future__ import annotations
import subprocess  # noqa: S404 # Use of subprocess required
import os
import yaml
import json
from eb7_sls_helper.src import newman
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Union, Any

Manfifest = Dict[str, Any]  # type: ignore[type-arg, misc]


class SlsFunction(object):
    """SlsFunction class."""

    def __init__(self, definition: Optional[str] = None) -> None:
        """Constructor of SlsFunction

        Args:
            definition (str, optional): Path to serverless definition (e.g.
                "serverless.yml"). Defaults to None.
        """
        self._definition: Optional[str] = definition
        self._deployments: List[SlsFunction._Deployment] = []
        self._service: Optional[str] = None
        self._provider_name: Optional[str] = None
        self._runtime: Optional[str] = None
        if self._definition:
            self._parse_definition()

    def __str__(self) -> str:
        """Format print statements."""
        return str(
            {
                "definition": self._definition,
                "service": self._service,
                "provider_name": self._provider_name,
                "runtime": self._runtime,
            }
        )

    @property
    def definition(self) -> Optional[str]:
        """Definition getter

        Definitions can only be defined once i.e. not redefined.

        Returns:
            Optional[str]: Returns the path the serverless
                definition, if defined
        """
        return self._definition

    @definition.setter
    def definition(self, definition: str) -> None:
        if self._definition:
            raise RuntimeError("Cannot change definition after init")
        else:
            self._definition = definition
            self._parse_definition()

    @property
    def service(self) -> Optional[str]:
        """Service getter.

        Returns:
            Optional[str]: Returns the parsed service,
                if definition was provided
        """
        return self._service

    @property
    def provider_name(self) -> Optional[str]:
        """Provider getter.

        Returns:
            Optional[str]: Returns the parsed provider name,
                if definition was provided
        """
        return self._provider_name

    @property
    def runtime(self) -> Optional[str]:
        """Runtime getter.

        Returns:
            Optional[str]: Returns the parsed runtime,
                if definition was provided
        """
        return self._runtime

    def validate(self, Validator: object) -> None:  # noqa: N803 # obj to come
        """Validates definition."""
        # TODO mark@e-bot7.com will add
        return None

    def Deployment(  # noqa: N802 # dynamic ref to nested class
        self,
        stage: Optional[str] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> SlsFunction._Deployment:
        """Reference to internal _Deployment class.

        Either no values are provided or all args have to be provided.
        If no args are provided, values from definition can be parsed,
        after construction.

        Args:
            stage (str, optional): stage of deployment. Defaults to None.
            region (str, optional): region of deployment. Defaults to None.
            profile (str, optional): profile of deployment. Defaults to None.

        Returns:
            SlsFunction._Deployment: Deployment instance
        """
        assert self._definition is not None
        deployment = self._Deployment(
            self._definition, self, stage, region, profile
        )
        self._deployments.append(deployment)
        return deployment

    def _parse_definition(self) -> None:
        """Parses the sls definition

        Raises:
            ValueError: Raised if service, provider name or runtime are
                missing in definition file
        """
        assert self._definition is not None
        with open(self._definition) as file:
            document = yaml.safe_load(file)
        try:
            # Not-safe key access to check validity
            self._service = document["service"]
            self._provider_name = document["provider"]["name"]
            self._runtime = document["provider"]["runtime"]

        except KeyError:
            raise ValueError("Serverless definiton not valid")

    class _Deployment(object):  # noqa: WPS431 # Google Style allows nesting
        """_Deployment class."""

        defaults: Dict[str, str] = {
            "region": "eu-central-1",
            "profile": "default",
            "stage": "dev",
        }

        def __init__(
            self,
            definition: str,
            sls_function: SlsFunction,
            stage: Optional[str] = None,
            region: Optional[str] = None,
            profile: Optional[str] = None,
            newman_collection: Optional[str] = None,
            newman_environment: Optional[str] = None,
        ) -> None:  # noqa: RST301 # Looks like flake8 error
            """Deployment class.

            Args:
                definition (str): path to serverless definition.
                stage (str, optional): stage of deployment. Defaults to None.
                    Examples prod, dev, ...
                region (str, optional): region of deployment. Defaults to None.
                    Example "us-east-1"
                    See docs.aws.amazon.com/en_en/general/latest/gr/rande.html
                profile (str, optional): AWS profile. Defaults to None.
                    Local AWS profile name.
            """
            self._definition: str = definition
            self._sls_function: SlsFunction = sls_function
            self._region: Optional[str] = region
            self._stage: Optional[str] = stage
            self._profile: Optional[str] = profile
            self._newman_collection: Optional[str] = newman_collection
            self._newman_environment: Optional[str] = newman_environment
            self._manifest: Optional[Manfifest] = None

        def __str__(self) -> str:
            """Formats print."""
            return str(
                {
                    "definition": self._definition,
                    "stage": self._stage,
                    "region": self._region,
                    "profile": self._profile,
                }
            )

        @property
        def definition(self) -> str:
            """Definition getter.

            Returns:
                str: File path of serverless definition
            """
            return self._definition

        @property
        def stage(self) -> Optional[str]:
            """Stage getter.

            Returns:
                Optional[str]: Stage of deployment, if defined
            """
            return self._stage

        @property
        def region(self) -> Optional[str]:
            """Region getter.

            Returns:
                Optional[str]: Region of deployment, if defined
            """
            return self._region

        @property
        def profile(self) -> Optional[str]:
            """Profile getter.

            Returns:
                Optional[str]: Profile of deployment, if defined
            """
            return self._profile

        @property
        def newman_collection(self) -> Optional[str]:
            """Newman Collection getter.

            Returns:
                Optional[str]: Newman collection for testing, if defined
            """
            return self._newman_collection

        @property
        def newman_environment(self) -> Optional[str]:
            """Newman Environment getter.

            Returns:
                Optional[str]: Newman environment for testing , if defined
            """
            return self._newman_environment

        def from_definition(self) -> SlsFunction._Deployment:
            """Parses deploy information from serverless definition.

            Raises:
                RuntimeError: Raised if deploymment information already set

            Returns:
                SlsFunction._Deployment: Deployment instance
            """
            if any([self._profile, self._region, self._stage]):
                raise RuntimeError(
                    "Cannot redefine already defined deployment."
                )
            else:
                self._parse_definition()
            return self

        def get_info(self) -> Optional[Manfifest]:
            """Gets information of deployment.

            Returns:
                Optional[Dict[str, Any]]: Information as gathered by
                    serverless-manifast plugin, if available
            """
            return self._manifest

        def deploy(self) -> None:
            """Deploys the serverless function."""
            cmd, output, error, return_code = self._run_sls_command("deploy")
            self._read_manfifest()  # Update deployment after deploy

        def remove(self) -> None:
            """Removes the serverless function."""
            cmd, output, error, return_code = self._run_sls_command("remove")
            self._manifest = None

        def test(self, postman_api_key: str) -> Tuple[str, str, bytes, int]:
            """Runs integration tests for the function."""
            assert self.profile is not None
            key = newman.get_api_key(
                f"{self.stage}-{self._sls_function._service}", self.profile
            )
            assert self.newman_collection is not None
            return newman.execute_tests(
                self.newman_collection,
                self.newman_environment,
                postman_api_key,
                key,
            )

        def _read_manfifest(self) -> None:
            """Upldates information on the deployed serverless function."""
            cmd, output, error, return_code = self._run_sls_command(
                "manifest --json"
            )
            self._manifest = json.loads(output)

        def _parse_definition(self) -> None:
            with open(self._definition) as file:
                document = yaml.safe_load(file)
            keys = ["region", "profile", "stage"]
            for k in keys:
                if k in document["provider"]:
                    setattr(self, f"_{k}", document["provider"].get(k))
                else:
                    setattr(self, f"_{k}", self.defaults[k])
                    print(
                        f"{k} not defined in serverless.yml, "
                        + f"defaulting to {self.defaults[k]}"
                    )
            if "custom" in document:
                if "newmanCollection" in document.get("custom"):
                    self._newman_collection = document.get("custom").get(
                        "newmanCollection"
                    )
                if "newmanEnvironment" in document.get("custom"):
                    self._newman_environment = (
                        document.get("custom")
                        .get("newmanEnvironment")
                        .get(self._stage)
                    )

        def _run_sls_command(
            self, operation: str
        ) -> Tuple[str, bytes, bytes, int]:
            """Executes sls command in subprocess.

            Args:
                operation (str): The sls command to execute.
                    See https://serverless.com/framework/docs/providers/aws/

            Raises:
                RuntimeError: Raised if serverless command execution failed.

            Returns:
                Tuple[str, bytes, bytes, int]: The command, stdout, stderr,
                    and return code
            """
            cwd = os.getcwd()
            parent = Path(self._definition).parent
            filename = Path(self._definition).name
            os.chdir(parent)
            try:
                cmd = (
                    f"sls {operation} --config {filename} "
                    + f"--stage {self._stage} "
                    + f"--profile {self._profile} --region {self._region}"
                )
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, shell=True  # noqa: S602
                )  # TODO: Input santization for sec reasons  mark@e-bot7.com
                output, error = process.communicate()
                return_code = process.wait()
                if return_code:
                    raise subprocess.CalledProcessError(return_code, cmd)
            except subprocess.CalledProcessError:
                print(output)
                print(error)
                raise RuntimeError(f"Execution of {cmd} failed")
            finally:
                os.chdir(cwd)
            return cmd, output, error, return_code


class Lambda(SlsFunction):
    """Lambda class."""

    pass  # noqa: WPS420,WPS604 # Inheritence already used without functionality change


class StateMachine(SlsFunction):
    """StateMachine class."""

    pass  # noqa: WPS420,WPS604 # Inheritence already used without functionality change
