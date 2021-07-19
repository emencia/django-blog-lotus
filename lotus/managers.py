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

        TODO:
            New way to get published article. This is required since actually it
            does not work correctly with joining like usage in AuthorManager. It
            does not group status & languages lookup which lead to unexpected
            results (only status or language lookup is used in SQL, depending there
            order in complete queryset).

            This new way require to merge "get_for_lang" here so we can put status &
            language lookups aside to be correctly grouped.

            And report it also for unpublished.

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
        print("   .. BasePublishedQuerySet.get_published:", target_date, prefix, language)
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
    def get_for_lang(self, language=None, prefix=None):
        """
        Return a queryset with unpublished entries selected.

        Keyword Arguments:
            language (string): Language code to filter on.
            prefix (string): Prefix to append on each lookup expression. Commonly used
                to filterfrom a relation. Default is empty.

        Returns:
            queryset: Queryset to filter published entries.
        """
        print("   .. BaseTranslatedQuerySet.get_for_lang:", language, prefix)
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

    NOTE: This will still untouched from NG managers.
    """
    def get_queryset(self):
        print("   .. CategoryManager.get_queryset")
        return BaseTranslatedQuerySet(self.model, using=self._db)

    def get_for_lang(self, language=None):
        print("   .. CategoryManager.get_for_lang:", language)
        return self.get_queryset().get_for_lang(language)


class ArticleManager(models.Manager):
    """
    Article objects manager.

    NOTE: Since of manager+QuerySet chaining, some methods may never be used.
    """
    def get_queryset(self):
        print("   .. ArticleManager.get_queryset")
        return ArticleQuerySet(self.model, using=self._db)

    def get_published(self, target_date=None, language=None):
        """
        TODO:
            New way to get published article, include the language filtering.
            Its usage have to be propagated everywhere
        """
        print("   .. ArticleManager.get_published", target_date)
        return self.get_queryset().get_published(
            target_date=target_date,
            language=language,
        )

    def get_unpublished(self, target_date=None):
        return self.get_queryset().get_unpublished(target_date)

    def get_for_lang(self, language=None):
        """
        TODO:
            Will be removed once get_ng_published is used everywhere

            Or not ? (it could be helpful).
        """
        print("   .. ArticleManager.get_for_lang:", language)
        return self.get_queryset().get_for_lang(language)


class AuthorManager(models.Manager):
    """
    Author objects manager.
    """
    def get_queryset(self):
        print("   .. AuthorManager.get_queryset")
        return ArticleQuerySet(self.model, using=self._db)

    def get_active(self, target_date=None, language=None):
        """
        Return distinct authors which have published articles.
        """
        print("   .. AuthorManager.get_active", target_date, language)
        q = self.get_queryset()

        q = q.get_published(
            target_date,
            language=language,
            prefix="articles__"
        )

        return q.distinct()
