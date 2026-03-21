"""Backends de autenticacion personalizados del proyecto."""

from django.contrib.auth.backends import ModelBackend

from apps.users.models import User


class DNIBackend(ModelBackend):
    """Permite autenticar usando el DNI en lugar del username por defecto."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Busca al usuario por DNI y reaprovecha las comprobaciones de Django."""

        try:
            user = User.objects.get(dni=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
