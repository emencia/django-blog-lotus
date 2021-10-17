"""
Pytest fixtures
"""
import os
import pytest

import lotus


class FixturesSettingsTestMixin(object):
    """
    A mixin containing settings about application. This is almost about useful
    paths which may be used in tests.

    Attributes:
        application_path (str): Absolute path to the application directory.
        package_path (str): Absolute path to the package directory.
        tests_dir (str): Directory name which include tests.
        tests_path (str): Absolute path to the tests directory.
        fixtures_dir (str): Directory name which include tests datas.
        fixtures_path (str): Absolute path to the tests datas.
    """
    def __init__(self):
        # Base fixture datas directory
        self.application_path = os.path.abspath(
            os.path.dirname(lotus.__file__)
        )
        self.package_path = os.path.normpath(
            os.path.join(
                os.path.abspath(
                    os.path.dirname(lotus.__file__)
                ),
                "..",
            )
        )

        self.tests_dir = "tests"
        self.tests_path = os.path.join(
            self.package_path,
            self.tests_dir,
        )

        self.fixtures_dir = "data_fixtures"
        self.fixtures_path = os.path.join(
            self.tests_path,
            self.fixtures_dir
        )

    def format(self, content):
        """
        Format given string to include some values related to this application.

        Arguments:
            content (str): Content string to format with possible values.

        Returns:
            str: Given string formatted with possible values.
        """
        return content.format(
            HOMEDIR=os.path.expanduser("~"),
            PACKAGE=self.package_path,
            APPLICATION=self.application_path,
            TESTS=self.tests_path,
            FIXTURES=self.fixtures_path,
            VERSION=lotus.__version__,
        )


@pytest.fixture(scope="module")
def tests_settings():
    """
    Initialize and return settings for tests.

    Example:
        You may use it in tests like this: ::

            def test_foo(tests_settings):
                print(tests_settings.package_path)
                print(tests_settings.format("foo: {VERSION}"))
    """
    return FixturesSettingsTestMixin()
