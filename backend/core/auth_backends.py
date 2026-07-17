from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class EmailBackend(ModelBackend):
    """Permite iniciar sesión utilizando el correo electrónico institucional."""
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Si el usuario ingresó un correo, lo buscamos en la base de datos
        if username and '@' in username:
            try:
                user = Usuario.objects.get(email__iexact=username)
                if user.check_password(password):
                    return user
            except Usuario.DoesNotExist:
                return None
        # Si no tiene arroba o falla lo anterior, dejamos que el backend nativo intente por username
        return super().authenticate(request, username=username, password=password, **kwargs)