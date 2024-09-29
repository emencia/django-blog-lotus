import datetime

from freezegun import freeze_time

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from django.urls import reverse

from lotus.choices import STATUS_DRAFT
from lotus.factories import multilingual_article, ArticleFactory, CategoryFactory
from lotus.models import Article
from lotus.utils.tests import (
    html_pyquery, get_admin_add_url, get_admin_change_url, get_admin_list_url,
)


def test_article_admin_add(db, admin_client):
    """
    Article model admin add form view should not raise error on GET request.
    """
    url = get_admin_add_url(Article)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_article_admin_list(db, admin_client):
    """
    Article model admin list view should not raise error on GET request.
    """
    url = get_admin_list_url(Article)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_article_admin_detail(db, admin_client):
    """
    Article model admin detail view should not raise error on GET request.
    """
    obj = ArticleFactory()

    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200


@freeze_time("2012-10-15 10:00:00")
def test_article_admin_list_is_published(db, admin_client):
    """
    Article model admin list view should have the right content for item column
    "is_published" depending item is published or not (following publication criterias)
    and 'PublicationFilter' should correctly filter list items on published/unpublished
    criterias.
    """
    # Date references
    utc = ZoneInfo("UTC")
    today = datetime.datetime(2012, 10, 15, 1, 00).replace(tzinfo=utc)
    past_hour = datetime.datetime(2012, 10, 15, 9, 00).replace(tzinfo=utc)
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    draft = ArticleFactory(
        title="draft",
        publish_date=today.date(),
        publish_time=today.time(),
        status=STATUS_DRAFT,
    )
    basic = ArticleFactory(
        title="basic published",
        publish_date=today.date(),
        publish_time=today.time(),
    )
    published_private = ArticleFactory(
        title="published but private",
        publish_date=today.date(),
        publish_time=today.time(),
        private=True,
    )
    published_notyet = ArticleFactory(
        title="not yet published",
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    published_passed = ArticleFactory(
        title="published but ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
    )
    published_private_passed = ArticleFactory(
        title="published, private and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        private=True,
    )
    draft_passed = ArticleFactory(
        title="draft and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        status=STATUS_DRAFT,
    )

    # Collect published and not published id apart
    expected_published_ids = [basic.id, published_private.id]
    expected_unpublished_ids = [
        draft.id,
        published_notyet.id,
        published_passed.id,
        published_private_passed.id,
        draft_passed.id,
    ]

    # Get default list view response
    url = get_admin_list_url(Article)
    response = admin_client.get(url)
    assert response.status_code == 200

    # Parse table rows to get article ids and publication state
    resulting_published_ids = []
    resulting_unpublished_ids = []
    dom = html_pyquery(response)
    for row in dom.find("#result_list tbody tr"):
        article_id = row.cssselect(
            "td.action-checkbox input.action-select"
        )[0].get("value")
        article_published = row.cssselect("td.field-is_published img")[0].get("alt")
        if article_published == "True":
            resulting_published_ids.append(int(article_id))
        else:
            resulting_unpublished_ids.append(int(article_id))

    assert sorted(resulting_published_ids) == sorted(expected_published_ids)
    assert sorted(resulting_unpublished_ids) == sorted(expected_unpublished_ids)

    # Get list view filter on published items
    url = get_admin_list_url(Article)
    response = admin_client.get(url, {"is_published": "true"})
    assert response.status_code == 200

    dom = html_pyquery(response)
    items = dom.find("#result_list tbody tr")
    assert len(items) == len(expected_published_ids)
    resulting_published_ids = []
    for row in dom.find("#result_list tbody tr"):
        article_id = row.cssselect(
            "td.action-checkbox input.action-select"
        )[0].get("value")
        article_published = row.cssselect("td.field-is_published img")[0].get("alt")
        if article_published == "True":
            resulting_published_ids.append(int(article_id))

    assert sorted(resulting_published_ids) == sorted(expected_published_ids)

    # Get list view filter on unpublished items
    url = get_admin_list_url(Article)
    response = admin_client.get(url, {"is_published": "false"})
    assert response.status_code == 200

    dom = html_pyquery(response)
    items = dom.find("#result_list tbody tr")
    assert len(items) == len(expected_unpublished_ids)
    resulting_unpublished_ids = []
    for row in dom.find("#result_list tbody tr"):
        article_id = row.cssselect(
            "td.action-checkbox input.action-select"
        )[0].get("value")
        article_published = row.cssselect("td.field-is_published img")[0].get("alt")
        if article_published == "False":
            resulting_unpublished_ids.append(int(article_id))

    assert sorted(resulting_unpublished_ids) == sorted(expected_unpublished_ids)


def test_article_admin_original_choices(db, admin_client):
    """
    Choices should be limited to some constraints:

    * 'original' field should not list items in same language, not the
      article itself and only original articles;
    * 'related' field should not list items in different language and not the
      article itself;
    * 'categories' field should not list items in different language;
    """
    # Create new object to check
    obj = ArticleFactory(language="en")
    # Create new object as a translation
    ArticleFactory(language="fr", original=obj)

    # Create some objects in same language
    fillers_en = [
        ArticleFactory(language="en"),
        ArticleFactory(language="en"),
    ]
    # Create some other objects in various other languages, these are the only
    # elligible articles for original field choices
    fillers_langs = [
        ArticleFactory(language="fr"),
        ArticleFactory(language="fr"),
        ArticleFactory(language="de"),
    ]
    # Create some categories
    cat_en = CategoryFactory(language="en")
    CategoryFactory(language="fr")

    # Get the obj detail page
    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200

    dom = html_pyquery(response)

    # Get available 'original' choice ids from their values
    options = dom.find("#id_original option")
    option_ids = [int(item.get("value")) for item in options if item.get("value")]

    assert sorted(option_ids) == sorted([item.id for item in fillers_langs])

    # Get available 'related' choice ids from their values
    options = dom.find("#id_related option")
    option_ids = [int(item.get("value")) for item in options if item.get("value")]

    assert sorted(option_ids) == sorted([item.id for item in fillers_en])

    # Get available 'categories' choice ids from their values
    options = dom.find("#id_categories option")
    option_ids = [cat_en.id]


def test_article_admin_translate_button_empty(db, admin_client):
    """
    Translate button should not be in detail if there is no available language for
    translation and finally the translate page should not contain form since there is
    language available.
    """
    ping = CategoryFactory(slug="ping")

    # Create cheese articles with published FR and DE translations
    created_cheese = multilingual_article(
        title="Cheese",
        slug="cheese",
        langs=["fr", "de"],
        fill_categories=[ping],
        contents={
            "fr": {
                "title": "Fromage",
                "slug": "fromage",
                "fill_categories": [ping],
            },
            "de": {
                "title": "Käse",
                "slug": "kase",
                "fill_categories": [ping],
            }
        },
    )

    # No translate button expected since all possible languages have been used
    url = get_admin_change_url(created_cheese["original"])
    response = admin_client.get(url)
    assert response.status_code == 200

    dom = html_pyquery(response)
    links = dom.find(".lotus-translate-link")
    assert len(links) == 0

    # Expected existing translation languages (without the original language)
    existings = dom.find(".lotus-siblings-resume a")
    assert len(existings) == 2

    existing_languages = [item.get("data-lotus-langcode") for item in existings]
    assert sorted(existing_languages) == ["de", "fr"]

    # No form expected since there is no available languages
    url = reverse(
        "admin:lotus_article_translate_original",
        args=(created_cheese["original"].id,),
    )
    response = admin_client.get(url)
    assert response.status_code == 200

    dom = html_pyquery(response)
    forms = dom.find("#lotus-translate-original-form")
    assert len(forms) == 0


def test_article_admin_translate_button_expected(db, admin_client):
    """
    Translate button should be in detail page with the right URL and lead to the
    "Translate" form with the right available languages.
    """
    ping = CategoryFactory(slug="ping")

    # Create meat articles with unpublished DE translation
    created_beef = multilingual_article(
        title="Beef",
        slug="beef",
        langs=["de"],
        fill_categories=[ping],
        contents={
            "de": {
                "title": "Rindfleisch",
                "slug": "rindfleisch",
                "fill_categories": [ping],
                "status": STATUS_DRAFT,
            }
        },
    )

    # Translate button is expected since there is an available language to translate to
    url = get_admin_change_url(created_beef["original"])
    response = admin_client.get(url)
    assert response.status_code == 200
    dom = html_pyquery(response)

    existings = dom.find(".lotus-siblings-resume a")
    assert len(existings) == 1

    links = dom.find(".lotus-translate-link")
    assert len(links) == 1

    # Expected existing translation languages (without the original language)
    existing_languages = [item.get("data-lotus-langcode") for item in existings]
    assert sorted(existing_languages) == ["de"]

    response = admin_client.get(links[0].get("href"))
    assert response.status_code == 200

    # Form is expected since there is an available language. Directly use the URL from
    # translate button
    dom = html_pyquery(response)
    forms = dom.find("#lotus-translate-original-form")
    assert len(forms) == 1

    # Check expected available language is correct
    options = dom.find("#lotus-translate-original-form #id_language option")
    option_ids = [item.get("value") for item in options if item.get("value")]
    assert sorted(option_ids) == ["fr"]

    # Ensure the original id is correctly set into hidden input
    original_id = dom.find("#lotus-translate-original-form input[name='original']")
    assert len(original_id) == 1
    assert int(original_id[0].get("value")) == created_beef["original"].id
