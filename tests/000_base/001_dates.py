import datetime

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from django.utils import timezone


def test_crafting_datetime_timezone_aware():
    """
    How to make a datetime aware of a specific timezone using zoneinfo.
    """
    # Get a timezone, we use an almost exotic one from "Pacific/Chatham"
    sandbox_tz = ZoneInfo("Pacific/Chatham")

    # Make a date aware
    aware = datetime.datetime(2012, 10, 15, 10, 0).replace(tzinfo=sandbox_tz)

    assert str(aware) == "2012-10-15 10:00:00+13:45"


def test_django_timezone_now():
    """
    Django timezone.now return an aware timezone datetime but with dummy timezone
    (UTC).
    """
    django_now = timezone.now()
    # The dummy timzeone name is UTC
    assert str(django_now.tzinfo) == "UTC"

    # Get a timezone, we use an almost exotic one from "Pacific/Chatham"
    sandbox_tz = ZoneInfo("Pacific/Chatham")

    # Make the date aware
    aware = datetime.datetime(2012, 10, 15, 10, 0).replace(tzinfo=sandbox_tz)
    # Corresponding timezone name like the one we set on date
    assert str(aware.tzinfo) == "Pacific/Chatham"
