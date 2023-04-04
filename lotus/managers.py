from django.db import models

from .lookups import LookupBuilder


class BasePublishedQuerySet(LookupBuilder, models.QuerySet):
    """
    Base queryset for publication methods.
    """
    def get_published(self, target_date=None, language=None, prefix=None):
        """
        Return a queryset with published entries selected.

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
        return self.filter(
            *self.build_publication_conditions(
                target_date=target_date,
                language=language,
                prefix=prefix
            )
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
        return self.exclude(
            *self.build_publication_conditions(
                target_date=target_date,
                language=language,
                prefix=prefix
            )
        )


class BaseTranslatedQuerySet(LookupBuilder, models.QuerySet):
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
        return self.filter(
            *self.build_language_conditions(language, prefix=prefix)
        )

    def get_siblings(self, source):
        """
        For given object, return the sibling objects which can be the original object
        and translation objects.

        Arguments:
            source (object): Object to use for its id and original_id used in queryset
                lookup.

        Returns:
            queryset: Queryset with sibling articles. For an original article it will
            be all of its translations. For a translation article it will be its
            original article and all other original's translation articles.
        """
        # Translations use complex lookups to regroup original and translations.
        return self.filter(
            *self.build_siblings_conditions(source)
        )


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

    def get_siblings(self, source):
        return self.get_queryset().get_siblings(source)


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

    def get_siblings(self, source):
        return self.get_queryset().get_siblings(source)


class AuthorManager(models.Manager):
    """
    Author objects manager.

    Use the ArticleQuerySet class to inherit article queryset behaviors.
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
