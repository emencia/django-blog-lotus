# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.urls import reverse


# A dummy password that should pass form validation
VALID_PASSWORD_SAMPLE = "Azerty12345678"


def get_website_url(site_settings):
    """
    A shortand to retrieve the full website URL according to Site ID and HTTP
    protocole settings.

    Arguments:
        site_settings (django.conf.settings): Settings object.

    Returns:
        string: Full website URL.
    """
    domain = Site.objects.get_current().domain
    protocol = "https://" if site_settings.HTTPS_ENABLED else "http://"

    return "".join([protocol, domain])


def get_relative_path(site_url, url):
    """
    From given URL, retrieve the relative path (URL without domain and starting
    slash).

    Arguments:
        site_url (string): Website URL to remove from given ``url``
            argument.
        url (string): Full URL (starting with http/https) to make relative to
            website URL.

    Returns:
        string: Admin change view URL path for given model object.
    """
    if url.startswith(site_url):
        return url[len(site_url):]

    return url


def get_admin_add_url(model):
    """
    Return the right admin URL for add form view for given class.

    Arguments:
        model (Model object): A model object to use to find its admin
            add form view URL.

    Returns:
        string: Admin add form view URL path.
    """
    url_pattern = "admin:{app}_{model}_add"

    return reverse(url_pattern.format(
        app=model._meta.app_label,
        model=model._meta.model_name
    ))


def get_admin_change_url(obj):
    """
    Return the right admin URL for a change view for given object.

    Arguments:
        obj (Model object): A model object instance to use to find its admin
            change view URL.

    Returns:
        string: Admin change view URL path.
    """
    url_pattern = "admin:{app}_{model}_change"

    return reverse(url_pattern.format(
        app=obj._meta.app_label,
        model=obj._meta.model_name
    ), args=[
        obj.pk
    ])


def get_admin_list_url(model):
    """
    Return the right admin URL for a list view for given class.

    Arguments:
        model (Model object): A model object to use to find its admin
            list view URL.

    Returns:
        string: Admin list view URL path.
    """
    url_pattern = "admin:{app}_{model}_changelist"

    return reverse(url_pattern.format(
        app=model._meta.app_label,
        model=model._meta.model_name
    ))
