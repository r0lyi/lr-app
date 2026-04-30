"""Personalizacion global del Django Admin."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _


admin.site.site_header = _("LR Clean & Service | Administración")
admin.site.site_title = _("LR Clean & Service")
admin.site.index_title = _("Gestión interna del sistema")
