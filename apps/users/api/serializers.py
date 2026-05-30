"""Serializers de autenticacion JWT adaptados al login por DNI."""

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class DNITokenObtainPairSerializer(TokenObtainPairSerializer):
    """Genera tokens JWT usando DNI y contrasena."""

    username_field = "dni"
    dni = serializers.CharField(write_only=True)

    def validate(self, attrs):
        dni = attrs.get("dni")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=dni,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                _("DNI o contraseña incorrectos."),
                code="authorization",
            )

        self.user = user
        data = {}
        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data
