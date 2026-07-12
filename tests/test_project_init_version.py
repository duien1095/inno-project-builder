import unittest
from project_init import __version__


class VersionTests(unittest.TestCase):
    def test_version_is_semantic(self) -> None:
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+(-[A-Za-z0-9.+-]+)?$")


if __name__ == "__main__":
    unittest.main()
