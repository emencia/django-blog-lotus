"""
Since ``Django 3.8``, ZoneInfo is the preferred way to localize date and play with
timezone instead of Pytz.

This module should safely load ``zoneinfo`` library to import ``ZoneInfo`` class
for ``Django>=3.8``.
"""
try:
    from zoneinfo import ZoneInfo  # noqa: F401,F403
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo  # noqa: F401,F403
