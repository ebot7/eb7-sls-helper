"""Test of the Lambda Class"""
import unittest
from eb7_sls_helper.src.sls_function import Lambda  # noqa: E402


class LambdaTestCase(unittest.TestCase):
    """Testing the Lambda objecti."""

    def setUp(self):
        """Setting test values."""
        self.definition = "eb7_sls_helper/test/complete.yml"
        self.service = "eb7-sls-helper"
        self.runtime = "python2.7"
        self.provider_name = "aws"
        self.Lambda = Lambda(self.definition)

    def test_custom_definition(self):
        """Asserts that the init of the object works."""
        self.assertEqual(self.Lambda.definition, self.definition)

    def test_definition_after_init(self):
        """Asserts that definition of params with empty init works."""
        a = Lambda()
        a.definition = self.definition
        self.assertEqual(vars(self.Lambda), vars(a))

    def test_redefinition(self):
        """Assertst that the Lambda object can only be defined once."""
        with self.assertRaises(RuntimeError):
            self.Lambda.definition = "new.yml"

    def test_service(self):
        """Asserts that the service property works as intended."""
        self.assertEqual(self.Lambda.service, self.service)

    def test_provider_name(self):
        """Asserts that the provider_name property works as intended."""
        self.assertEqual(self.Lambda.provider_name, self.provider_name)

    def test_runtime(self):
        """Asserts that the runtime property works as intended."""
        self.assertEqual(self.Lambda.runtime, self.runtime)

    def test_invalid_definition(self):
        """Asserts that incomplete sls definitions raise errors."""
        with self.assertRaises(ValueError):
            Lambda("eb7_sls_helper/test/incomplete.yml")

    def test_str(self):
        """Asserts that string representation works."""
        output = str(
            {
                "definition": "eb7_sls_helper/test/complete.yml",
                "service": "eb7-sls-helper",
                "provider_name": "aws",
                "runtime": "python2.7",
            }
        )
        self.assertEqual(output, self.Lambda.__str__())  # noqa: WPS609
