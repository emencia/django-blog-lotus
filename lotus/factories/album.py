import factory

from ..models import Album, AlbumItem
from ..utils.imaging import DjangoSampleImageCrafter


class AlbumFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a Album.
    """
    title = factory.Faker("text", max_nb_chars=20)

    class Meta:
        model = Album
        skip_postgeneration_save = True

    @factory.post_generation
    def fill_items(self, create, extracted, **kwargs):
        """
        Add some AlbumItem objects.

        Arguments:
            create (bool): True for create strategy, False for build strategy.
            extracted (object): If ``True``, will create a new random item
                object. If an integer assume it's the lenght of items to create.
                Else won't do anything.
        """
        # Do nothing for build strategy
        if not create or not extracted:
            return

        # Create a new random item
        if extracted is True:
            AlbumItemFactory(album=self)
        elif isinstance(extracted, int):
            for item in range(0, extracted):
                AlbumItemFactory(album=self, order=item)


class AlbumItemFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a AlbumItem.
    """
    album = factory.SubFactory(AlbumFactory)
    title = factory.Faker("text", max_nb_chars=20)
    order = factory.Sequence(lambda n: 10 * n)

    class Meta:
        model = AlbumItem
        skip_postgeneration_save = True

    @factory.lazy_attribute
    def media(self):
        """
        Fill media field with generated image.

        Returns:
            django.core.files.File: File object.
        """
        crafter = DjangoSampleImageCrafter()
        return crafter.create()
