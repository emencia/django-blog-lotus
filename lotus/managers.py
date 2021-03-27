"""
Model querysets and managers.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class BasePublishedQuerySet(models.QuerySet):
    """
    Base queryset for publication methods.
    """
    def get_published(self, target_date=None):
        target_date = target_date or timezone.now()

        return self.filter(
            models.Q(publish_start__lte=target_date),
            models.Q(publish_end__gt=target_date) | models.Q(publish_end=None),
        )

    def get_unpublished(self, target_date=None):
        target_date = target_date or timezone.now()

        return self.exclude(
            models.Q(publish_start__lte=target_date),
            models.Q(publish_end__gt=target_date) | models.Q(publish_end=None),
        )


class BaseTranslatedQuerySet(models.QuerySet):
    """
    Base queryset for translation methods only.
    """
    def get_for_lang(self, language=None):
        language = language or settings.LANGUAGE_CODE

        return self.filter(language=language)


class ArticleQuerySet(BasePublishedQuerySet, BaseTranslatedQuerySet):
    """
    Article queryset mix publication and translation querysets.
    """
    pass


class CategoryManager(models.Manager):
    """
    Categroy objects manager.
    """
    def get_queryset(self):
        return BaseTranslatedQuerySet(self.model, using=self._db)

    def get_for_lang(self, language=None):
        return self.get_queryset().get_for_lang(language)


class ArticleManager(models.Manager):
    """
    Article objects manager.
    """
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def get_published(self, target_date=None):
        return self.get_queryset().get_published(target_date)

    def get_unpublished(self, target_date=None):
        return self.get_queryset().get_unpublished(target_date)

    def get_for_lang(self, language=None):
        return self.get_queryset().get_for_lang(language)
