"""Test of the GH Action Interface"""
import unittest
from eb7_sls_helper.src import gh_action_interface
from unittest.mock import patch
import os


def mock_subprocess(*args, **kwargs):
    """Mock for subprocess.Popen calls."""

    class MockResponse(object):
        """Mock class for Popen"""

        def __init__(self, *args, **kwargs):
            self._output = b""
            config = (
                "sls config credentials --provider aws"
                + f" --key {os.environ.get('INPUT_AWS_KEY')}"
                + f" --secret {os.environ.get('INPUT_AWS_SECRET')}"
            )
            valid_cmds = [
                config,
            ]
            if any(x in valid_cmds for x in args):
                self._code = 0
            else:
                self._code = 1

        def communicate(self):
            return (self._output, b"")

        def wait(self):
            return self._code

    return MockResponse(*args, **kwargs)


class DeploymentTestCase(unittest.TestCase):
    def setUp(self):
        self.definition = "test/complete.yml"
        self.stage = "dev"
        self.profile = "default"
        self.region = "eu-central-1"

    @patch("builtins.print")
    def test_set_gh_output(self, mock):
        gh_action_interface.set_output("key", "value")
        mock.assert_called_once()
        mock.assert_called_once_with("::set-output name=key::value")

    @patch("builtins.print")
    def test_set_gh_output_multiline(self, mock):
        gh_action_interface.set_output("key", "value\n\rvalue")
        mock.assert_called_once_with("::set-output name=key::value%0A%0Dvalue")

    @patch("eb7_sls_helper.src.gh_action_interface.set_output")
    def test_output_endpoints(self, mock):
        deployments = [
            {
                "service": "test",
                "stage": "dev",
                "endpoints": {
                    "GET": ["www.url.com/a", "www.url.com/b"],
                    "POST": ["www.url.com/c"],
                },
            }
        ]
        gh_action_interface.output_endpoints(deployments)
        deployment = deployments[0]
        test_string = (
            "The following services were deployed:\n"
            + f'Service name: `{deployment["service"]}`\n'
            + f'stage: `{deployment["stage"]}`\n'
            + "Endpoints:\n"
            + "GET www.url.com/a\n\nGET www.url.com/bPOST www.url.com/c"
            + "\nTo retrieve API keys run "
            + "`aws apigateway get-api-keys "
            + f'--name-query {deployment["stage"]}-{deployment["service"]} '
            + "--include-values`\n\n"
        )
        mock.assert_called_once_with("formatted", test_string)

    @patch("subprocess.Popen", side_effect=mock_subprocess)
    def test_setup(self, mock):
        os.environ["INPUT_AWS_KEY"] = "KEY"
        os.environ["INPUT_AWS_SECRET"] = "SECRET"
        gh_action_interface.set_profile()
