
=========
Changelog
=========

Development
-----------

A minor release with many things for *Category tree* and some API improvements, there
is no incompatible changes with v0.9.0.

* Updated french translations in PO;
* Updated every Category queryset to use the right ordering for flat or tree listing,
  this should fix issue where some nodes could be missing in tree listing;
* Improved ``Category.get_nested_tree()`` to add a "branch mode" where only nodes from
  a tree branch will be unfolded;
* Changed ``Category.get_nested_tree()`` which accept new arguments ``current`` and
  ``branch``;
* Improved template tag ``get_category_tree_html`` which includes last changes from
  ``Category.get_nested_tree()``;
* Improved Article sitemap class to set another priority value when article is pinned
  or featured;
* Added new options in Article sitemap setting ``pinned_priority`` and
  ``featured_priority`` to define different value for pinned or feature articles;
* Added a new validation on Article and Category forms to avoid to make an
  original object as a translation of another original object. An original can not be
  a translation;
* Added ``translations`` field to Category and Article API detail endpoint;
* Added ``children`` field to Category API detail endpoint;


Version 0.9.0 - 2024/10/15
--------------------------

A major release with new feature *Category tree*, see
`Migration to 0.9.0 <https://django-blog-lotus.readthedocs.io/en/latest/migrations.html#from-0-8-1-to-0-9-0>`_
to know about migrating your project.

**This will be the last version to support Django<4.1.**

* Dropped support for Python 3.8;
* Added new feature 'Category tree':

  * Added django-treebeard to requirements and applied usage in Category model;
  * Adapted Category form to manage the treebeard fields;
  * Added some validation in Category admin form for constraints about language and
    parenting to ensure tree is not corrupted;
  * Added a new admin view to list a tree of categories, this is currently in beta and
    will need some more work in UI/UX before to be ready to override the admin changelist;
  * Added new template tag ``get_category_tree_html`` to display a tree of all categories
    for current language;
  * Added new setting ``LOTUS_CATEGORY_SHORT_CRUMBS`` to disable category ancestors
    listing in breadcrumb;
  * Added new setting ``LOTUS_CATEGORY_TREE_TAG_TEMPLATE`` to define a custom default
    template for template tag ``get_category_tree_html``;

* Added new extra requirements section ``sandbox`` dedicated to sandbox only third party
  application. It is currently not installed from the Makefile task ``install``;
* Added requirement ``drf-redesign`` to sandbox extra requirements;
* Updated Category serializers and its tests to include 'parent' field;
* Fixed syntax error in some help text from ``lotus_demo`` command, close #78;
* Fixed invalid documentation configuration referencing another repository, close #77;
* Fixed Article item fragment template that was still displaying the categories part
  even if it does not have any relatded category, close #73;
* Added Diskette configuration in contrib
* Added ``lotus.contrib.disk.DISKETTE_DEFINITIONS`` list to use with
  `diskette <https://diskette.readthedocs.io/en/latest/>`_ to
  include default configuration to manage dumps for Lotus data;
* Configured and enabled Diskette usage in sandbox;
* Added minimal requirement versions to help Pip resolving;
* Updated script to freeze local dependencies;
* Updated Makefile for minor enhancements;


Version 0.8.1 - 2023/12/01
--------------------------

A minor release with new feature *Sitemaps*, see
`Migration to 0.8.1 <https://django-blog-lotus.readthedocs.io/en/latest/migrations.html#from-0-8-0-to-0-8-1>`_
to know about migrating your project.

* Added a ``modified`` field on Category, Album and AlbumItem models. This was required
  to have accurate update datetime in future ``sitemap.xml``;
* Added Sitemap classes for Article, Author, Category and Tag objects with test
  coverage and documentation;


Version 0.8.0 - 2023/11/22
--------------------------

A major release with new feature *Article album*, see
`Migration to 0.8.0 <https://django-blog-lotus.readthedocs.io/en/latest/migrations.html#from-0-7-0-to-0-8-0>`_
to know about migrating your project.

* Added new feature "Article album":

  * Album holds items which can have a uploaded media;
  * Article can select an Album to display in its detail view;
  * This features comes with new models, factories, setting, template tag and tests;
  * Updated ``lotus_demo`` command to create some albums to use in articles;
  * API does not implement it yet and it will come in the next version;

* Improved quality task to include check-django;
* Adopted some django-ckeditor settings in sandbox for a better usecase with image
  embedded in ckeditor contents;
* Added new meta tag in ``base.html`` to define canonical URL for every pages, this
  needs to enable a new middleware in your Django settings to work. See migration
  document for details;
