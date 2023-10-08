from freezegun import freeze_time

from django.urls import reverse

from lotus.choices import STATUS_DRAFT
from lotus.factories import ArticleFactory, AuthorFactory


@freeze_time("2012-10-15 10:00:00")
def test_author_viewset_list_payload(db, settings, api_client):
    """
    Author list item payload should contain fields as expected from its serializer.
    Also, this demonstrates than author are only listed if it is related to an article
    at least.
    """
    picsou = AuthorFactory(first_name="Picsou", last_name="McDuck")

    response = api_client.get(reverse("lotus-api:author-list"))
    assert response.status_code == 200

    json_data = response.json()
    assert json_data["count"] == 0

    # Relate author to an article
    ArticleFactory(title="article", fill_authors=[picsou])

    response = api_client.get(reverse("lotus-api:author-list"))
    assert response.status_code == 200

    json_data = response.json()
    # print()
    # print(json.dumps(json_data, indent=4))
    assert json_data["count"] == 1
    payload_item = json_data["results"][0]

    assert payload_item == {
        "url": "http://testserver/api/author/{}/".format(picsou.id),
        "detail_url": picsou.get_absolute_url(),
        "first_name": picsou.first_name,
        "last_name": picsou.last_name,
    }


def test_author_viewset_filtered(db, settings, api_client):
    """
    Viewset should returns content for required language by client and properly
    filter for publication criteria.

    This also demonstrate the way to ask for language in a request to Lotus API with
    the HTTP header 'Accept-Language'.
    """
    settings.LANGUAGE_CODE = "en"

    picsou = AuthorFactory(first_name="Picsou", last_name="McDuck", username="picsou")
    donald = AuthorFactory(first_name="Donald", last_name="Duck", username="donald")
    superdupont = AuthorFactory(
        first_name="Super",
        last_name="Dupont",
        username="superdupont"
    )
    bertand = AuthorFactory(
        first_name="Bertrand",
        last_name="Bertrand",
        username="bertandbertand"
    )
    AuthorFactory()

    # Relate authors to some articles
    ArticleFactory(
        title="beans",
        fill_authors=[picsou, donald]
    )
    ArticleFactory(
        title="baguette",
        language="fr",
        fill_authors=[superdupont]
    )
    ArticleFactory(
        title="privé",
        language="fr",
        private=True,
        fill_authors=[superdupont, bertand]
    )
    ArticleFactory(
        title="brouillon",
        status=STATUS_DRAFT,
        fill_authors=[superdupont, bertand]
    )

    url = reverse("lotus-api:author-list")

    # List result for default language (english) returns authors with english article
    response = api_client.get(url)
    assert response.status_code == 200
    json_data = response.json()
    assert [
        item["first_name"] + " " + item["last_name"]
        for item in json_data["results"]
    ] == ["Donald Duck", "Picsou McDuck"]
    assert len(json_data["results"]) == 2

    # List result for french language returns the author with a french article
    response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="fr")
    json_data = response.json()
    assert [
        item["first_name"] + " " + item["last_name"]
        for item in json_data["results"]
    ] == ["Super Dupont"]
    assert response.status_code == 200
    assert len(json_data["results"]) == 1

    # List result for deutsch language returns nothing since no deutsch article related
    # to an author
    response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="de")
    json_data = response.json()
    assert response.status_code == 200
    assert len(json_data["results"]) == 0
