from django.conf import settings
from django.db import models
from django.utils import timezone

from .choices import STATUS_PUBLISHED


class LookupBuilder:
    """
    A convenient interface to build complex lookups.

    It has been done to cover Article and Category models, except some methods that
    may be related only to one of those models.

    This exists to share complex lookups build among other models since
    you can use this builder to get lookups for relations or to use in queryset
    annotations from related models.
    """
    def build_publication_conditions(self, target_date=None, language=None,
                                     private=None, prefix=None):
        """
        Return a set of complex lookups for publication criterias.

        This build a complex queryset about status, publish start date, publish start
        time, publish end datetime, private, and language.

        Keyword Arguments:
            target_date (datetime.datetime): Datetime timezone aware for
                publication target, if empty the value will be the current datetime.
            language (string): Language code to filter on. If empty, language is not
                filtered.
            private (boolean): Either True or False to set lookup for 'private' field.
                If not given, private field will not be part of built lookups.
            prefix (string): Prefix to append on each lookup expression on
                publication dates fields (start/end). Commonly used to filter
                from a relation like ``author__``. Default is empty.

        Returns:
            tuple: Lookup conditions to apply all publication criterias (publish dates
            and language) with a ``filter(*conditions)`` or a complex condition
            ``models.Q(*conditions)``.
        """
        prefix = prefix or ""
        target_date = target_date or timezone.now()

        base_lookups = {
            prefix + "status": STATUS_PUBLISHED,
        }
        if language:
            base_lookups[prefix + "language"] = language

        if private is not None:
            base_lookups[prefix + "private"] = private

        return (
            models.Q(**base_lookups),
            models.Q(**{prefix + "publish_date__lt": target_date.date()}) |
            models.Q(
                models.Q(**{prefix + "publish_date": target_date.date()}),
                models.Q(**{prefix + "publish_time__lte": target_date.time()})
            ),
            models.Q(**{prefix + "publish_end__gt": target_date}) |
            models.Q(**{prefix + "publish_end": None}),
        )

    def build_language_conditions(self, language, prefix=None):
        """
        Return simple lookup to filter on language.

        Arguments:
            language (string): Language code to filter on.

        Keyword Arguments:
            prefix (string): Prefix to append on each lookup expression. Commonly used
                to filter from a relation. Default is empty.

        Returns:
            tuple: Lookup conditions to apply language filtering.
        """
        prefix = prefix or ""

        return (
            models.Q(
                **{prefix + "language": language or settings.LANGUAGE_CODE}
            ),
        )

    def build_siblings_conditions(self, source):
        """
        Return lookups to get sibling objects for given source object.

        The siblings can be the original object and translation objects.

        TODO: Method should have an option (enable by default) to only list object for
        enabled languages from ``settings.settings.LANGUAGES``.

        Arguments:
            source (object): Object to use for its id and original_id used in queryset
                lookup.

        Returns:
            tuple: Lookup conditions to get sibling objects. For an original article it
            will be all of its translations. For a translation article it will be its
            original article and all other original's translation articles.
        """
        # Original has just translation relations
        if source.original is None:
            return (models.Q(original=source),)

        # Translations use complex lookups to regroup original and translations.
        return (
            models.Q(**{"id": source.original_id}) |
            models.Q(
                models.Q(**{"original_id": source.original_id}),
                ~models.Q(**{"id": source.id})
            ),
        )
