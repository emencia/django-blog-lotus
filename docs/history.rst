.. _intro_history:

=======
History
=======


Version 0.5.0 - Unreleased
--------------------------

**Enter in beta stage**

* **Dropped Python 3.6 and 3.7 support**;
* **Dropped Django 3.1 support** (in fact it should currently work but is not able to
  run tests so we can not keep support);
* **Added Python 3.10 support**;
* **Added Django 4.0 and 4.1 support**;
* Add github templates for bug report and feature request;
* Define admin context varname and url arg from settings instead of AdminModeMixin
  attributes, close issue #33;
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


Version 0.4.4 - 2022/01/03
--------------------------

**Not released to a package**

This is the last Alpha branch version, it have everything working still needs some
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

**Not released to a package**

* Article, Category and Author models;
* Article and Category translations;
* Basic template integrations;
* Demonstration layout with Bootstrap 5.1.x;
* Full test coverage;


Version 0.1.0 - Unreleased
--------------------------

First commit to start repository.
