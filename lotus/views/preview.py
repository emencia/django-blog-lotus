from django.conf import settings
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy
from django.http import (
    HttpResponse, HttpResponseRedirect,
    HttpResponseBadRequest, HttpResponseForbidden,
)

from ..responses import HttpResponseUnauthorized


class PreviewTogglerView(RedirectView):
    """
    Toggle preview mode in user session.

    The redirection url can not be one of the preview toggler url, this is to avoid
    malicious redirection loop.

    Only authenticated admin user is allowed to use this view and an URL
    argument "next" is required to be given and not relative (not starting with ``/``)
    else it is assumed as a bad operation.
    """
    permanent = False
    disable_url = reverse_lazy("lotus:preview-disable")
    enable_url = reverse_lazy("lotus:preview-enable")
    mode = "enable"

    def get_redirect_url(self, *args, **kwargs):
        """
        Return the URL redirect to. Keyword arguments from the URL pattern
        match generating the redirect request are provided as kwargs to this
        method.
        """
        url = self.request.GET.get("next", "")

        if not url:
            return HttpResponseBadRequest("URL argument 'next' is required.")
        elif not url.startswith("/"):
            return HttpResponseBadRequest(
                "Relative URL for redirection is not allowed."
            )
        elif url in (self.disable_url, self.enable_url):
            return HttpResponseBadRequest(
                "You can not redirect to the preview toggler URL."
            )

        return url

    def set_preview_mode(self, request, mode):
        if mode == "enable":
            request.session[settings.LOTUS_PREVIEW_KEYWORD] = True
        elif mode == "disable":
            request.session[settings.LOTUS_PREVIEW_KEYWORD] = False

    def get(self, request, *args, **kwargs):
        # Anonymous are not allowed here
        if not request.user.is_authenticated:
            return HttpResponseUnauthorized("You are not allowed to be here.")
        # Non staff use are forbidden here
        elif not request.user.is_staff:
            return HttpResponseForbidden(
                "You don't have permission level to use this view."
            )

        # Get redirection URL and validate it
        url = self.get_redirect_url(*args, **kwargs)
        if isinstance(url, HttpResponse):
            return url

        # Switch preview mode in session depending given 'mode' attribute
        self.set_preview_mode(request, self.mode)

        return HttpResponseRedirect(url)
