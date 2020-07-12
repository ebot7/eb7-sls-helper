"""Integration testing."""
import boto3
import json
import subprocess  # noqa: S404 # Use of subprocess required
from typing import Tuple


def get_api_key(name: str, profile: str) -> str:
    """Get API Gateway API key"""
    session = boto3.Session(profile_name=profile)
    client = session.client("apigateway")
    response = client.get_api_keys(nameQuery=name, includeValues=True)
    return response["items"][0]["value"]


def execute_tests(
    collection: str, environment, postman_api_key: str, endpoint_key: str
) -> Tuple[str, str, bytes, int]:
    """Execute newman test"""
    cmd = (
        f"newman run {collection}"
        + f" --postman-api-key {postman_api_key}"
        + f" --environment {environment}"
        + f' --global-var "key={endpoint_key}"'
    )
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True  # noqa: S602
    )  # TODO: Input santization for sec reasons  mark@e-bot7.com
    output, error = process.communicate()
    return_code = process.wait()
    return cmd, output.decode("utf-8"), error, return_code
