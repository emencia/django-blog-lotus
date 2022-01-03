.. _intro_history:

=======
History
=======


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
