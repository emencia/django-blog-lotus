import datetime

import pytest
import pytz
from freezegun import freeze_time

from django.template import Context, Template
from django.utils import timezone

from lotus.choices import STATUS_DRAFT
from lotus.factories import (
    ArticleFactory,
)


def test_tag_article_state_list_basic(db):
    """
    Basic usage without context ``lotus_now`` variable on a simple available article
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

    assert rendered == "available"


def test_tag_article_state_list_mixed(db):
    """
    Usage with context ``lotus_now`` variable on an article with some options should
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

    assert rendered == "pinned,private,available,passed"


def test_tag_article_state_list_prefixed(db):
    """
    Usage with context ``lotus_now`` variable on an article with some options should
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

    assert rendered == "foo-pinned,foo-private,foo-available,foo-passed"


def test_tag_article_states_mixed(db):
    """
    Usage with context ``lotus_now`` variable on an article with some options should
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

    assert rendered == "pinned private available passed"


def test_tag_article_states_prefixed(db):
    """
    Usage with context ``lotus_now`` variable on an article with some options should
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

    assert rendered == "foo-pinned foo-private foo-available foo-passed"
