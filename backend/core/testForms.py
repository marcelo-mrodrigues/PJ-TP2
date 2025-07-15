from django.test import TestCase
from core.forms import CustomUserCreationForm, CustomAuthenticationForm
from core.models import Usuario, Categoria, Marca, Produto, Loja, Categoria, Oferta
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from core.forms import ProdutoForm, LojaForm, OfertaForm, CategoriaForm


User = get_user_model()
class CustomUserCreationFormTests(TestCase):
    def test_form_valid_data(self):
        form = CustomUserCreationForm(data={
            "username": "usuario1",
            "first_name": "Fulano",
            "last_name": "Silva",
            "email": "fulano@example.com",
            "password1": "SenhaSegura123",
            "password2": "SenhaSegura123",
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, "fulano@example.com")
        self.assertEqual(user.first_name, "Fulano")
        self.assertTrue(user.check_password("SenhaSegura123"))

    def test_form_missing_email(self):
        form = CustomUserCreationForm(data={
            "username": "usuario2",
            "first_name": "Ciclano",
            "last_name": "Souza",
            "password1": "SenhaSegura123",
            "password2": "SenhaSegura123",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_password_mismatch(self):
        form = CustomUserCreationForm(data={
            "username": "usuario3",
            "first_name": "Beltrano",
            "last_name": "Pereira",
            "email": "beltrano@example.com",
            "password1": "Senha123",
            "password2": "SenhaDiferente123",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

User = get_user_model()

class CustomAuthenticationFormTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="usuario_teste",
            email="teste@example.com",
            first_name="Test",
            last_name="User",
            password="senha123"
        )

    def test_login_with_username(self):
        form = CustomAuthenticationForm(
            request=self.factory.post("/login/"),
            data={"username": "usuario_teste", "password": "senha123"}
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_login_with_username_not_found(self):
        form = CustomAuthenticationForm(
            request=self.factory.post("/login/"),
            data={"username": "usuario_inexistente", "password": "senha123"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
 

    def test_login_with_email(self):
        form = CustomAuthenticationForm(
            request=self.factory.post("/login/"),
            data={"username": "teste@example.com", "password": "senha123"}
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_login_invalid_credentials(self):
        form = CustomAuthenticationForm(
            request=self.factory.post("/login/"),
            data={"username": "usuario_teste", "password": "senha_errada"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)



class ProdutoFormTest(TestCase):
    def setUp(self):
        self.cat = Categoria.objects.create(nome="Eletrônicos")
        self.marca = Marca.objects.create(nome="MarcaX")
        self.produto = Produto.objects.create(
            nome="Celular",
            descricao="Smartphone",
            imagem_url="http://imagem.com/img.jpg",
            categoria=self.cat,
            marca=self.marca,
        )

    def test_form_fields_have_form_control_class(self):
        form = ProdutoForm()
        for field in form.fields.values():
            self.assertIn("form-control", field.widget.attrs.get("class", ""))

    def test_categoria_e_marca_querysets_and_labels(self):
        form = ProdutoForm()
        self.assertIn(self.cat, form.fields["categoria"].queryset)
        self.assertIn(self.marca, form.fields["marca"].queryset)
        self.assertEqual(form.fields["categoria"].empty_label, "Selecione uma categoria")
        self.assertEqual(form.fields["marca"].empty_label, "Selecione uma marca")

    def test_product_id_hidden_initial(self):
        form = ProdutoForm(instance=self.produto)
        self.assertEqual(form.fields["product_id_hidden"].initial, self.produto.pk)
    

class LojaFormTest(TestCase):
    def setUp(self):
        self.loja = Loja.objects.create(
            nome="Loja Teste",
            url="http://lojinha.com",
            logo_url="http://lojinha.com/logo.png"
        )

    def test_form_fields_have_form_control_class(self):
        form = LojaForm()
        for field in form.fields.values():
            self.assertIn("form-control", field.widget.attrs.get("class", ""))

    def test_store_id_hidden_initial(self):
        form = LojaForm(instance=self.loja)
        self.assertEqual(form.fields["store_id_hidden"].initial, self.loja.pk)

class OfertaFormTest(TestCase):
    def setUp(self):
        self.produto = Produto.objects.create(nome="Produto Y")
        self.loja = Loja.objects.create(nome="Loja Z")
        self.oferta = Oferta.objects.create(produto=self.produto, loja=self.loja, preco=99.99)

    def test_form_fields_have_form_control_class(self):
        form = OfertaForm()
        for field in form.fields.values():
            self.assertIn("form-control", field.widget.attrs.get("class", ""))

    def test_produto_e_loja_querysets_and_labels(self):
        form = OfertaForm()
        self.assertIn(self.produto, form.fields["produto"].queryset)
        self.assertIn(self.loja, form.fields["loja"].queryset)
        self.assertEqual(form.fields["produto"].empty_label, "Selecione um produto")
        self.assertEqual(form.fields["loja"].empty_label, "Selecione uma loja")

    def test_offer_id_hidden_initial(self):
        form = OfertaForm(instance=self.oferta)
        self.assertEqual(form.fields["offer_id_hidden"].initial, self.oferta.pk)


class CategoriaFormTest(TestCase):
    def test_nome_field_has_form_control_class(self):
        form = CategoriaForm()
        self.assertIn("form-control", form.fields["nome"].widget.attrs.get("class", ""))