"""
=============
Author models
=============

"""
from django.apps import apps
from django.conf import settings
from django.db import models
from django.urls import reverse

from ..managers import AuthorManager


def safe_get_user_model():
    """
    Safe loading of the User model, customized or not.
    """
    user_app, user_model = settings.AUTH_USER_MODEL.split('.')
    return apps.get_registered_model(user_app, user_model)


class AuthorManagerEnabled(models.Model):
    """
    Proxy model manager to avoid overriding of the default User's manager:

    https://docs.djangoproject.com/en/dev/topics/db/models/#proxy-model-managers
    """
    lotus_objects = AuthorManager()

    class Meta:
        abstract = True


class Author(safe_get_user_model(), AuthorManagerEnabled):
    """
    Proxy model around :class:`django.contrib.auth.models.get_user_model`.
    """
    def published_articles(self):
        """
        Returns author's published articles.
        """
        return self.articles.get_published()

    def get_absolute_url(self):
        """
        Builds and returns the author's URL based on his username.
        """
        try:
            return super().get_absolute_url()
        except AttributeError:
            return reverse('lotus:author_detail', args=[self.get_username()])

    def __str__(self):
        """
        If the user has a full name, use it instead of the username.
        """
        return (self.get_short_name()
                or self.get_full_name()
                or self.get_username())

    class Meta:
        """
        Author's meta informations.
        """
        proxy = True
