"""Test of the Lambda Class"""
import unittest
from eb7_sls_helper.src.sls_function import Lambda  # noqa: E402
from unittest.mock import patch


def mock_subprocess(*args, **kwargs):
    """Mock for subprocess.Popen calls."""

    class MockResponse(object):
        """Mock class for Popen"""

        def __init__(self, *args, **kwargs):
            self._output = b""
            valid_cmds = [
                "sls remove --config complete.yml --stage dev --profile default --region eu-central-1",
                "sls deploy --config complete.yml --stage dev --profile default --region eu-central-1",
            ]
            if any(x in valid_cmds for x in args):
                self._code = 0
            elif (
                "sls manifest --json --config complete.yml --stage dev --profile default --region eu-central-1"
                in args
            ):
                self._code = 0
                with open("manifest_output.json") as file:
                    self._output = file.read()
            else:
                self._code = 1

        def communicate(self):
            return (self._output, b"")

        def wait(self):
            return self._code

    return MockResponse(*args, **kwargs)


class DeploymentTestCase(unittest.TestCase):
    """Testing Deployment class."""

    def setUp(self):
        """Sets up base parameters."""
        self.definition = "eb7_sls_helper/test/complete.yml"
        self.stage = "dev"
        self.profile = "default"
        self.region = "eu-central-1"
        self.Lambda = Lambda(self.definition)
        self.Deployment = self.Lambda.Deployment(
            self.stage, self.region, self.profile
        )
        self.FailingDeployment = self.Lambda.Deployment(
            self.stage, "foo", "notexisting"
        )

    def test_custom_definition(self):
        """Asserts that definition is initialized."""
        self.assertEqual(self.Deployment.definition, self.definition)

    def test_from_definition(self):
        """Asserts that parsing values from sls file works."""
        a = self.Lambda.Deployment().from_definition()
        self.assertEqual(vars(self.Deployment), vars(a))

    def test_redefinition(self):
        """Asserts that deployments cannot be redefined."""
        with self.assertRaises(RuntimeError):
            self.Deployment.from_definition()

    def test_fallback_incomplete_definition(self):
        """Asserts fallback to default values."""
        a = (
            Lambda("eb7_sls_helper/test/defaults.yml")
            .Deployment()
            .from_definition()
        )
        self.assertEqual(a.stage, self.stage)
        self.assertEqual(a.region, self.region)

    def test_stage(self):
        """Asserts stage property is set correctly."""
        self.assertEqual(self.Deployment.stage, self.stage)

    def test_profile(self):
        """Asserts profile property is set correctly."""
        self.assertEqual(self.Deployment.profile, self.profile)

    def test_region(self):
        """Asiserts region property is set correctly."""
        self.assertEqual(self.Deployment.region, self.region)

    def test_str(self):
        """Asiserts human-readible output is correct."""
        output = str(
            {
                "definition": self.definition,
                "stage": self.stage,
                "region": self.region,
                "profile": self.profile,
            }
        )

        self.assertEqual(
            output, self.Deployment.__str__()  # noqa: WPS609 # Ok for testing
        )

    def test_info(self):
        """Asserts that info is intialized empty."""
        self.assertEqual(self.Deployment.get_info(), None)

    @patch("sls_function.subprocess.Popen", side_effect=mock_subprocess)
    def test_deploy(self, mock):
        """Asserts that deployment of service works."""
        self.Deployment.deploy()
        self.assertTrue(mock.called)
        self.assertTrue(len(mock.call_args_list) == 2)

    @patch("sls_function.subprocess.Popen", side_effect=mock_subprocess)
    def test_deploy_failing(self, mock):
        """Asserts that misspecified service raises RuntimeError."""
        with self.assertRaises(RuntimeError):
            self.FailingDeployment.deploy()

    @patch("sls_function.subprocess.Popen", side_effect=mock_subprocess)
    def test_remove(self, mock):
        """Asserts that removing service works."""
        self.Deployment.deploy()
        self.Deployment.remove()
        self.assertEqual(None, self.Deployment.get_info())
