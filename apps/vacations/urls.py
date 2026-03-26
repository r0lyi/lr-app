"""URLs del dominio de vacaciones usadas por el panel del empleado."""

from django.urls import path

from apps.vacations.views import (
    create_vacation_request_view,
    review_vacation_request_view,
)

app_name = "vacations"

urlpatterns = [
    path("request/", create_vacation_request_view, name="create-request"),
    path("requests/<int:request_id>/review/", review_vacation_request_view, name="review-request"),
]
