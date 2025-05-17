import random
from pathlib import Path

from faker import Faker

from PIL import ImageFont

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from taggit.models import Tag

from lotus.factories import (
    AlbumFactory, AlbumItemFactory, ArticleFactory, AuthorFactory, CategoryFactory,
    TagNameBuilder,
)
from lotus.models import Album, Article, Author, Category
from lotus.choices import STATUS_DRAFT
from lotus.utils.imaging import DjangoSampleImageCrafter


# Enabled Background colors (as item key) with their allowed text color (as item value)
PLACEHOLDER_PALETTE = getattr(settings, "LOTUS_DEMO_PLACEHOLDER_PALETTE", {
    "#3d8eb9": "#ffffff",
    "#eb6361": "#ffffff",
    "#71ba51": "#ffffff",
    "#ce86ed": "#ffffff",
    "#78c4fb": "#ffffff",
    "#fc6e51": "#ffffff",
    "#48cfad": "#ffffff",
    "#cab7f2": "#ffffff",
    "#ffdfa3": "#af8f53",
    "#eec374": "#ffffff",
    "#cbccce": "#ffffff",
    "#89888a": "#ffffff",
})


# Available image format to randomly use to create a placeholder
PLACEHOLDER_FORMATS = getattr(settings, "LOTUS_DEMO_PLACEHOLDER_FORMATS", [
    "PNG", "SVG"
])


ALBUM_MEDIA_SIZE = getattr(settings, "LOTUS_DEMO_ALBUM_MEDIA_SIZE", (640, 480))
ARTICLE_COVER_SIZE = getattr(settings, "LOTUS_DEMO_ARTICLE_COVER_SIZE", (300, 200))
ARTICLE_LARGE_SIZE = getattr(settings, "LOTUS_DEMO_ARTICLE_LARGE_SIZE", (1280, 640))
CATEGORY_COVER_SIZE = getattr(settings, "LOTUS_DEMO_CATEGORY_COVER_SIZE", (800, 500))