* Pinned django-taggit to ``<5.0.0`` since the 5.x version drops support of Django 4.0
  that we want to keep for Lotus 0.8.x version;
* Fixed task ``check-migration`` so it returns migration code instead of just signal
  error when there is pending migration. This is required since Django 4.0 the Django
  command ``makemigration`` has some behavior changes;
* Enabled CSS Grid from Bootstrap settings in sandbox frontend (since Grid is used to
  display Album);
* Added API overview documentation;
* Added new stylesheet used in Lotus model admins to improve CKEditor width, this
  configurable from settings;


Version 0.7.0 - 2023/10/11
--------------------------

A major release without almost no breaking changes, see
`Migration to 0.7.0 <https://django-blog-lotus.readthedocs.io/en/latest/migrations.html#from-0-6-1-to-0-7-0>`_
to know about migrating your project.

* Added API with Django REST framework (DRF):

  * API is in beta stage for now, some improvements may come later;
  * API is optional depending DRF is installed or not;
  * API is read only, at least for now;
  * Article, Author and Category have their own entrypoint;
  * Listing and details use different serializers to avoid too large responses;
  * Publication criteria and language filtering is properly implemented alike in HTML
    frontend;

* Added new template tag ``article_get_related`` that is able to properly filter
  related article queryset and use it in article detail template;
* Added new template tag ``get_categories`` to list all categories available in current
  language;
* Added new template tag ``get_categories_html`` which do the same as
  ``get_categories`` but is rendered to HTML fragment from a template;
* Added filter on Category into Article admin list;
* Moved documentation to Furo theme;
* Restructured documentation and improved some parts;
* Fixed warnings about deprecated ``django.utils.timezone.utc`` in favor of
  ``datetime.timezone.utc``;
* Fixed warnings about Factoryboy deprecation with post generators and auto save using
  ``skip_postgeneration_save`` on every factory;


Version 0.6.1 - 2023/08/18
--------------------------

A minor version only to update ``.readthedocs.yml`` file to follow service deprecations
changes.


Version 0.6.0 - 2023/06/12
--------------------------

* **Added Django 4.2 support**;
* Removed path prefix ``articles/`` from detail view URL since it is useless;
* Added new setting ``LOTUS_CRUMBS_TITLES`` so crumb title for views can be customized
  from settings. However this does not apply for detail views which directly use their
  object title as the crumb title;
* Changed view so Lotus is compatible with single language project (when middleware
  ``LocaleMiddleware`` is disabled);
* Fixed admin views for Article and Category to not fail when there is an object saved
  with language that are not available anymore;
* Added ``seo_title``, ``lead``, ``introduction``, ``content`` to searchable fields in
  Article admin list;
* Added ``lead``, ``description`` to searchable fields in Category admin list;
* Added new filter to Article admin list to filter on published or unpublished items;
* Added logo and favicon to documentation and sandbox;
* Renamed some template blocks:

  * ``head_title`` to ``header-title``;
  * ``head_metas`` to ``metas``;
  * ``head_styles`` to ``header-resource``;
  * ``javascript`` to ``body-javascript``;

* Moved admin filters from ``lotus.admin.translated`` to ``lotus.admin_filters``;
* Upgraded to ``django-autocomplete-light>=3.9.7``;
* Removed temporary fix for DAL in Article admin change view template;
* Upgraded Sandbox frontend to ``bootstrap==5.2.3``;
* Added sidebar to Category detail to include some useful infos and links;
* Added publication state to part "Available in languages" in details;


Migrating from previous version
...............................

* Upgrade ``django-autocomplete-light``;
* Use the new template block names if you override some of lotus list, details
  templates;
* If you mounted Lotus on root url path and standing on removed ``articles/`` path to
  not pollute root path, you need to mount Lotus on path like ``blog/`` or even
  ``articles/``;
* If you used Lotus for a single language site, now you may be able to disable
  ``LocaleMiddleware``;
* Now you are able to edit Lotus crumb titles for index views, see settings
  documentation for ``LOTUS_CRUMBS_TITLES``;


Version 0.5.2.1 - 2023/06/03
----------------------------

A fix release for migration missing callables for choices value and default
which leaded Django to require a new Lotus migration when changing language or status
settings.

Migrating from previous version
...............................

If you updated to the previous version and runned the wrong pending migration (which
should start with ``0002``) previously raised by Django, you need to remove it from
you migration history since the current version has fixed this invalid pending
migration.


Version 0.5.2 - 2023/04/04
--------------------------

A fix release to solve issue with ReadTheDocs building.


Version 0.5.1 - 2023/04/04
--------------------------

