"""Integration testing."""
import boto3
import json
import subprocess  # noqa: S404 # Use of subprocess required


def get_api_key(name: str, profile: str) -> str:
    """Get API Gateway API key"""
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("apigateway").setLevel(logging.CRITICAL)
    session = boto3.Session(profile_name=profile)
    client = session.client("apigateway")
    response = client.get_api_keys(nameQuery=name, includeValues=True)
    return response["items"][0]["value"]


def execute_tests(
    collection: str, postman_api_key: str, globals_file: str, endpoint_key: str
):
    """Execute newman test"""
    cmd = (
        f"newman run {collection}"
        + f" --postman-api-key {postman_api_key}"
        + f" -g {globals_file}"
        + f' --global-var "key={endpoint_key}"'
    )
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True  # noqa: S602
    )  # TODO: Input santization for sec reasons  mark@e-bot7.com
    output, error = process.communicate()
    return_code = process.wait()
    return cmd, output, error, return_code
