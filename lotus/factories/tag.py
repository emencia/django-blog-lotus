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


class TagNameBuilder:
    """
    A helper to create a batch of valid Tag names to use for creating Tag objects.

    Keyword Arguments:
        language (string): Language code to use to create random content with Faker.
            Default to the default ``settings.LANGUAGE_CODE``.
        faker (Faker): A Faker instance to use. Default to a new Faker instance create
            on the fly with given language. If a Faker instance is given, the language
            argument is not used, since given Faker instance already got one.
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
            length (int): Number of tags to create.

        Returns:
            list: A list of strings for built tag names (one word per tag).
        """
        self._built = [
            item.capitalize()
            for item in self.faker.words(length, unique=True)
        ]

        return self._built
