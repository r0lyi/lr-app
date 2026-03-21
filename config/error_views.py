"""Vistas de error reutilizables para rutas mal formadas o no encontradas."""

from django.shortcuts import render


def page_not_found_view(request, unknown_path=None):
    """Muestra una pagina 404 amigable cuando ninguna URL coincide."""
    return render(
        request,
        "errors/error_404.html",
        {
            "requested_path": request.path,
            "unknown_path": unknown_path,
        },
        status=404,
    )
