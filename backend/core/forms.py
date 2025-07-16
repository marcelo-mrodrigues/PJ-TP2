from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import Usuario, Produto, Loja, Oferta, Categoria, Marca, ItemLista, ListaCompra, Comentario


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            if field_name == "email":
                field.required = True


class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulário customizado para autenticação de usuário, permitindo login
    com nome de usuário (username) ou email.
    """

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        # Altera o rótulo do campo 'username' para ser mais genérico
        self.fields["username"].label = "Usuário ou Email"
        # Adiciona a classe 'form-control' para consistência visual
        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["password"].widget.attrs["class"] = "form-control"

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                if "@" in username:
                    try:
                        user_by_email = Usuario.objects.get(email=username)
                        user = authenticate(
                            self.request,
                            username=user_by_email.username,
                            password=password,
                        )
                    except Usuario.DoesNotExist:
                        pass

            if user is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                    params={"username": self.username_field.verbose_name},
                )
            else:
                self.user_cache = user
        return self.cleaned_data


class ProdutoForm(forms.ModelForm):
    product_id_hidden = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Produto
        # CORREÇÃO APLICADA AQUI
        fields = [
            "nome",
            "descricao",
            "imagem_url",
            "categoria",
            "marca",
            "product_id_hidden",
        ]
        labels = {
            "nome": "Nome do Produto",
            "descricao": "Descrição",
            "imagem_url": "URL da Imagem",
            "categoria": "Categoria",
            "marca": "Marca",
        }
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 4}),
            "imagem_url": forms.URLInput(
                attrs={"placeholder": "Ex: http://example.com/imagem.jpg"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
        self.fields["categoria"].queryset = Categoria.objects.all().order_by("nome")
        self.fields["marca"].queryset = Marca.objects.all().order_by("nome")
        self.fields["categoria"].empty_label = "Selecione uma categoria"
        self.fields["marca"].empty_label = "Selecione uma marca"
        if self.instance and self.instance.pk:
            self.fields["product_id_hidden"].initial = self.instance.pk


class LojaForm(forms.ModelForm):
    store_id_hidden = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Loja
        # CORREÇÃO APLICADA AQUI
        fields = ["nome", "url", "logo_url", "store_id_hidden"]
        labels = {
            "nome": "Nome da Loja",
            "url": "URL da Loja",
            "logo_url": "URL do Logo",
        }
        widgets = {
            "url": forms.URLInput(
                attrs={"placeholder": "Ex: http://www.minhaloja.com.br"}
            ),
            "logo_url": forms.URLInput(
                attrs={"placeholder": "Ex: http://www.minhaloja.com.br/logo.png"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
        if self.instance and self.instance.pk:
            self.fields["store_id_hidden"].initial = self.instance.pk


class OfertaForm(forms.ModelForm):
    offer_id_hidden = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Oferta
        fields = ["produto", "loja", "preco", "offer_id_hidden"]
        labels = {"produto": "Produto", "loja": "Loja", "preco": "Preço"}
        widgets = {"preco": forms.NumberInput(attrs={"step": "0.01", "min": "0.01"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
        self.fields["produto"].queryset = Produto.objects.all().order_by("nome")
        self.fields["loja"].queryset = Loja.objects.all().order_by("nome")
        self.fields["produto"].empty_label = "Selecione um produto"
        self.fields["loja"].empty_label = "Selecione uma loja"
        if self.instance and self.instance.pk:
            self.fields["offer_id_hidden"].initial = self.instance.pk


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome"]
        labels = {"nome": "Nome da Categoria"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nome"].widget.attrs["class"] = "form-control"



class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ["nome"]
        labels = {"nome": "Nome da Marca"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nome"].widget.attrs["class"] = "form-control"


class ListaCompraForm(forms.ModelForm):
    class Meta:
        model = ListaCompra
        fields = ["nome", "finalizada"]

class ItemListaForm(forms.ModelForm):
    class Meta:
        model = ItemLista
        fields = ["produto", "observacoes"]

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["texto", "nota"]
        widgets = {
            "texto": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "nota": forms.NumberInput(attrs={"min": 1, "max": 5, "class": "form-control"}),
        }