"""Helpers pequenos para convertir errores de formulario en mensajes visibles."""

from django.utils.translation import gettext as _


def get_first_form_error(form, fallback=None):
    """Devuelve el primer error legible de un formulario Django."""

    fallback = fallback or _("Revisa los datos del formulario e inténtalo de nuevo.")

    for error in form.non_field_errors():
        return str(error)

    for field_name, errors in form.errors.items():
        if field_name == "__all__":
            continue
        field = form.fields.get(field_name)
        label = field.label if field is not None else field_name
        for error in errors:
            return _("%(field)s: %(error)s") % {
                "field": label,
                "error": error,
            }

    return fallback
