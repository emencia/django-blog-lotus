import datetime

from django.utils import timezone

from lotus.factories import ArticleFactory, AuthorFactory
from lotus.models import Author
from lotus.utils.tests import queryset_values


def test_author_manager(db):
    """
    Author manager should be able to get all author which have published
    articles and Author method "published_articles" should return all published
    articles for an Author object.
    """
    now = timezone.now()
    tomorrow = now + datetime.timedelta(days=1)
    # Today 5min sooner to avoid shifting with pytest and factory delays
    today = now - datetime.timedelta(minutes=5)

    # Some authors
    picsou = AuthorFactory(username="picsou")
    donald = AuthorFactory(username="donald")
    flairsou = AuthorFactory(username="flairsou")

    # Some articles
    ArticleFactory(
        slug="Klondike",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_authors=[picsou],
    )

    ArticleFactory(
        slug="DuckCity",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_authors=[picsou, donald],
    )

    ArticleFactory(
        slug="Tomorrow",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
        fill_authors=[donald],
    )

    # Check for author which have published articles
    q_authors_published = Author.lotus_objects.get_published()
    data = queryset_values(q_authors_published, names=["username"],
                           orders=["username"])

    assert data == [{"username": "donald"}, {"username": "picsou"}]

    # Check for published articles for each author
    assert queryset_values(flairsou.articles.get_published()) == []

    assert queryset_values(donald.articles.get_published()) == [
        {"language": "en", "slug": "DuckCity"},
    ]

    assert queryset_values(picsou.articles.get_published()) == [
        {"language": "en", "slug": "DuckCity"},
        {"language": "en", "slug": "Klondike"},
    ]
