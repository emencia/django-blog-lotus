import datetime

import pytz

from django.conf import settings
from django.template import Context, Template

from lotus.factories import ArticleFactory


# Shortcut for a shorter variable name
STATES = settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES


def test_tag_article_state_list_basic(db):
    """
    Basic usage without context variable ``lotus_now`` on a simple available article
    without any options should just return the "available" state.
    """
    article_object = ArticleFactory(title="dummy")

    template = Template(
        "{% load lotus %}{% article_state_list article_object as states %}"
        "{{ states|join:',' }}"
    )

    context = Context({
        "article_object": article_object,
    })
    rendered = template.render(context)

    assert rendered == STATES["status_available"]


def test_tag_article_state_list_mixed(db):
    """
    Usage with context variable ``lotus_now`` on an article with some options should
    return all the right states.
    """
    # Date references
    default_tz = pytz.timezone("UTC")
    now = default_tz.localize(datetime.datetime(2012, 10, 15, 10, 00))
    today = default_tz.localize(datetime.datetime(2012, 10, 15, 1, 00))
    past_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 00))

    article_object = ArticleFactory(
        title="pinned, private and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        pinned=True,
        private=True,
    )

    template = Template(
        "{% load lotus %}{% article_state_list article_object as states %}"
        "{{ states|join:',' }}"
    )

    context = Context({
        "lotus_now": now,
        "article_object": article_object,
    })
    rendered = template.render(context)

    assert rendered == ",".join([
        STATES["pinned"],
        STATES["private"],
        STATES["status_available"],
        STATES["publish_end_passed"],
    ])


def test_tag_article_state_list_prefixed(db):
    """
    Usage with context variable ``lotus_now`` on an article with some options should
    return all the right states prefixed.
    """
    # Date references
    default_tz = pytz.timezone("UTC")
    now = default_tz.localize(datetime.datetime(2012, 10, 15, 10, 00))
    today = default_tz.localize(datetime.datetime(2012, 10, 15, 1, 00))
    past_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 00))

    article_object = ArticleFactory(
        title="pinned, private and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        pinned=True,
        private=True,
    )

    template = Template(
        "{% load lotus %}"
        "{% article_state_list article_object prefix='foo-' as states %}"
        "{{ states|join:',' }}"
    )

    context = Context({
        "lotus_now": now,
        "article_object": article_object,
    })
    rendered = template.render(context)

    assert rendered == ",".join([
        "foo-" + STATES["pinned"],
        "foo-" + STATES["private"],
        "foo-" + STATES["status_available"],
        "foo-" + STATES["publish_end_passed"],
    ])


def test_tag_article_states_mixed(db):
    """
    Usage with context variable ``lotus_now`` on an article with some options should
    return all the right states.
    """
    # Date references
    default_tz = pytz.timezone("UTC")
    now = default_tz.localize(datetime.datetime(2012, 10, 15, 10, 00))
    today = default_tz.localize(datetime.datetime(2012, 10, 15, 1, 00))
    past_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 00))

    article_object = ArticleFactory(
        title="pinned, private and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        pinned=True,
        private=True,
    )

    template = Template(
        "{% load lotus %}{% article_states article_object %}"
    )

    context = Context({
        "lotus_now": now,
        "article_object": article_object,
    })
    rendered = template.render(context)

    assert rendered == " ".join([
        STATES["pinned"],
        STATES["private"],
        STATES["status_available"],
        STATES["publish_end_passed"],
    ])


def test_tag_article_states_prefixed(db):
    """
    Usage with context variable ``lotus_now`` on an article with some options should
    return all the right states prefixed.
    """
    # Date references
    default_tz = pytz.timezone("UTC")
    now = default_tz.localize(datetime.datetime(2012, 10, 15, 10, 00))
    today = default_tz.localize(datetime.datetime(2012, 10, 15, 1, 00))
    past_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 00))

    article_object = ArticleFactory(
        title="pinned, private and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        pinned=True,
        private=True,
    )

    template = Template(
        "{% load lotus %}{% article_states article_object prefix='foo-' %}"
    )

    context = Context({
        "lotus_now": now,
        "article_object": article_object,
    })
    rendered = template.render(context)

    assert rendered == " ".join([
        "foo-" + STATES["pinned"],
        "foo-" + STATES["private"],
        "foo-" + STATES["status_available"],
        "foo-" + STATES["publish_end_passed"],
    ])
