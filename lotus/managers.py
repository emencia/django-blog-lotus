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
    def published_for(self, target_date):
        return self.filter(
            models.Q(publish_start__lte=target_date),
            models.Q(publish_end__gt=target_date) | models.Q(publish_end=None),
            is_published=True,
        )

    def unpublished_for(self, target_date):
        return self.exclude(
            models.Q(publish_start__lte=target_date),
            models.Q(publish_end__gt=target_date) | models.Q(publish_end=None),
            is_published=True,
        )


class BaseTranslatedQuerySet(models.QuerySet):
    """
    Base queryset for translation methods.
    """
    def get_for_lang(self, language):
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
        """
        Return object related to either current lang (if lang arg is
        None) or given lang code.
        """
        language = language or settings.LANGUAGE_CODE

        return self.get_queryset().get_for_lang(language)


class ArticleManager(models.Manager):
    """
    Article objects manager.
    """
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def get_published(self):
        """
        Only return the published objects.
        """
        now = timezone.now()

        return self.get_queryset().published_for(now)

    def get_unpublished(self):
        """
        Only return the non published objects.
        """
        now = timezone.now()

        return self.get_queryset().unpublished_for(now)

    def get_for_lang(self, language=None):
        """
        Return object related to either current lang (if lang arg is
        None) or given lang code.
        """
        language = language or settings.LANGUAGE_CODE

        return self.get_queryset().get_for_lang(language)
