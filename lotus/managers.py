"""
============================
Model querysets and managers
============================

"""
from django.conf import settings
from django.db import models
from django.utils import timezone

from .choices import STATUS_PUBLISHED


class BasePublishedQuerySet(models.QuerySet):
    """
    Base queryset for publication methods.
    """
    def get_published(self, target_date=None, prefix=None):
        """
        Return a queryset with published entries selected.

        TODO: It needs to include checking also about "status" value.

        Keyword Arguments:
            target_date (datetime.datetime): Datetime timezone aware for
                publication target, default to the current datetime.
            prefix (string): Prefix to append on each lookup expression on
                publication dates fields (start/end). Commonly used to filter
                from a relation like ``author__``. Default is empty.

        Returns:
            queryset: Queryset to filter published entries.
        """
        prefix = prefix or ""
        target_date = target_date or timezone.now()

        return self.filter(
            models.Q(**{prefix + "status": STATUS_PUBLISHED}),
            models.Q(**{prefix + "publish_start__lte": target_date}),
            models.Q(**{prefix + "publish_end__gt": target_date}) |
            models.Q(**{prefix + "publish_end": None}),
        )

    def get_unpublished(self, target_date=None, prefix=None):
        """
        Return a queryset with unpublished entries selected.

        Keyword Arguments:
            target_date (datetime.datetime): Datetime timezone aware for
                publication target, default to the current datetime.
            prefix (string): Prefix to append on each lookup expression on
                publication dates fields (start/end). Commonly used to filter
                from a relation. Default is empty.

        Returns:
            queryset: Queryset to filter published entries.
        """
        prefix = prefix or ""
        target_date = target_date or timezone.now()

        return self.exclude(
            models.Q(**{prefix + "status": STATUS_PUBLISHED}),
            models.Q(**{prefix + "publish_start__lte": target_date}),
            models.Q(**{prefix + "publish_end__gt": target_date}) |
            models.Q(**{prefix + "publish_end": None}),
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


class AuthorManager(models.Manager):
    """
    Author objects manager.
    """
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def get_published(self, target_date=None):
        """
        Return authors which have published articles.
        """
        return self.get_queryset().get_published(
            target_date,
            prefix="articles__"
        ).distinct()

    def get_unpublished(self, target_date=None):
        """
        Return authors which have unpublished articles.
        """
        return self.get_queryset().get_unpublished(target_date, prefix="articles__")
