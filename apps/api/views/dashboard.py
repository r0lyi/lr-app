"""Endpoints de metricas generales de la plataforma."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.api.permissions import IsRrhhOrAdmin
from apps.users.selectors.api_metrics import get_user_kpis
from apps.vacations.selectors.api_metrics import get_vacation_request_kpis


@api_view(["GET"])
@permission_classes([IsRrhhOrAdmin])
def request_kpis_view(request):
    """Devuelve KPIs agregados de solicitudes de vacaciones."""

    return Response(get_vacation_request_kpis())


@api_view(["GET"])
@permission_classes([IsRrhhOrAdmin])
def user_kpis_view(request):
    """Devuelve KPIs agregados de usuarios y perfiles."""

    return Response(get_user_kpis())
