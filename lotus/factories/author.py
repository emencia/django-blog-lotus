import factory

from django.db.models.signals import post_save

from ..models import Author


@factory.django.mute_signals(post_save)
class AuthorFactory(factory.django.DjangoModelFactory):
    """
    Factory to create an Author object, which is finally a Django auth User
    model.
    """
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Sequence(lambda n: "demo-user-%d" % n)
    is_active = True
    is_staff = False
    is_superuser = False
    password = "secret"

    class Meta:
        model = Author
        skip_postgeneration_save = True

    class Params:
        """
        Declare traits that add relevant parameters for admin and superuser
        """
        flag_is_admin = factory.Trait(
            is_superuser=False,
            is_staff=True,
            username=factory.Sequence(lambda n: "admin-%d" % n),
        )
        flag_is_superuser = factory.Trait(
            is_superuser=True,
            is_staff=True,
            username=factory.Sequence(lambda n: "superuser-%d" % n),
        )

    @factory.lazy_attribute
    def email(self):
        """
        Email is automatically build from username
        """
        return "%s@test.com" % self.username

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Ensure the raw password gets set after the initial save
        """
        password = kwargs.pop("password", None)
        obj = super(AuthorFactory, cls)._create(model_class, *args, **kwargs)
        obj.set_password(password)
        obj.save()
        return obj
