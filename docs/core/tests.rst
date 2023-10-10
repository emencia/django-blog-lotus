.. _references_tests_intro:

=====
Tests
=====

There is a lot of tests and we try to make them "straight to the point", however we
sometime need to use some technics to ease test development. This document will try
to resume them.


Freezetime
**********

Most of tests are using `FreezeGun <https://github.com/spulec/freezegun>`_ decorator
like:  ::

    @freeze_time("2012-10-15 10:00:00")

This is to avoid playing with date and time in tests since Lotus code sometime use
``datetime.now()``, with FreezeGun we can always set the same datetime and ease
asserting on expected date.


Language
********

Many tests include this kind of code line : ::

    settings.LANGUAGE_CODE = "en"

This is to ensure the test is working in an exact language because Lotus filter content
on language and some Django code may involve to set a different language from a test to
another.

Using this line, explicitely set the right expected language and avoid that a
previously executed tests change it to another one that would make a further test to
fail.


Result serialization in JSON
****************************

You may see some tests that are serializing and deserializing result payloads with
something like: ::

    json.loads(json.dumps(...))

This is a convenient way to ease assertions against expected data because sometime
payload contains various Python object that may not be simply asserted. It is much
simpler to compare two simple dictionnaries with string than dictionnaries with Python
objects inside.

This may not allways work since JSON can only serialize a few set of object types
without to declare a custom encoder. Finally this is something you may not use
everytime since it may speed down tests.
