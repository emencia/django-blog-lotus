import datetime

from django.conf import settings
from django.utils import timezone

import factory

from ..models import Article
from ..choices import STATUS_PUBLISHED, get_article_template_default
from ..utils.factory import fake_html_paragraphs
from ..utils.imaging import DjangoSampleImageCrafter

from .author import AuthorFactory
from .category import CategoryFactory
from .tag import TagFactory


class ArticleFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of an Article.

    No relations for category, author, related or author are created by default, it
    needs to be explicitely asken for with post generation methods.
    """
    language = settings.LANGUAGE_CODE
    original = None
    status = STATUS_PUBLISHED
    title = factory.Sequence(lambda n: "Article {0}".format(n))
    slug = factory.Sequence(lambda n: "article-{0}".format(n))
    featured = False
    pinned = False
    private = False
    publish_end = None
    album = None
    seo_title = ""
    cover_alt_text = factory.Faker("text", max_nb_chars=50)
    image_alt_text = factory.Faker("text", max_nb_chars=50)
    template = get_article_template_default()

    class Meta:
        model = Article
        skip_postgeneration_save = True

    @factory.lazy_attribute
    def publish_date(self):
        """
        Return current date.

        Returns:
            datetime.date: Current time.
        """
        return timezone.now().date()

    @factory.lazy_attribute
    def publish_time(self):
        """
        Return current time without timezone since it's not supported by all DB
        backends.

        Returns:
            datetime.time: Current time (timezone not aware).
        """
        return timezone.now().time()

    @factory.lazy_attribute
    def last_update(self):
        """
        Fill last update date from publication date.

        Returns:
            django.timezone: Datetime timezone enabled.
        """
        return datetime.datetime.combine(
            self.publish_date, self.publish_time
        ).replace(tzinfo=datetime.timezone.utc)

    @factory.lazy_attribute
    def cover(self):
        """
        Fill cover field with generated image.

        Returns:
            django.core.files.File: File object.
        """
        crafter = DjangoSampleImageCrafter()
        return crafter.create()

    @factory.lazy_attribute
    def image(self):
        """
        Fill image field with generated image.

        Returns:
            django.core.files.File: File object.
        """
        crafter = DjangoSampleImageCrafter()
        return crafter.create()

    @factory.lazy_attribute
    def lead(self):
        """
        Fill lead field with short plain text.

        Returns:
            string: Plain text.
        """
        return fake_html_paragraphs(
            is_html=False,
            max_nb_chars=55,
            nb_paragraphs=1,
        )

    @factory.lazy_attribute
    def introduction(self):
        """
        Fill introduction field with HTML.

        Returns:
            string: HTML content.
        """
        return fake_html_paragraphs(
            max_nb_chars=55,
            nb_paragraphs=1,
        )

    @factory.lazy_attribute
    def content(self):
        """
        Fill content field with HTML.

        Returns:
            string: HTML content.
        """
        return fake_html_paragraphs()

    @factory.post_generation
    def fill_categories(self, create, extracted, **kwargs):
        """
        Add categories.

        Arguments:
            create (bool): True for create strategy, False for build strategy.
            extracted (object): If ``True``, will create a new random category
                object. If a list assume it's a list of Category objects to add.
                Else if empty don't do anything.
        """
        # Do nothing for build strategy
        if not create or not extracted:
            return

        # Create a new random category adopting the article language
        if extracted is True:
            categories = [CategoryFactory(language=self.language)]
        # Take given category objects
        else:
            categories = extracted

        # Add categories
        for category in categories:
            self.categories.add(category)

    @factory.post_generation
    def fill_authors(self, create, extracted, **kwargs):
        """
        Add authors.

        Arguments:
            create (bool): True for create strategy, False for build strategy.
            extracted (object): If ``True``, will create a new random author
                object. If a list assume it's a list of Author objects to add.
                Else if empty don't do anything.
        """
        # Do nothing for build strategy
        if not create or not extracted:
            return

        # Create a new random author
        if extracted is True:
            authors = [AuthorFactory()]
        # Take given author objects
        else:
            authors = extracted

        # Add authors
        for author in authors:
            self.authors.add(author)

    @factory.post_generation
    def fill_related(self, create, extracted, **kwargs):
        """
        Add related articles.

        Arguments:
            create (bool): True for create strategy, False for build strategy.
            extracted (list): Expect a list of Article objects to add. Else
            don't do anything.
        """
        # Do nothing for build strategy
        if not create or not extracted:
            return

        for item in extracted:
            self.related.add(item)

    @factory.post_generation
    def fill_tags(self, create, extracted, **kwargs):
        """
        Add tags.

        .. Note::

            This won't works in build strategy since Taggit need to have an object
            primary key to build its generic type relation.

        Arguments:
            create (bool): True for create strategy, False for build strategy.
            extracted (list):  If ``True``, will create a new random tag
                object. If a list assume it's a list of Tag objects to add.
                Else if empty don't do anything.
        """
        if not create or not extracted:
            return

        # Create a new random tag
        if extracted is True:
            tags = [TagFactory()]
        # Take given tag objects
        else:
            tags = extracted

        # Add tags
        self.tags.add(*tags)


def multilingual_article(**kwargs):
    """
    A shortand to create an original Article and its translation.

    Arguments:
        **kwargs: Keyword arguments passed to factory for original generation
            then for translation generations. May be altered for each translation
            with relative content in ``contents``.

    Keyword Arguments:
        langs (list): List of language code for each translation category to
            create.
        contents (dict): Each item is index on a language code and contains
            kwargs to pass to the factory for this language.

    Returns:
        dict: A dict where "original" item is the original category object and
        "translations" is a dict of translations object for language required
        from "langs" argument. Item are indexed by their language code.
    """
    langs = set(kwargs.pop("langs", []))
    contents = kwargs.pop("contents", {})
    translations = {}

    # Create original object
    original = ArticleFactory(**kwargs)
    kwargs["original"] = original

    # Create translations adopting original kwargs or possible language
    # specific kwargs if any
    for lang in langs:
        context = kwargs.copy()
        context["language"] = lang

        if lang in contents:
            context.update(contents[lang])

        translations[lang] = ArticleFactory(
            **context
        )

    return {
        "original": original,
        "translations": translations,
    }
