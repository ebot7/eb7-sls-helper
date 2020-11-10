"""Test the tox output formatter.

PX-1086:
- Adds test that access tokens are not leaked when the output from subprocess is logged.
- The original string's access token was modified, so it's fine to commit it to repo.
"""
import unittest

from eb7_sls_helper.src.utils.tox_formatter import format_tox_output


class FormatterTestCase(unittest.TestCase):
    """Test cases for tox formatter."""

    def setUp(self):
        """Test setup."""
        with open("eb7_sls_helper/test/log_example.txt", "r") as fp:
            line = fp.readline()
            self.original_bytes = bytes(line, encoding="utf-8")

    def test_formatter_sanitizes(self):
        """Test sanitizer."""
        # This is not an actual token, don't fret ReviewDog.
        token_to_remove = "41f2c763acc948e99fe0188c7171b8176fd6c910"  # noqa: S105
        logged_output = format_tox_output(self.original_bytes)
        # Assert token is gone
        self.assertEqual(logged_output.find(token_to_remove), -1)
        # Assert we still have some testing info.
        self.assertIn("1 passed in 3.61s", logged_output)
