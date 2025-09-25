from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from ..managers import AuthorManager


class AuthorManagerEnabled(models.Model):
    """
    Proxy model manager to avoid overriding default User's manager:

    https://docs.djangoproject.com/en/dev/topics/db/models/#proxy-model-managers
    """
    lotus_objects = AuthorManager()

    class Meta:
        abstract = True


class Author(get_user_model(), AuthorManagerEnabled):
    """
    Proxy model around User model gotten from
    :class:`django.contrib.auth.models.get_user_model`.
    """
    def __str__(self):
        """
        If the user has a full name, use it instead of the username.
        """
        return (self.get_full_name()
                or self.get_short_name()
                or self.get_username())

    def get_absolute_url(self):
        """
        Builds and returns the author's URL based on his username.

        TODO: The try..except does not seems useful.
        """
        try:
            return super().get_absolute_url()
        except AttributeError:
            return reverse("lotus:author-detail", args=[self.get_username()])

    def get_absolute_api_url(self):
        """
        Return absolute URL to the author detail viewset from API.

        Returns:
            string: An URL.
        """
        return reverse("lotus-api:author-detail", kwargs={"pk": self.id})

    COMMON_ORDER_BY = ["first_name", "last_name"]
    """
    List of field order commonly used in frontend view/api
    """

    class Meta:
        """
        Author's meta informations.
        """
        proxy = True
