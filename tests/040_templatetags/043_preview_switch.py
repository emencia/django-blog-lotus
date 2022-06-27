from django.template import RequestContext, Template
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware

from lotus.factories import AuthorFactory
from lotus.utils.tests import html_pyquery


def test_tag_preview_switch_anonymous(rf):
    """
    Empty content should always be returned for anonymous.
    """
    request = rf.get("/")
    template = Template(
        "{% load lotus %}{% preview_switch %}"
    )

    rendered = template.render(
        RequestContext(request, {})
    )

    assert rendered.strip() == ""


def test_tag_preview_switch_non_staff(rf, db):
    """
    Empty content should always be returned for non staff user.
    """
    user = AuthorFactory(username="picsou")

    request = rf.get("/")
    request.user = user

    template = Template(
        "{% load lotus %}{% preview_switch %}"
    )

    rendered = template.render(
        RequestContext(request, {})
    )

    assert rendered.strip() == ""


def test_tag_preview_switch_staff(rf, db, enable_preview):
    """
    Toggle link should be returned to staff user. It should be the link to enable if
    preview is not enabled, else the link to disable preview.
    """
    user = AuthorFactory(username="picsou", flag_is_admin=True)

    request = rf.get("/foo/")
    request.user = user

    # Append expected session object to the request since the factory avoid it
    middleware = SessionMiddleware(request)
    middleware.process_request(request)
    request.session.save()

    template = Template(
        "{% load lotus %}{% preview_switch %}"
    )

    disable_url = reverse("lotus:preview-disable")
    enable_url = reverse("lotus:preview-enable")

    # With disabled preview
    rendered = template.render(
        RequestContext(request, {})
    )
    dom = html_pyquery(rendered)
    link = dom.find("a")[0]
    assert link.text.strip() == "Enable preview"
    assert link.get("href") == "{}?next=/foo/".format(enable_url)

    # With enabled preview
    enable_preview(request)
    rendered = template.render(
        RequestContext(request, {})
    )
    dom = html_pyquery(rendered)
    link = dom.find("a")[0]
    assert link.text.strip() == "Disable preview"
    assert link.get("href") == "{}?next=/foo/".format(disable_url)
