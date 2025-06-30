from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import Usuario 

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'email', 'role', 
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'email' in self.fields:
            self.fields['email'].required = True # Garante que o email é obrigatório no form

class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulário customizado para autenticação de usuário, permitindo login
    com nome de usuário (username) ou email.
    """
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        # Altera o rótulo do campo 'username' para ser mais genérico
        self.fields['username'].label = 'Usuário ou Email'

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(self.request, username=username, password=password)

            if user is None:
                # Se a autenticação inicial falhar, e o username parece um email,
                # tenta encontrar o usuário pelo email e autenticar usando o username real.
                if '@' in username:
                    try:
                        user_by_email = Usuario.objects.get(email=username)
                        user = authenticate(
                            self.request,
                            username=user_by_email.username,
                            password=password
                        )
                    except Usuario.DoesNotExist:
                        # Se não encontrar pelo email, o usuário permanece None
                        pass

            if user is None:
                # Se ainda não autenticado, levanta erro de login inválido
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.user_cache = user # Armazena o usuário autenticado no cache do formulário
        return self.cleaned_data