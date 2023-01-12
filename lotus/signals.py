"""
==========================
Signal receivers functions
==========================

"""
from pathlib import Path


def auto_purge_cover_file_on_delete(sender, instance, **kwargs):
    """
    Deletes 'cover' file from filesystem when corresponding object is deleted.

    To be used on signal ``django.db.models.signals.post_delete``.
    """
    if instance.cover and Path(instance.cover.path).is_file():
        instance.cover.storage.delete(instance.cover.path)


def auto_purge_cover_file_on_change(sender, instance, **kwargs):
    """
    Deletes old 'cover' file from filesystem when corresponding object is
    updated with new cover file.

    Try to perform an additional get request on instance object to get its
    previous value just before current save.

    It's safe about case when file does not exists anymore.

    To be used on signal ``django.db.models.signals.pre_save``.
    """
    # Do not do anything for creation
    if not instance.pk:
        return False

    try:
        old_obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False
    else:
        old_cover = old_obj.cover

    if old_cover and old_cover != instance.cover and Path(old_cover.path).is_file():
        instance.cover.storage.delete(old_cover.path)


def auto_purge_media_files_on_delete(sender, instance, **kwargs):
    """
    Purge media files (cover and image fields) from filesystem when
    corresponding object is deleted.

    To be used on signal ``django.db.models.signals.post_delete``.
    """
    if instance.cover and Path(instance.cover.path).is_file():
        instance.cover.storage.delete(instance.cover.path)

    if instance.image and Path(instance.image.path).is_file():
        instance.image.storage.delete(instance.image.path)


def auto_purge_media_files_on_change(sender, instance, **kwargs):
    """
    Purge old media files (cover and image fields) from filesystem when
    corresponding object is updated with new media files.

    Try to perform an additional get request on instance object to get its
    previous value just before current save.

    It is safe if file does not exists anymore.

    To be used on signal ``django.db.models.signals.pre_save``.
    """
    # Do not do anything for creation
    if not instance.pk:
        return False

    try:
        old_obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False
    else:
        old_cover = old_obj.cover
        old_image = old_obj.image

    if old_cover and old_cover != instance.cover and Path(old_cover.path).is_file():
        instance.cover.storage.delete(old_cover.path)

    if old_image and old_image != instance.image and Path(old_image.path).is_file():
        instance.image.storage.delete(old_image.path)