* Added Article tags feature with ``django-taggit``;
* Added ``django-autocomplete-light`` for a nice widget on Article 'tags' field in
  admin;
* Fixed some tests that played with language and view request, seems between these
  tests the setting ``LANGUAGE_CODE`` may be altered and not turning back to initial
  value. This resulted to weird behaviors where resolved urls got a wrong language
  suffix;
* Pinned requirements for RTFD to fix issue with rtd theme alike it was done in extra
  requirements "dev";
* Fixed missing ``management/`` directory due to missing ``__init__.py`` files;
* Added 'Translate' link to Article detail page along the 'Edit' link;
* Changed models ``get_absolute_url`` method to use ``translate_url`` instead of
  ``translation_activate``;
* Added ``lookups.LookupBuilder``, an abstraction to make complex lookups for
  publication/language criterias for Article and Category;
* Added ``lotus.contrib.django_configuration.LotusDefaultSettings`` class to use with
  `django-configuration <https://django-configurations.readthedocs.io/en/stable/>`_ to
  include default Lotus settings instead of ``from lotus.settings import *``;


Version 0.5.0 - 2023/01/16
--------------------------

**Enter in beta stage**

* **First release on PyPi**;
* **Dropped Python 3.6 and 3.7 support**;
* **Dropped Django 3.1 support** (it should currently work but won't able to
  run tests so we can not keep official support);
* **Added Python 3.10 support**;
* **Added Django 4.0 and 4.1 support**;
* **Rebooted again migrations**
* Add github templates for bug report and feature request;
* Define admin context varname and url arg from settings instead of AdminModeMixin
  attributes;
* Refactored *preview mode* (previously named *admin mode*) to use session instead
  of URL argument and make all missing improvements, close issue #26;
* Added full frontend stack to be able to build Bootstrap CSS and JS for sandbox.
  However frontend assets are currently directly deployed in sandbox and loaded with
  django static tag, there is no 'django-webpack' configuration to use;
* Improved Makefile with new actions and some color on action titles;
* Fixed Demonstration layout for responsive issues and missing Bootstrap Javascript
  loading;
* Changed ``SampleImageCrafter`` to use a TrueType font that is required to remove
  usage of deprecated ``ImageDraw.textsize``;
* Splitted dev requirements to reduce Tox environment installation time;
* Added ``LotusContextStage`` mixin in views for a basic way to mark Lotus menu items
  as active depending current view;
* Replaced usage of ``os`` module for disk I/O in favor of ``pathlib.Path``;
* Replaced usage of ``pytz`` module for timezone crafting in tests to ``timezone``;
* Fixed Tox to install ``backports.zoneinfo`` for combo Python 3.8 + Django 3.2,
  required to run tests;
* Added ``django-smart-media`` to requirements and implemented it as image model fields
  and thumbnailing in templates;
* Added new context argument ``from`` to "items" templates so these items will know
  where they are used and possibly implement some variant behaviors;
* Pinned ``sphinx-rtd-theme`` to ``==1.1.0`` to avoid an
  `issue which enforce install of old 0.5.x release <https://stackoverflow.com/questions/67542699/readthedocs-sphinx-not-rendering-bullet-list-from-rst-file/71069918#71069918>`_;


Version 0.4.4 - 2022/01/03
--------------------------

This is the last Alpha branch version, it has everything working still needs some
improvements and minor features to come with Beta branch versions.

* Improved image crafting for test and demo usage with new classes
  ``SampleImageCrafter`` and ``DjangoSampleImageCrafter``;
* Improved demonstration layout and ergonomy;
* Improved lotus_demo command to add some state variances on some articles;
* Fixed every templates and code to use translation strings for texts;
* Added distinct PO files for application and sandbox in default enabled languages from
  base settings: en, fr, de. "en" is the default language, "fr" is the only one to be
  translated since i don't know german;
* Added ``po`` and ``mo`` actions to Makefile to build PO and compile MO files;
* Fixed ``get_absolute_url`` from models. They used translation activate and deactivate
  methods which was wrong since once called it broke translation rendering in templates.
  We switched back to another solution which activate the object language then activate
  again the current session language just after URL resolution. Worth to notice, i
  don't remember exactly which case this "activate" usage tried to cover (without it
  the tests or front does not fail);


Version 0.4.3 - 2021/12/27
--------------------------

* Article, Category and Author models;
* Article and Category translations;
* Basic template integrations;
* Demonstration layout with Bootstrap 5.1.x;
* Full test coverage;


Version 0.1.0 - Unreleased
--------------------------

First commit to start repository.
