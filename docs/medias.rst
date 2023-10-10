.. _django-smart-media: https://github.com/sveetch/django-smart-media

.. _medias_intro:

======
Medias
======

Category and Article object have some fields to upload media contents. These medias
are managed through `django-smart-media`_ library which allow for any supported format
from PIL plus a soft SVG support.

Soft SVG support
****************

You can upload a SVG file but it won't have a generated thumbnail alike other
formats since it is assumed that vectorial format can resize to fit anywhere.

Unique file name
****************

All uploaded files are renamed with an unique ID so they are always unique and avoid
any encoding issues from filename.

FileField
*********

All field from django-smart-media are still simple Django FileField with some sugar
in admin form for better input layout.

Automatic purge
***************

All field from django-smart-media include an automatic purge for stale content,
this means every files from a deleted Article are removed with it and previous file
from a changed field are removed. This way, your project won't keep storing many stale
files.
