# backend/core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroUsuarioForm(UserCreationForm):
    """Formulario de registro que utiliza nuestro modelo y exige el correo."""
    
    # Declaramos explícitamente el campo de email para hacerlo obligatorio
    email = forms.EmailField(
        required=True, 
        label="Correo electrónico",
        help_text="Necesario para que el creador del proyecto te pueda invitar."
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Le decimos a Django que ahora queremos el username y el email
        # (Las contraseñas se agregan solas automáticamente)
        fields = ('username', 'email')