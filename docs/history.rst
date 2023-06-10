.. _intro_history:

=======
History
=======


Version 0.5.3 - Unreleased
--------------------------

* Removed path prefix ``articles/`` from detail view URL since it is useless;
* Added new setting ``LOTUS_CRUMBS_TITLES`` so crumb title for views can be customized
  from settings. However this does not apply for detail views which directly use their
  object title as the crumb title;
* Changed view so Lotus is compatible with single language project (when middleware
  ``LocaleMiddleware`` is disabled);
* Fixed admin views for Article and Category to not fail when there is an object saved
  with language that are not available anymore;
* Added ``seo_title``, ``lead``, ``introduction``, ``content`` to seachable fields in
  Article admin list;
* Added ``lead``, ``description`` to seachable fields in Category admin list;
* Added new filter to Article admin list to filter on published or unpublished items;
* Moved admin filters from ``lotus.admin.translated`` to ``lotus.admin_filters``;
* Upgraded to ``django-autocomplete-light>=3.9.7``;
* Removed temporary fix for DAL in Article admin change view template;


Version 0.5.2.1 - 2023/06/03
----------------------------

A fix release for migration missing callables for choices value and default
which leaded Django to require a new Lotus migration when changing language or status
settings.


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
