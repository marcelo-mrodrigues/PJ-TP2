from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import Usuario , Produto, Loja, Oferta, Categoria, Marca

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
    

class ProdutoForm(forms.ModelForm):
    """
    Formulário para adicionar ou editar um Produto.
    Utiliza ModelForm para gerar campos automaticamente a partir do modelo Produto.
    """
    class Meta:
        model = Produto
        # Campos que você quer incluir no formulário.
        # 'adicionado_por' será preenchido automaticamente na view.
        fields = ['nome', 'descricao', 'imagem_url', 'categoria', 'marca']
        # Labels personalizados para melhor apresentação no front-end
        labels = {
            'nome': 'Nome do Produto',
            'descricao': 'Descrição',
            'imagem_url': 'URL da Imagem',
            'categoria': 'Categoria',
            'marca': 'Marca',
        }
        # Widgets personalizados para controle de input (opcional, para melhor UX)
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}), # Torna a descrição uma textarea maior
            'imagem_url': forms.URLInput(attrs={'placeholder': 'Ex: http://example.com/imagem.jpg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opcional: Adiciona classes CSS para estilização (ex: Bootstrap)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Opcional: Torna Categoria e Marca dropdowns com opções reais do banco
        self.fields['categoria'].queryset = Categoria.objects.all().order_by('nome')
        self.fields['marca'].queryset = Marca.objects.all().order_by('nome')
        
        # Opcional: Adiciona uma opção "--------" para campos ForeignKey vazios
        self.fields['categoria'].empty_label = "Selecione uma categoria"
        self.fields['marca'].empty_label = "Selecione uma marca"


class LojaForm(forms.ModelForm):
    """
    Formulário para adicionar ou editar uma Loja.
    """
    class Meta:
        model = Loja
        fields = ['nome', 'url', 'logo_url']
        labels = {
            'nome': 'Nome da Loja',
            'url': 'URL da Loja',
            'logo_url': 'URL do Logo',
        }
        widgets = {
            'url': forms.URLInput(attrs={'placeholder': 'Ex: http://www.minhalojatop.com.br'}),
            'logo_url': forms.URLInput(attrs={'placeholder': 'Ex: http://www.minhalojatop.com.br/logo.png'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class OfertaForm(forms.ModelForm):
    """
    Formulário para adicionar ou editar uma Oferta.
    """
    class Meta:
        model = Oferta
        # Não inclua 'data_captura' pois ela é auto_now_add=True no modelo.
        fields = ['produto', 'loja', 'preco']
        labels = {
            'produto': 'Produto',
            'loja': 'Loja',
            'preco': 'Preço',
        }
        widgets = {
            'preco': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}), # Permite centavos e mínimo 0.01
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Opcional: Popula os dropdowns com opções reais do banco
        self.fields['produto'].queryset = Produto.objects.all().order_by('nome')
        self.fields['loja'].queryset = Loja.objects.all().order_by('nome')

        self.fields['produto'].empty_label = "Selecione um produto"
        self.fields['loja'].empty_label = "Selecione uma loja"