import pytest

from lotus.factories import ArticleFactory
from lotus.utils.tests import html_pyquery


@pytest.mark.skip(reason="on hold until models are finished")
def test_article_detail_404(db, client):
    """
    Try to reach unexisting article should return a 404 response.
    """
    article = ArticleFactory(title="article1")

    url = "/{article_pk}/1/".format(article_pk=article.id)

    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.skip(reason="on hold until models are finished")
def test_article_detail_noblog(db, client):
    """
    If required article ID in url does not exists, article detail should return a
    404 response.
    """
    url = "/42/"

    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.skip(reason="on hold until models are finished")
def test_article_detail_content(db, client):
    """
    Article content should be displayed correctly.
    """
    article = ArticleFactory()

    url = "/{article_pk}/".format(
        article_pk=article.id,
    )

    response = client.get(url)

    assert response.status_code == 200

    dom = html_pyquery(response)
    article_title = dom.find(".article-detail h2")
    article_content = dom.find(".article-detail div.content")

    assert article_title.text() == article.title
    # Avoid text() method to remove white spaces since content may contain some
    # line breaks
    assert article_content.text(squash_space=False) == article.content
