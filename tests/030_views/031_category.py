import pytest

from tests.utils import html_pyquery

from lotus.factories import ArticleFactory, CategoryFactory
from lotus.models import Article, Category


@pytest.mark.skip(reason="on hold until models are finished")
def test_category_index_empty(db, client):
    """
    Without any existing category, index view should just return the empty text.
    """
    response = client.get("/")

    assert response.status_code == 200

    dom = html_pyquery(response)
    content = dom.find(".category-list li")[0].text

    assert "No categorys yet." == content


@pytest.mark.skip(reason="on hold until models are finished")
def test_category_index_basic(db, client):
    """
    Category index view should list every category.
    """
    category1 = CategoryFactory(title="category1")
    category2 = CategoryFactory(title="category2")

    response = client.get("/")

    assert response.status_code == 200

    dom = html_pyquery(response)
    items = dom.find(".category-list li")

    expected_titles = [
        "category1",
        "category2",
    ]

    expected_urls = [
        "/{category_pk}/".format(category_pk=category1.id),
        "/{category_pk}/".format(category_pk=category2.id),
    ]

    assert expected_titles == [item.find("a").text for item in items]

    assert expected_urls == [item.find("a").get("href") for item in items]


@pytest.mark.skip(reason="on hold until models are finished")
def test_category_index_pagination(settings, db, client):
    """
    Category index view is paginated from setting limit, not every category is listed
    on the same page.
    """
    # Twice the category pagination limit plus one entry so we can expect three
    # result pages
    category_total = (settings.BLOG_PAGINATION * 2) + 1

    CategoryFactory.create_batch(category_total)

    assert category_total == Category.objects.all().count()

    # First result page
    response = client.get("/")
    assert response.status_code == 200

    dom = html_pyquery(response)
    items = dom.find(".category-list li")
    assert settings.BLOG_PAGINATION == len(items)
    # Check pagination is correct
    pages = dom.find(".pagination a")
    assert 3 == len(pages)

    # Second result page
    response = client.get("/?page=2")
    assert response.status_code == 200

    dom = html_pyquery(response)
    items = dom.find(".category-list li")
    assert settings.BLOG_PAGINATION == len(items)
    # Check current page is correct
    active = dom.find(".pagination a.active")
    assert 1 == len(active)
    assert "2" == active.text()

    # Third result page
    response = client.get("/?page=3")

    assert response.status_code == 200

    dom = html_pyquery(response)
    items = dom.find(".category-list li")
    assert 1 == len(items)


@pytest.mark.skip(reason="on hold until models are finished")
def test_category_detail_404(db, client):
    """
    Try to reach unexisting category should return a 404 response.
    """
    url = "/42/"

    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.skip(reason="on hold until models are finished")
def test_category_detail_no_article(db, client):
    """
    Without any related article, category detail view should just contains its
    content and return the empty text for article list.
    """
    category1 = CategoryFactory(title="category1")

    url = "/{category_pk}/".format(category_pk=category1.id)

    response = client.get(url)

    assert response.status_code == 200

    dom = html_pyquery(response)

    category_title = dom.find(".category-detail h2")
    assert category_title.text() == category1.title

    content = dom.find(".article-list li")[0].text
    assert "No articles yet." == content


@pytest.mark.skip(reason="on hold until models are finished")
def test_category_detail_article_pagination(settings, db, client):
    """
    Category index detail has a paginated list of article and so not every category
    articles are listed on the same page.
    """
    category1 = CategoryFactory(title="category1")

    category_url = "/{category_pk}/".format(category_pk=category1.id)

    article_total = (settings.ARTICLE_PAGINATION * 2) + 1

    ArticleFactory.create_batch(article_total, category=category1)

    assert article_total == Article.objects.all().count()

    # First result page
    response = client.get(category_url)
    assert response.status_code == 200

    dom = html_pyquery(response)
    items = dom.find(".article-list li")
    assert settings.ARTICLE_PAGINATION == len(items)
    # Check pagination is correct
    pages = dom.find(".pagination a")
    assert 3 == len(pages)

    # Second result page
    response = client.get(category_url + "?page=2")
    assert response.status_code == 200

    dom = html_pyquery(response)
    items = dom.find(".article-list li")
    assert settings.ARTICLE_PAGINATION == len(items)
    # Check current page is correct
    active = dom.find(".pagination a.active")
    assert 1 == len(active)
    assert "2" == active.text()

    # Third result page
    response = client.get(category_url + "?page=3")

    assert response.status_code == 200

    dom = html_pyquery(response)
    items = dom.find(".article-list li")
    assert 1 == len(items)
