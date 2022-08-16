"""
Pytest fixtures
"""
from pathlib import Path

import pytest

from PIL import ImageFont

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
        self.application_path = Path(
            lotus.__file__
        ).parents[0].resolve()

        self.package_path = self.application_path.parent

        self.tests_dir = "tests"
        self.tests_path = self.package_path / self.tests_dir

        self.fixtures_dir = "data_fixtures"
        self.fixtures_path = self.tests_path / self.fixtures_dir

    def format(self, content):
        """
        Format given string to include some values related to this application.

        Arguments:
            content (str): Content string to format with possible values.

        Returns:
            str: Given string formatted with possible values.
        """
        return content.format(
            HOMEDIR=Path.home(),
            PACKAGE=str(self.package_path),
            APPLICATION=str(self.application_path),
            TESTS=str(self.tests_path),
            FIXTURES=str(self.fixtures_path),
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


@pytest.fixture(scope="function")
def enable_preview(settings):
    """
    Enable preview mode in given client session

    Example:
        You may use it in tests like this: ::

            def test_foo(client, enable_preview):
                enable_preview(client)
    """
    def _inner(current_client):
        session = current_client.session
        session[settings.LOTUS_PREVIEW_KEYWORD] = True
        session.save()

    return _inner


@pytest.fixture(scope="function")
def disable_preview(settings):
    """
    Enable preview mode in given client or request session

    Example:
        You may use it in tests like this: ::

            def test_foo(client, disable_preview):
                disable_preview(client)
    """
    def _inner(current_client):
        session = current_client.session
        session[settings.LOTUS_PREVIEW_KEYWORD] = False
        session.save()

    return _inner


@pytest.fixture(scope="module")
def font(tests_settings):
    """
    Return a PIL ImageFont using embedded TrueType font in data fixtures directory.

    Font will be loaded with hardcoded 12px font size.
    """
    return ImageFont.truetype(
        str(tests_settings.fixtures_path / "font" / "VeraMono.ttf"),
        12
    )
