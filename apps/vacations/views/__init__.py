"""Vistas reservadas para la app de vacaciones."""

from .view_create_request import create_vacation_request_view
from .view_review_request import review_vacation_request_view

__all__ = [
    "create_vacation_request_view",
    "review_vacation_request_view",
]
