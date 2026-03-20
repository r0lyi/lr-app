from django.contrib.auth.backends import ModelBackend
from apps.users.models import User

# Custom authentication backend para autenticar usando DNI en lugar de username
class DNIBackend(ModelBackend):
    # Sobrescribimos el método authenticate para buscar al usuario por su DNI
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(dni=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None