.. _intro_references_test:

=====
Tests
=====

A new document todo to improve comprehensiveness of how we do tests.

* Why using the common ``@freeze_time("2012-10-15 10:00:00")``
* Why using the ``settings.LANGUAGE_CODE = "en"`` at start of tests;
* Why using ``json.loads(json.dumps(...))`` to assert payloads;
