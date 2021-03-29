"""
=================
Article factories
=================

"""
from django.conf import settings
from django.utils import timezone

import factory

from ..models import Article
from ..choices import STATUS_PUBLISHED
from ..utils.factory import fake_html_paragraphs
from ..utils.imaging import create_image_file

from .author import AuthorFactory
from .category import CategoryFactory


class ArticleFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of an Article.
    """
    language = settings.LANGUAGE_CODE
    original = None
    status = STATUS_PUBLISHED
    title = factory.Sequence(lambda n: "Article {0}".format(n))
    slug = factory.Sequence(lambda n: "article-{0}".format(n))
    publish_start = factory.LazyFunction(timezone.now)
    publish_end = None

    class Meta:
        model = Article

    @factory.lazy_attribute
    def last_update(self):
        """
        Fill last update date from publication date.

        Returns:
            django.timezone: Datetime timezone enabled.
        """
        return self.publish_start

    @factory.lazy_attribute
    def cover(self):
        """
        Fill file field with generated image.

        Returns:
            django.core.files.File: File object.
        """
        return create_image_file()

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
            max_nb_chars=100,
            nb_paragraphs=2,
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
    # pylint: disable=unused-argument
    def fill_categories(self, create, extracted, **kwargs):
        """
        Add categories.

        Arguments:
            create (bool): True for create strategy, False for build strategy.
            extracted (object): If empty, will create a new random category object.
                Else, expect a list of Category objects to add. Give a ``False``
                value to avoid creating random categories.
        """
        # Do nothing for build strategy
        if not create or extracted is False:
            return

        # Take given category objects
        if extracted:
            categories = extracted
        # Create a new random category adopting the article language
        else:
            categories = [CategoryFactory(language=self.language)]

        # Add categories
        for category in categories:
            self.categories.add(category)

    @factory.post_generation
    # pylint: disable=unused-argument
    def fill_authors(self, create, extracted, **kwargs):
        """
        Add authors.

        Arguments:
            create (bool): True for create strategy, False for build strategy.
            extracted (object): If empty, will create a new random author object.
                Else, expect a list of Author objects to add. Give a ``False``
                value to avoid creating random categories.
        """
        # Do nothing for build strategy
        if not create or extracted is False:
            return

        # Take given author objects
        if extracted:
            authors = extracted
        # Create a new random author
        else:
            authors = [AuthorFactory()]

        # Add authors
        for author in authors:
            self.authors.add(author)


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
        from "langs" argument. Item are index by their language code.
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
