"""Endpoints de consulta de usuarios."""

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.api.permissions import IsSelfRrhhOrAdmin
from apps.users.models import User
from apps.users.selectors.api_metrics import get_user_summary


@api_view(["GET"])
@permission_classes([IsSelfRrhhOrAdmin])
def user_summary_view(request, user_id):
    """Devuelve una ficha resumida del usuario solicitado."""

    user = get_object_or_404(User, pk=user_id)
    return Response(get_user_summary(user))
