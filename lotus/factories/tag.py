from django.conf import settings

from faker import Faker

import factory

from taggit.models import Tag


class TagFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a Tag.
    """
    name = factory.Sequence(lambda n: "Tag {0}".format(n))
    slug = factory.Sequence(lambda n: "tag-{0}".format(n))

    class Meta:
        model = Tag


class TagsFactory:
    """
    Aint not a factory with factory boy but indeed provide a common way to build a
    batch of tags

    TODO: Docstring to fill and should be renamed to TagsBuilder

    Keyword Arguments:
        language (string):
        faker (Faker):
    """
    def __init__(self, language=None, faker=None):
        self.language = language or settings.LANGUAGE_CODE
        self.faker = faker or Faker(self.language)
        self._built = []

    def __str__(self):
        return ", ".join(self._built)

    def build(self, length):
        """
        Create a list of random tag names with Faker.

        Arguments:
            length (int):

        Returns:
            list:
        """
        self._built = [
            item.capitalize()
            for item in self.faker.words(length, unique=True)
        ]

        return self._built
