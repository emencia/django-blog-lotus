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

    TODO:
        * Implement translations for Category and Article;
    """
    help = (
        "Create Author, Article and Category objects for demonstration purpose."
        "You may need to use flush options to remove objects to avoid constraint "
        "failures on some unique fields. Currently only working for default "
        "language. Default length of created objects depends on limits settings."
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
            Author.objects.exclude(is_superuser=True).delete()

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
            self.style.SUCCESS("* Creating {} authors".format(self.author_length))
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

            self.stdout.write("  {}) Author: {}".format(
                str(i).zfill(2),
                obj.username,
            ))
            created.append(obj)

        return created

    def create_categories(self):
        """
        Create Category objects required length from factory.
        """
        created = []

        self.stdout.write(
            self.style.SUCCESS("* Creating {} categories".format(self.category_length))
        )

        for i in range(1, self.category_length + 1):
            title = self.faker.unique.company()
            slug = slugify(title)

            obj = CategoryFactory(
                title=title,
                slug=slug,
            )

            self.stdout.write("  {}) Category: {}".format(
                str(i).zfill(2),
                obj.title,
            ))
            created.append(obj)

        return created

    def create_articles(self, authors=[], categories=[]):
        """
        Create Article objects required length from factory.
        """
        created = []

        self.stdout.write(
            self.style.SUCCESS("* Creating {} articles".format(self.article_length))
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

            obj = ArticleFactory(
                title=title,
                slug=slug,
                fill_authors=random.sample(
                    authors,
                    random.randint(1, authors_count),
                ),
                fill_categories=random.sample(
                    categories,
                    random.randint(1, categories_count),
                ),
                fill_related=random.sample(
                    created,
                    random.randint(0, relations_count),
                ),
            )

            self.stdout.write("  {}) Article: {}".format(
                str(i).zfill(2),
                obj.title,
            ))
            created.append(obj)

        return created

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("=== Starting creations ===")
        )

        # Should be validated there are greater than 1
        self.author_length = options["authors"]
        self.article_length = options["articles"]
        self.category_length = options["categories"]

        # Initialize faker instance
        self.faker = Faker()

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

        # Create objects (order does matter)
        created_authors = self.create_authors()

        created_categories = self.create_categories()

        self.create_articles(
            authors=created_authors,
            categories=created_categories,
        )
