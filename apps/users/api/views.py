"""Vistas API del dominio de usuarios."""

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.api.permissions import IsRrhhOrAdmin
from apps.users.api.serializers import DNITokenObtainPairSerializer


class DNITokenObtainPairView(TokenObtainPairView):
    """Endpoint JWT compatible con el flujo actual de login por DNI."""

    serializer_class = DNITokenObtainPairSerializer


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsRrhhOrAdmin])
def session_token_view(request):
    """Emite un JWT para el usuario autenticado por sesion Django."""

    refresh = RefreshToken.for_user(request.user)
    return Response(
        {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    )
