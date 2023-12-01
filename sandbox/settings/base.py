"""
Base Django settings for sandbox
"""

from pathlib import Path

from django import VERSION


SECRET_KEY = "***TOPSECRET***"


# Root of project repository
BASE_DIR = Path(__file__).parents[2]

# Django project
PROJECT_PATH = BASE_DIR / "sandbox"

# Variable content directory, mostly use for local db and media storage in
# deployed environments
VAR_PATH = BASE_DIR / "var"

DEBUG = False

# Https is never enabled on default and development environment, only for
# integration and production.
HTTPS_ENABLED = False

ADMINS = (
    # ("Admin", "PUT_ADMIN_EMAIL_HERE"),
)

MANAGERS = ADMINS

DATABASES = {}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
# TIME_ZONE = "America/Chicago"
TIME_ZONE = "Europe/Paris"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en"

LANGUAGES = (
    ("en", "English"),
    ("fr", "Français"),
    ("de", "Deutsche"),
)

# A tuple of directories where Django looks for translation files
LOCALE_PATHS = [
    PROJECT_PATH / "locale",
]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# We want to avoid warning from this settings that is deprecated since Django 4.x
if VERSION[0] < 4:
    # If you set this to False, Django will not format dates, numbers and
    # calendars according to the current locale.
    USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = VAR_PATH / "media"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = VAR_PATH / "static"

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = [
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROJECT_PATH / "static-sources",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
]

ROOT_URLCONF = "sandbox.urls"

# Python dotted path to the WSGI application used by Django"s runserver.
WSGI_APPLICATION = "sandbox.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            PROJECT_PATH / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": False,
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.forms",
]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Ensure we can override applications widgets templates from project template
# directory, require also 'django.forms' in INSTALLED_APPS
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

"""
Django Treebeard part
"""
INSTALLED_APPS.append(
    "treebeard",
)

"""
Smart media and Sorl parts
"""
from smart_media.settings import *  # noqa: E402,F401,F403

INSTALLED_APPS.extend([
    "sorl.thumbnail",
    "smart_media",
])

"""
CKEditor part
"""
INSTALLED_APPS[0:0] = [
    "ckeditor",
    "ckeditor_uploader",
]

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_RESTRICT_BY_DATE = False
CKEDITOR_IMAGE_BACKEND = "ckeditor_uploader.backends.PillowBackend"
CKEDITOR_BROWSE_SHOW_DIRS = True

CKEDITOR_CONFIGS = {
    "lotus": {
        "width": "100%",
        "height": 400,
        "language": "{{ language }}",
        "skin": "moono-lisa",
        # Enabled showblocks as default behavior
        "startupOutlineBlocks": True,
        # Enable image2 plugin
        "extraPlugins": "image2",
        "image_previewText": True,
        # Disable element filter to enable full HTML5, also this will let
        # append any code, even bad syntax and malicious code, so be careful
        "removePlugins": "stylesheetparser",
        "allowedContent": True,
        "toolbar": "Default",
        "toolbar_Default": [
            ["Undo", "Redo"],
            ["ShowBlocks"],
            ["Format", "Styles"],
            ["RemoveFormat"],
            "/",
            ["Bold", "Italic", "Underline", "-", "Subscript", "Superscript"],
            ["JustifyLeft", "JustifyCenter", "JustifyRight"],
            ["TextColor"],
            ["Link", "Unlink"],
            ["Image", "-", "NumberedList", "BulletedList",
                "-", "Table", "-", "CreateDiv", "HorizontalRule"],
            ["Source"],
        ],
    },
}

"""
django-view-breadcrumbs optional part
"""
try:
    import view_breadcrumbs  # noqa: F401
except ImportError:
    pass
else:
    INSTALLED_APPS[0:0] = [
        "view_breadcrumbs",
    ]


"""
django-taggit part
"""
INSTALLED_APPS[0:0] = [
    "dal",
    "dal_select2",
]
INSTALLED_APPS.append(
    "taggit",
)

"""
DRF
"""
try:
    import rest_framework  # noqa: F401
except ModuleNotFoundError:
    API_AVAILABLE = False
else:
    API_AVAILABLE = True
    INSTALLED_APPS.extend([
        "rest_framework",
        'drf_spectacular',
        'drf_spectacular_sidecar',  # required for Django collectstatic discovery
    ])

    REST_FRAMEWORK = {
        "DEFAULT_PERMISSION_CLASSES": [
            # Use Django"s standard `django.contrib.auth` permissions,
            # or allow read-only access for unauthenticated users.
            "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",
            # Only Django"s standard `django.contrib.auth` permissions, every
            # authenticated user can read and anonymous are never allowed
            # "rest_framework.permissions.DjangoModelPermissions",
        ],
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
        "PAGE_SIZE": 20,
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    }

    SPECTACULAR_SETTINGS = {
        'TITLE': 'Your Project API',
        'DESCRIPTION': 'Your project description',
        'VERSION': '1.0.0',
        'SERVE_INCLUDE_SCHEMA': False,
        'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
        'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
        'REDOC_DIST': 'SIDECAR',
        # OTHER SETTINGS
    }

"""
Diskette part
"""
from diskette.settings import *  # noqa: E402,F401,F403
from lotus.contrib.disk import DISKETTE_DEFINITIONS as LOTUS_DEFINITIONS  # noqa: E402

INSTALLED_APPS.append(
    "diskette",
)

DISKETTE_APPS = [
    [
        "django.contrib.auth", {
            "comments": "django.contrib.auth: user and groups, no perms",
            "natural_foreign": True,
            "models": ["auth.Group", "auth.User"]
        }
    ],
    [
        "django.contrib.sites", {
            "comments": "django.contrib.sites",
            "natural_foreign": True,
            "models": "sites"
        }
    ]
] + LOTUS_DEFINITIONS

# A list of *Unix shell-style wildcards* patterns to filter out some storages files
DISKETTE_STORAGES_EXCLUDES = ["cache/*", "uploads/*"]

# A list of Path objects for storage to collect and dump
DISKETTE_STORAGES = [MEDIA_ROOT]

# For where are stored created dump
DISKETTE_DUMP_PATH = VAR_PATH

# For where to extract archive storages contents
DISKETTE_LOAD_STORAGES_PATH = BASE_DIR


"""
Lotus part
"""
from lotus.settings import *  # noqa: E402,F401,F403

INSTALLED_APPS.append(
    "lotus",
)
