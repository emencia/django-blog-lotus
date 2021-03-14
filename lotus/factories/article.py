# -*- coding: utf-8 -*-
from django.conf import settings

import factory

from .category import CategoryFactory
from ..models import Article


class ArticleFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of an Article.
    """
    language = settings.LANGUAGE_CODE
    original = None
    title = factory.Sequence(lambda n: "Article {0}".format(n))
    slug = factory.Sequence(lambda n: "article-{0}".format(n))

    class Meta:
        model = Article

    @factory.post_generation
    # pylint: disable=unused-argument
    def fill_categories(self, create, extracted, **kwargs):
        """
        Add categories.

        Arguments:
            create (bool): True for create strategy, False for build strategy.
            extracted (object): If empty, will create a new random category object.
                Else, expect a list of Category objects to add.
        """
        # Do nothing for build strategy
        if not create:
            return

        # Take given category objects
        if extracted:
            categories = extracted
        # Create a new random category
        else:
            categories = [CategoryFactory()]

        # Add categories
        for category in categories:
            self.categories.add(category)


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

    original = ArticleFactory(**kwargs)
    kwargs["original"] = original

    for l in langs:
        context = kwargs.copy()
        context["language"] = l

        if l in contents:
            context.update(contents[l])

        translations[l] = ArticleFactory(
            **context
        )

    return {
        "original": original,
        "translations": translations,
    }
