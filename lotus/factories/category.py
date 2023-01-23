from django.conf import settings

import factory

from ..models import Category
from ..utils.factory import fake_html_paragraphs
from ..utils.imaging import DjangoSampleImageCrafter


class CategoryFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a Category.
    """
    language = settings.LANGUAGE_CODE
    original = None
    title = factory.Sequence(lambda n: "Category {0}".format(n))
    slug = factory.Sequence(lambda n: "category-{0}".format(n))
    description = factory.Faker("text", max_nb_chars=150)

    class Meta:
        model = Category

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
    def cover(self):
        """
        Fill cover field with generated image.

        Returns:
            django.core.files.File: File object.
        """
        crafter = DjangoSampleImageCrafter()
        return crafter.create()


def multilingual_category(**kwargs):
    """
    A shortand to create an original Category and its translation.

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

    original = CategoryFactory(**kwargs)
    kwargs["original"] = original

    for lang in langs:
        context = kwargs.copy()
        context["language"] = lang

        if lang in contents:
            context.update(contents[lang])

        translations[lang] = CategoryFactory(
            **context
        )

    return {
        "original": original,
        "translations": translations,
    }
