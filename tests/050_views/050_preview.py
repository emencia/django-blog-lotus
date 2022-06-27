from django.urls import reverse

from lotus.factories import AuthorFactory


def test_preview_toggler_anonymous(db, client):
    """
    Anonymous should not be allowed.
    """
    disable_url = reverse("lotus:preview-disable")
    enable_url = reverse("lotus:preview-enable")

    response = client.get(disable_url)
    assert response.status_code == 401

    response = client.get(enable_url)
    assert response.status_code == 401


def test_preview_toggler(db, client):
    """
    Lambda user should not be allowed
    """
    user = AuthorFactory(username="donald")
    client.force_login(user)

    disable_url = reverse("lotus:preview-disable")
    enable_url = reverse("lotus:preview-enable")

    response = client.get(disable_url)
    assert response.status_code == 403

    response = client.get(enable_url)
    assert response.status_code == 403


def test_preview_toggler_bad_operations(db, client):
    """
    Toggler view require a valid redirection URL else it should return a bad operation
    response.
    """
    admin = AuthorFactory(username="picsou", flag_is_admin=True)
    client.force_login(admin)

    disable_url = reverse("lotus:preview-disable")
    enable_url = reverse("lotus:preview-enable")

    # URL argument 'next' is required
    response = client.get(disable_url)
    assert response.status_code == 400

    # URL redirection can not be relative
    response = client.get(disable_url, {"next": "foo"})
    assert response.status_code == 400

    # URL redirection can not be a toggler view URL
    response = client.get(disable_url, {"next": enable_url})
    assert response.status_code == 400


def test_preview_toggler_toggle(db, settings, client):
    """
    Toggler should switch mode value in session as required by view 'mode' attribute.
    """
    admin = AuthorFactory(username="picsou", flag_is_admin=True)
    client.force_login(admin)

    lotus_home = reverse("lotus:article-index")
    disable_url = reverse("lotus:preview-disable")
    enable_url = reverse("lotus:preview-enable")

    # On default there is no preview mode in session
    assert client.session.get(settings.LOTUS_PREVIEW_KEYWORD) is None

    # Disable preview
    response = client.get(disable_url, {"next": lotus_home}, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [
        (lotus_home, 302)
    ]
    assert client.session.get(settings.LOTUS_PREVIEW_KEYWORD) is False

    # Disable preview
    response = client.get(enable_url, {"next": lotus_home}, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [
        (lotus_home, 302)
    ]
    assert client.session.get(settings.LOTUS_PREVIEW_KEYWORD) is True
