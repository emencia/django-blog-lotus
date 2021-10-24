from django.contrib import admin


class CustomLotusAdminContext:
    """
    Mixin to add required context for a custom model admin view.

    The view which use it must have the ``model`` correctly set to your model, if your
    view has no model then this mixin is probably useless.

    Also, there is an additional useful context variable ``title`` to set yourself in
    your view since its value is totally related to the view itself.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
            "app_label": self.model._meta.app_label,
            "app_path": self.request.get_full_path(),

        })

        return context