class Command(BaseCommand):
    """
    Demo data maker.

    TODO:

        Variance creation is not safe against the 'articles' argument if it
        is less than needed from variances, each variance requiring at least a
        dedicated article in addition to the base articles.

        The command should be tested to be safer and articles/authors/categories/tags
        arguments should be validated. Actually if they do not match needed length,
        the script will fail.
    """
    help = (
        "Create Author, Album, Article and Category objects for demonstration purpose."
        "You should use the flush options to remove objects to avoid constraint "
        "failures on some unique fields. Default length of created objects depends on "
        "limits settings. Author are shared with every languages. For translations, it "
        "will create articles and categories in other languages and link them to "
        "originals (created objects with default language)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--albums",
            type=int,
            default=settings.LOTUS_ARTICLE_PAGINATION,
            help=(
                "Length of Album objects to create. Must be at least half of "
                "article length and greater or equal to 1."
            ),
        )
        parser.add_argument(
            "--flush-albums",
            action="store_true",
            help="Flush all album objects before creations.",
        )
        parser.add_argument(
            "--item-per-album",
            type=int,
            default=12,
            help=(
                "Maximum of item to add to each album. Must equal or greater than 1."
            ),
        )
        parser.add_argument(
            "--authors",
            type=int,
            default=(settings.LOTUS_AUTHOR_PAGINATION * 2),
            help="Length of Author objects to create. Must be greater than 1.",
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
            help="Length of Article objects to create. Must be greater than 7.",
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
            help="Length of Category objects to create. Must be greater than 1.",
        )
        parser.add_argument(
            "--flush-categories",
            action="store_true",
            help="Flush all category objects before creations.",
        )
        parser.add_argument(
            "--tags",
            type=int,
            default=30,
            help="Length of Tag objects to create. Must be greater than 1.",
        )
        parser.add_argument(
            "--tag-per-article",
            type=int,
            default=5,
            help=(
                "Maximum of Tag to add to each article. Must be less than tag length "
                "to create."
            ),
        )
        parser.add_argument(
            "--flush-tags",
            action="store_true",
            help="Flush all taggit tag objects before creations.",
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
            default=[],
            action="append",
            help=(
                "A language code (like 'fr' or 'fr-be') to enable for translations. "
                "This is a cumulative argument. Only enabled languages from "
                "'settings.LANGUAGES' are allowed. By default, there is no enabled "
                "language for translations, object are only created for default "
                "language from 'settings.LANGUAGE_CODE'."
            )
        )
        parser.add_argument(
            "--font",
            type=str,
            metavar="FILEPATH",
            default=None,
            help=(
                "A path to a TrueType font to use to create random bitmap images. If "
                "empty, a default non TrueType font will be used which leads to badly "
                "positionned text in bitmap images."
            ),
        )

    def flush(self, albums=False, articles=False, authors=False, categories=False,
              tags=False):
        """
        Flush required model objects.
        """

        if albums:
            self.stdout.write(
                self.style.WARNING("* Flushing all albums")
            )
            Album.objects.all().delete()

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

        if tags:
            self.stdout.write(
                self.style.WARNING("* Flushing all tags")
            )
            Tag.objects.all().delete()

    def build_random_placeholder(self, slug, size, background=None, text_color=None,
                                 format_name=None):
        """
        Create a random placeholder image.

        Bg color and format (PNG or SVG) are randomized. Filename is built from slug.
        """
        background = background or random.choice(list(PLACEHOLDER_PALETTE.keys()))
        text_color = text_color or PLACEHOLDER_PALETTE[background]
        format_name = format_name or random.choice(PLACEHOLDER_FORMATS)
        extension = format_name.lower()

        built = self.image_crafter.create(
            filename="{name}.{ext}".format(name=slug, ext=extension),
            size=size,
            bg_color=background,
            text=True,
            text_color=text_color,
            format_name=format_name,
        )

        return built

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

    def get_filled_slots(self, length, items, empty_value=None, ratio=0.75):
        """
        Computate a list starting from given items then filled with empty value to
        match required length.

        Returns:
            list: New list filled started from ``items`` and possibly filled with empty
            value.
        """
        slot_length = len(items)
        if length >= slot_length:
            slot_length = round(length * ratio)

        slots = items + [empty_value] * (slot_length - len(items))
        random.shuffle(slots)

        return slots

    def create_albums(self):
        """
        Create Album objects for required length.
        """
        created = []

        self.stdout.write(
            self.style.SUCCESS("* Creating {length} albums".format(
                length=self.album_length,
            ))
        )

        for i in range(1, self.album_length + 1):
            items_length = random.randint(1, self.item_per_album)
            album = AlbumFactory()

            for k in range(0, items_length):
                background = random.choice(list(PLACEHOLDER_PALETTE.keys()))
                text_color = PLACEHOLDER_PALETTE[background]

                AlbumItemFactory(
                    album=album,
                    media=self.build_random_placeholder(
                        "foo-{}".format(i),
                        ALBUM_MEDIA_SIZE,
                        background=background,
                        text_color=text_color,
                        format_name="PNG",
                    ),
                )

            self.stdout.write("  {index}) Album: {title} ({items} items)".format(
                index=str(i).zfill(2),
                title=album.title,
                items=items_length,
            ))
            created.append(album)

        return created

    def create_authors(self):
        """
        Create Author objects for required length.
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

    def create_tags(self, faker):
        """
        Create a list of unique tags for required length.

        Arguments:
            faker (Faker): A Faker instance to use to generated words.

        Returns:
            list: List of tag names.
        """
        self.stdout.write(
            self.style.SUCCESS("* Creating {length} tags".format(
                length=self.tag_length,
            ))
        )

        builder = TagNameBuilder(faker=faker)

        return builder.build(self.tag_length)

    def create_categories(self, language, originals=None):
        """
        Create Category objects for required length.
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
            # Choose color
            background = random.choice(list(PLACEHOLDER_PALETTE.keys()))
            text_color = PLACEHOLDER_PALETTE[background]

            context = {
                "title": title,
                "slug": slug,
                "language": language,
                "cover": self.build_random_placeholder(
                    slug,
                    CATEGORY_COVER_SIZE,
                    background=background,
                    text_color=text_color,
                ),
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

        """
        WARNING:
            This was used as a quick fix resolution for factory that produced a
            dummy path. Disabled for now because it leaded to error on usage of
            Postgresql. (Need to be rechecked with sqlite3).

            This was because from batch for english language, the factory sequence
            finished on something like '5' so the last path was "0005". But then
            'fix_tree' operation incremented all path, so the last one was finally
            "0006".

            But then for the next batch for french language, the sequence is at '6' so
            it try to create an object with path "0006" and this lead to SQL error
            about uniquenes constraint for path.
        """
        # Category.fix_tree(fix_paths=True)

        return created

    def create_articles(self, language, albums=[], authors=[], categories=[], tags=[],
                        originals=None):
        """
        Create Article objects for required length.
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

        # Make a list of album slots started from created album list and filled with
        # null value to fit to article length
        reserved_albums = self.get_filled_slots(self.article_length, albums)

        for i in range(1, self.article_length + 1):
            title = self.faker.unique.sentence(nb_words=5)
            slug = slugify(title)
            # Choose color
            background = random.choice(list(PLACEHOLDER_PALETTE.keys()))
            text_color = PLACEHOLDER_PALETTE[background]

            # Estimate how many authors exists to relate on, but never more than 3
            authors_count = 0
            if self.author_length > 3:
                authors_count = 3
            elif self.author_length > 1:
                authors_count = self.author_length
            elif self.author_length > 0:
                authors_count = 1

            # Estimate how many categories exists to relate on, but never more than 3
            categories_count = 0
            if self.category_length > 3:
                categories_count = 3
            elif self.category_length > 1:
                categories_count = self.category_length
            elif self.category_length > 0:
                categories_count = 1

            # Estimate how many article exists to relate on, but never more than 3
            relations_count = 0
            if len(created) > 3:
                relations_count = 3
            elif len(created) > 1:
                relations_count = len(created)
            elif len(created) > 0:
                relations_count = 1

            context = {
                "title": title,
                "slug": slug,
                "language": language,
                "cover": self.build_random_placeholder(
                    slug,
                    ARTICLE_COVER_SIZE,
                    background=background,
                    text_color=text_color,
                ),
                "image": self.build_random_placeholder(
                    slug,
                    ARTICLE_LARGE_SIZE,
                    background=background,
                    text_color=text_color,
                ),
                "album": random.choice(reserved_albums),
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
                "fill_tags": random.sample(
                    tags,
                    random.randint(0, self.tag_per_article),
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

        # Registry for already used article for states so they are never used twice.
        # Also, we will ignore the first item and only use articles from first page.
        # NOTE: This will probably fail if there is less than 7 articles.
        used_in_variance = []
        # Sort created article from last published to the first one
        created_ordered = sorted(
            created,
            key=lambda item: item.publish_time
        )

        # Put draft state on random article
        draft_article = random.choice(
            [
                item
                for item in created_ordered[1:self.article_length]
                if item not in used_in_variance
            ]
        )
        draft_article.status = STATUS_DRAFT
        draft_article.save()
        used_in_variance.append(draft_article)

        # Put pinned state on random article
        pinned_article = random.choice(
            [
                item
                for item in created_ordered[1:self.article_length]
                if item not in used_in_variance
            ]
        )
        pinned_article.pinned = True
        pinned_article.save()
        used_in_variance.append(pinned_article)

        # Put featured state on random article
        featured_article = random.choice(
            [
                item
                for item in created_ordered[1:self.article_length]
                if item not in used_in_variance
            ]
        )
        featured_article.featured = True
        featured_article.save()
        used_in_variance.append(featured_article)

        # Put private state on random article
        private_article = random.choice(
            [
                item
                for item in created_ordered[1:self.article_length]
                if item not in used_in_variance
            ]
        )
        private_article.private = True
        private_article.save()
        used_in_variance.append(private_article)

        # Change date to make publication end from 2 years
        passed_article = random.choice(
            [
                item
                for item in created_ordered[1:self.article_length]
                if item not in used_in_variance
            ]
        )
        passed_article.publish_end = passed_article.publish_date.replace(
            year=(passed_article.publish_date.year - 2)
        )
        passed_article.save()
        used_in_variance.append(passed_article)

        # Change date to schedule publication in 2 years
        futur_article = random.choice(
            [
                item
                for item in created_ordered[1:self.article_length]
                if item not in used_in_variance
            ]
        )
        futur_article.publish_date = futur_article.publish_date.replace(
            year=(futur_article.publish_date.year + 2)
        )
        futur_article.save()
        used_in_variance.append(futur_article)

        # Put private mixed states on random article
        mixed_article = random.choice(
            [
                item
                for item in created_ordered[1:self.article_length]
                if item not in used_in_variance
            ]
        )
        mixed_article.pinned = True
        mixed_article.private = True
        mixed_article.featured = True
        mixed_article.draft = True
        mixed_article.save()

        return created

    def get_font(self, font_path=None):
        if not font_path:
            return None

        font = Path(font_path).resolve()
        # Temporary validation, we can do better
        assert font.exists()

        return ImageFont.truetype(str(font), 12)

    def validate_command_args(self, *args, **options):
        """
        Naive validation on command arguments.

        TODO:
        Object lengths should be smarter to avoid issues with missing left relations
        needed in random choices because of uniqueness.
        """
        if options["articles"] < 2:
            raise CommandError("Argument 'articles' should be greater than 1")

        if options["categories"] < 2:
            raise CommandError("Argument 'categories' should be greater than 1")

        if options["albums"] < 2:
            raise CommandError("Argument 'albums' should be greater or equal to 1")
        elif options["albums"] < (options["articles"] / 2):
            raise CommandError(
                "Argument 'albums' should be at least half of article length."
            )

        if options["tags"] < 2:
            raise CommandError("Argument 'tags' should be greater than 1")

        if options["tag_per_article"] > options["tags"]:
            raise CommandError((
                "Argument 'tag-per-article' can not be greater than 'tags' argument "
                "value."
            ))

        if options["item_per_album"] < 1:
            raise CommandError((
                "Argument 'item-per-album' must be greater or equal to 1."
            ))

        return True

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("=== Starting creations ===")
        )

        self.validate_command_args(*args, **options)

        self.font = self.get_font(font_path=options["font"])

        self.image_crafter = DjangoSampleImageCrafter(font=self.font)

        self.translation_languages = options["translation"]

        if self.translation_languages:
            self.stdout.write(
                self.style.SUCCESS("Enabled translations: {}".format(
                    ",".join(self.translation_languages)
                ))
            )

        # Register limits from command arguments
        self.album_length = options["albums"]
        self.author_length = options["authors"]
        self.article_length = options["articles"]
        self.category_length = options["categories"]
        self.tag_length = options["tags"]
        self.tag_per_article = options["tag_per_article"]
        self.item_per_album = options["item_per_album"]

        # Initialize faker instance with default language
        self.faker = Faker(settings.LANGUAGE_CODE)

        # Manage object flush
        flush_albums = options["flush_albums"]
        flush_articles = options["flush_articles"]
        flush_authors = options["flush_authors"]
        flush_categories = options["flush_categories"]
        flush_tags = options["flush_tags"]
        if options["flush_all"]:
            flush_articles = True
            flush_authors = True
            flush_categories = True
            flush_tags = True

        self.flush(
            albums=flush_albums,
            articles=flush_articles,
            authors=flush_authors,
            categories=flush_categories,
            tags=flush_tags,
        )

        # Create objects (order does matter) for default language only
        created_albums = self.create_albums()

        created_authors = self.create_authors()

        created_categories = {
            settings.LANGUAGE_CODE: self.create_categories(
                language=settings.LANGUAGE_CODE
            ),
        }

        created_articles = self.create_articles(
            settings.LANGUAGE_CODE,
            albums=created_albums,
            authors=created_authors,
            categories=created_categories[settings.LANGUAGE_CODE],
            tags=self.create_tags(self.faker),
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
                albums=created_albums,
                authors=created_authors,
                categories=created_categories[code],
                originals=created_articles,
                tags=self.create_tags(self.faker),
            )
