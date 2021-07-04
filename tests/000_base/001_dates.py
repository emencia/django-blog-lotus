import datetime

import pytz

from django.utils import timezone


def test_crafting_datetime_timezone_aware():
    """
    How to make a datetime aware of a specific timezone using pytz.
    """
    # Get a timezone, we use an almost exotic one from "Pacific/Chatham"
    sandbox_tz = pytz.timezone("Pacific/Chatham")

    # Make a date aware
    aware = sandbox_tz.localize(
        datetime.datetime(2012, 10, 15, 10, 0)
    )

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
    sandbox_tz = pytz.timezone("Pacific/Chatham")

    # Make the date aware
    aware = sandbox_tz.localize(
        datetime.datetime(2012, 10, 15, 10, 0)
    )
    # Corresponding timezone name like the one we set on date
    assert str(aware.tzinfo) == "Pacific/Chatham"
