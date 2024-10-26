import pytest
from freezegun import freeze_time

from django.urls import reverse

from lotus.factories import CategoryFactory, multilingual_category

try:
    import rest_framework  # noqa: F401
except ModuleNotFoundError:
    API_AVAILABLE = False
else:
    API_AVAILABLE = True


pytestmark = pytest.mark.skipif(
    not API_AVAILABLE,
    reason="Django REST is not available, API is disabled"
)


@freeze_time("2012-10-15 10:00:00")
def test_category_viewset_list_payload(db, settings, api_client):
    """
    Category list item payload should contain fields as expected from its serializer.
    """
    category = CategoryFactory(title="cat_1")

    response = api_client.get(reverse("lotus-api:category-list"))
    assert response.status_code == 200

    json_data = response.json()
    # print()
    # print(json.dumps(json_data, indent=4))
    assert json_data["count"] == 1
    payload_item = json_data["results"][0]

    assert payload_item == {
        "url": "http://testserver/api/category/{}/".format(category.id),
        "detail_url": category.get_absolute_url(),
        "language": category.language,
        "title": category.title,
        "lead": category.lead,
        "cover": "http://testserver" + category.cover.url,
        "description": category.description,
    }


@freeze_time("2012-10-15 10:00:00")
def test_category_viewset_list_order(db, settings, api_client):
    """
    Category list should be ordered on common front order for flat list.
    """
    pong = CategoryFactory(title="Pong", slug="pong")
    ang = CategoryFactory(title="Ang", slug="ang")
    ping = CategoryFactory(title="Ping", slug="ping")
    # Make a tree of categories such as Ping > Pong
    pong.move_into(ping)

    response = api_client.get(reverse("lotus-api:category-list"))
    assert response.status_code == 200

    json_data = response.json()
    assert json_data["count"] == 3

    assert [item["title"] for item in json_data["results"]] == [
        ang.title,
        ping.title,
        pong.title,
    ]


@pytest.mark.parametrize("allow", [True, False])
def test_category_viewset_language(db, settings, api_client, allow):
    """
    Viewset should returns content for required language by client.

    The setting 'LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE' does never change this
    behavior.

    This also demonstrate the way to ask for language in a request to Lotus API with
    the HTTP header 'Accept-Language'.
    """
    settings.LANGUAGE_CODE = "en"
    settings.LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE = allow

    CategoryFactory(title="beans", language="en")
    CategoryFactory(title="fish and chips", language="en")
    CategoryFactory(title="baguette", language="fr")
    multilingual_category(
        title="Cheese",
        langs=["fr", "de"],
        contents={
            "fr": {
                "title": "Fromage",
            },
            "de": {
                "title": "Käse",
            }
        },
    )

    url = reverse("lotus-api:category-list")

    # List result for default language (english)
    response = api_client.get(url)
    assert response.status_code == 200
    json_data = response.json()
    # print()
    # print(json.dumps(json_data, indent=4))
    assert len(json_data["results"]) == 3
    assert len([
        category
        for category in json_data["results"]
        if category["language"] == "en"
    ]) == 3

    # List result for french language returns only french category
    response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="fr")
    json_data = response.json()
    assert response.status_code == 200
    assert len(json_data["results"]) == 2
    assert len([
        category
        for category in json_data["results"]
        if category["language"] == "fr"
    ]) == 2

    # List result for deutsch language returns only deutsch category
    response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="de")
    json_data = response.json()
    assert response.status_code == 200
    assert len(json_data["results"]) == 1
    assert len([
        category
        for category in json_data["results"]
        if category["language"] == "de"
    ]) == 1


def test_category_viewset_allow_language_safe_enabled(db, settings, api_client):
    """
    When setting 'LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE' is enabled the detail won't
    filter on current client language, an object in different language can be reached.
    """
    settings.LANGUAGE_CODE = "en"
    settings.LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE = True

    egg = CategoryFactory(title="egg", language="en")
    oeuf = CategoryFactory(title="oeuf", language="fr")

    # English category is reachable with english language
    response = api_client.get(egg.get_absolute_api_url(), HTTP_ACCEPT_LANGUAGE="en")
    assert response.status_code == 200

    # French category is still reachable with english language
    response = api_client.get(oeuf.get_absolute_api_url(), HTTP_ACCEPT_LANGUAGE="en")
    assert response.status_code == 200


def test_category_viewset_allow_language_safe_disabled(db, settings, api_client):
    """
    When setting 'LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE' is disabled the detail will
    filter on current client language, an object in different language can not be
    reached.
    """
    settings.LANGUAGE_CODE = "en"
    settings.LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE = False

    egg = CategoryFactory(title="egg", language="en")
    oeuf = CategoryFactory(title="oeuf", language="fr")

    # English category is reachable with english language
    response = api_client.get(egg.get_absolute_api_url(), HTTP_ACCEPT_LANGUAGE="en")
    assert response.status_code == 200

    # French category is still reachable with english language
    response = api_client.get(oeuf.get_absolute_api_url(), HTTP_ACCEPT_LANGUAGE="en")
    assert response.status_code == 404
