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
    def get_published(self, target_date=None, language=None, prefix=None):
        """
        Return a queryset with published entries selected.

        This build a complex queryset about status, publish start date, publish start
        time, publish end datetime and language.

        Keyword Arguments:
            target_date (datetime.datetime): Datetime timezone aware for
                publication target, if empty default value will be the current
                datetime.
            language (string): Language code to filter on. If empty, language is not
                filtered.
            prefix (string): Prefix to append on each lookup expression on
                publication dates fields (start/end). Commonly used to filter
                from a relation like ``author__``. Default is empty.

        Returns:
            queryset: Queryset to filter published entries.
        """
        prefix = prefix or ""
        target_date = target_date or timezone.now()

        base_lookups = {
            prefix + "status": STATUS_PUBLISHED,
        }
        if language:
            base_lookups[prefix + "language"] = language

        return self.filter(
            models.Q(**base_lookups),
            models.Q(**{prefix + "publish_date__lt": target_date.date()}) |
            models.Q(
                models.Q(**{prefix + "publish_date": target_date.date()}),
                models.Q(**{prefix + "publish_time__lte": target_date.time()})
            ),
            models.Q(**{prefix + "publish_end__gt": target_date}) |
            models.Q(**{prefix + "publish_end": None}),
        )

    def get_unpublished(self, target_date=None, language=None, prefix=None):
        """
        Return a queryset with unpublished entries selected.

        Keyword Arguments:
            target_date (datetime.datetime): Datetime timezone aware for
                publication target, if empty default value will be the current
                datetime.
            language (string): Language code to filter on. If empty, language is not
                filtered.
            prefix (string): Prefix to append on each lookup expression on
                publication dates fields (start/end). Commonly used to filter
                from a relation like ``author__``. Default is empty.

        Returns:
            queryset: Queryset to filter published entries.
        """
        prefix = prefix or ""
        target_date = target_date or timezone.now()

        base_lookups = {
            prefix + "status": STATUS_PUBLISHED,
        }
        if language:
            base_lookups[prefix + "language"] = language

        return self.exclude(
            models.Q(**base_lookups),
            models.Q(**{prefix + "publish_date__lt": target_date.date()}) |
            models.Q(
                models.Q(**{prefix + "publish_date": target_date.date()}),
                models.Q(**{prefix + "publish_time__lte": target_date.time()})
            ),
            models.Q(**{prefix + "publish_end__gt": target_date}) |
            models.Q(**{prefix + "publish_end": None}),
        )


class BaseTranslatedQuerySet(models.QuerySet):
    """
    Base queryset for translation methods only.
    """
    def get_for_lang(self, language, prefix=None):
        """
        Return a queryset with unpublished entries selected.

        Arguments:
            language (string): Language code to filter on.

        Keyword Arguments:
            prefix (string): Prefix to append on each lookup expression. Commonly used
                to filterfrom a relation. Default is empty.

        Returns:
            queryset: Queryset to filter published entries.
        """
        prefix = prefix or ""
        language = language or settings.LANGUAGE_CODE

        return self.filter(**{prefix + "language": language})


class ArticleQuerySet(BasePublishedQuerySet, BaseTranslatedQuerySet):
    """
    Article queryset mix publication and translation QuerySet classes.
    """
    pass


class CategoryManager(models.Manager):
    """
    Categroy objects manager.
    """
    def get_queryset(self):
        return BaseTranslatedQuerySet(self.model, using=self._db)

    def get_for_lang(self, language):
        return self.get_queryset().get_for_lang(language)


class ArticleManager(models.Manager):
    """
    Article objects manager.
    """
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def get_published(self, target_date=None, language=None):
        return self.get_queryset().get_published(
            target_date=target_date,
            language=language,
        )

    def get_unpublished(self, target_date=None, language=None):
        return self.get_queryset().get_unpublished(
            target_date=target_date,
            language=language,
        )

    def get_for_lang(self, language):
        return self.get_queryset().get_for_lang(language)


class AuthorManager(models.Manager):
    """
    Author objects manager.
    """
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def get_active(self, target_date=None, language=None):
        """
        Return distinct authors which have published articles.
        """
        q = self.get_queryset()

        q = q.get_published(
            target_date=target_date,
            language=language,
            prefix="articles__"
        )

        return q.distinct()
