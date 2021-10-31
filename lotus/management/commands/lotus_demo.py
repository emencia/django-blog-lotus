import random

from faker import Faker

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from lotus.factories import (
    ArticleFactory, AuthorFactory, CategoryFactory,
)
from lotus.models import Article, Author, Category


class Command(BaseCommand):
    """
    Demo data maker.
    """
    help = (
        "Create Author, Article and Category objects for demonstration purpose."
        "You should use the flush options to remove objects to avoid constraint "
        "failures on some unique fields. Default length of created objects depends on "
        "limits settings. Author are shared with every languages. For translations, it "
        "will create articles and categories in other languages and link them to "
        "originals (created objects with default language)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--authors",
            type=int,
            default=(settings.LOTUS_AUTHOR_PAGINATION * 2),
            help="Number of Author object to create. Must be greater than 1.",
        )
        parser.add_argument(
            "--flush-authors",
            action="store_true",
            help="Flush all author objects (except superuser) before creations.",
        )
        parser.add_argument(
            "--articles",
            type=int,
            default=(settings.LOTUS_ARTICLE_PAGINATION * 2),
            help="Number of Article object to create. Must be greater than 1.",
        )
        parser.add_argument(
            "--flush-articles",
            action="store_true",
            help="Flush all article objects before creations.",
        )
        parser.add_argument(
            "--categories",
            type=int,
            default=(settings.LOTUS_CATEGORY_PAGINATION * 2),
            help="Number of Category object to create. Must be greater than 1.",
        )
        parser.add_argument(
            "--flush-categories",
            action="store_true",
            help="Flush all category objects before creations.",
        )
        parser.add_argument(
            "--flush-all",
            action="store_true",
            help=(
                "Flush all objects no matter other flush arguments have been "
                "used or not."
            ),
        )
        parser.add_argument(
            "--translation",
            type=str,
            metavar="LANGUAGE",
            choices=[
                item[0] for item in settings.LANGUAGES
                if (item[0] != settings.LANGUAGE_CODE)
            ],
            action="append",
            help=(
                "A language code (like 'fr' or 'fr-be') to enable for translations. "
                "This is a cumulative argument. Only enabled languages from "
                "'settings.LANGUAGES' are allowed. By default, there is no enabled "
                "language for translations, object are only created for default "
                "language from 'settings.LANGUAGE_CODE'."
            )
        )

    def flush(self, articles=False, authors=False, categories=False):
        """
        Flush required model objects.
        """

        if articles:
            self.stdout.write(
                self.style.WARNING("* Flushing all articles")
            )
            Article.objects.all().delete()

        if authors:
            self.stdout.write(
                self.style.WARNING("* Flushing all authors")
            )
            # Keep all admins
            Author.objects.exclude(is_staff=True).delete()

        if categories:
            self.stdout.write(
                self.style.WARNING("* Flushing all categories")
            )
            Category.objects.all().delete()

    def create_authors(self):
        """
        Create Author objects required length from factory.
        """
        created = []

        self.stdout.write(
            self.style.SUCCESS("* Creating {length} authors".format(
                length=self.author_length,
            ))
        )

        for i in range(1, self.author_length + 1):
            first_name = self.faker.unique.first_name()
            last_name = self.faker.unique.last_name()
            username = slugify("{} {}".format(first_name, last_name))

            obj = AuthorFactory(
                first_name=first_name,
                last_name=last_name,
                username=username,
                flag_is_admin=True,
            )

            self.stdout.write("  {index}) Author: {username}".format(
                index=str(i).zfill(2),
                username=obj.username,
            ))
            created.append(obj)

        return created

    def random_reservation(self, length, choices):
        """
        Reserve a set of random items from given choices.

        Only the two tiers of items are reserved and last tier is filled with None
        items to fit length. This give a random behavior to add foreign key relations
        where not all available items are used.
        """
        empty = []
        empty_slots = 0
        reservation = 0

        # Harcoded reservation computation, this is a little bit tricky and weak
        if length > 6:
            empty_slots = 4
            reservation = length - empty_slots
        elif length > 4:
            empty_slots = 3
            reservation = length - empty_slots
        elif length > 2:
            empty_slots = 1
            reservation = length - empty_slots

        if empty_slots:
            empty = [None for item in range(empty_slots)]

        reserved = random.sample(choices, reservation) + empty
        random.shuffle(reserved)

        return reserved

    def create_categories(self, language, originals=None):
        """
        Create Category objects required length from factory.
        """
        created = []

        msg = "* Creating {length} categories for language '{lang}'"
        self.stdout.write(
            self.style.SUCCESS(msg.format(
                length=self.category_length,
                lang=language,
            ))
        )

        if originals:
            reserved_originals = self.random_reservation(
                self.category_length, originals
            )

        # Create categories for required length
        for i in range(1, self.category_length + 1):
            title = self.faker.unique.company()
            slug = slugify(title)

            context = {
                "title": title,
                "slug": slug,
                "language": language,
            }
            # Use item from reserved originals according to the object index
            if originals:
                context["original"] = reserved_originals[i - 1]

            obj = CategoryFactory(**context)

            self.stdout.write("  {index}) Category: {title}".format(
                index=str(i).zfill(2),
                title=obj.title,
            ))
            created.append(obj)

        return created

    def create_articles(self, language, authors=[], categories=[], originals=None):
        """
        Create Article objects required length from factory.
        """
        created = []

        msg = "* Creating {length} articles for language '{lang}'"
        self.stdout.write(
            self.style.SUCCESS(msg.format(
                length=self.article_length,
                lang=language,
            ))
        )

        if originals:
            reserved_originals = self.random_reservation(
                self.article_length, originals
            )

        for i in range(1, self.article_length + 1):
            title = self.faker.unique.sentence(nb_words=5)
            slug = slugify(title)

            # Estimate how many authors exists to relate on, but never more than 5
            authors_count = 0
            if self.author_length > 5:
                authors_count = 5
            elif self.author_length > 1:
                authors_count = self.author_length
            elif self.author_length > 0:
                authors_count = 1

            # Estimate how many categories exists to relate on, but never more than 5
            categories_count = 0
            if self.category_length > 5:
                categories_count = 5
            elif self.category_length > 1:
                categories_count = self.category_length
            elif self.category_length > 0:
                categories_count = 1

            # Estimate how many article exists to relate on, but never more than 5
            relations_count = 0
            if len(created) > 5:
                relations_count = 5
            elif len(created) > 1:
                relations_count = len(created)
            elif len(created) > 0:
                relations_count = 1

            context = {
                "title": title,
                "slug": slug,
                "language": language,
                "fill_authors": random.sample(
                    authors,
                    random.randint(1, authors_count),
                ),
                "fill_categories": random.sample(
                    categories,
                    random.randint(1, categories_count),
                ),
                "fill_related": random.sample(
                    created,
                    random.randint(0, relations_count),
                ),
            }
            # Use item from reserved originals according to the object index
            if originals:
                context["original"] = reserved_originals[i - 1]

            obj = ArticleFactory(**context)

            self.stdout.write("  {index}) Article: {title}".format(
                index=str(i).zfill(2),
                title=obj.title,
            ))
            created.append(obj)

        return created

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("=== Starting creations ===")
        )

        self.translation_languages = options["translation"]

        self.stdout.write(
            self.style.SUCCESS("Enabled translations: {}".format(
                ",".join(self.translation_languages)
            ))
        )

        # Should be validated there are greater than 1
        self.author_length = options["authors"]
        self.article_length = options["articles"]
        self.category_length = options["categories"]

        # Initialize faker instance with default language
        self.faker = Faker(settings.LANGUAGE_CODE)

        # Manage object flush
        flush_articles = options["flush_articles"]
        flush_authors = options["flush_authors"]
        flush_categories = options["flush_categories"]
        if options["flush_all"]:
            flush_articles = True
            flush_authors = True
            flush_categories = True

        self.flush(
            articles=flush_articles,
            authors=flush_authors,
            categories=flush_categories,
        )

        # Create objects (order does matter) for default language
        created_authors = self.create_authors()

        created_categories = {
            settings.LANGUAGE_CODE: self.create_categories(
                language=settings.LANGUAGE_CODE
            ),
        }

        created_articles = self.create_articles(
            settings.LANGUAGE_CODE,
            authors=created_authors,
            categories=created_categories[settings.LANGUAGE_CODE],
        )

        # Continue for enabled languages
        for code in self.translation_languages:
            # Init again faker with given language
            self.faker = Faker(code)

            created_categories[code] = self.create_categories(
                code,
                originals=created_categories[settings.LANGUAGE_CODE],
            )

            self.create_articles(
                code,
                authors=created_authors,
                categories=created_categories[code],
                originals=created_articles,
            )
