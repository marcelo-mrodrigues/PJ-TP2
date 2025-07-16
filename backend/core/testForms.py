## @file tests/test_forms.py
#
# @brief Contém testes de unidade para os formulários customizados do aplicativo 'core'.
#
# Este arquivo utiliza o framework de testes `unittest` do Django para
# verificar a funcionalidade e o comportamento dos formulários de criação de usuário,
# autenticação de usuário e formulários relacionados a produtos (Produto, Loja, Oferta, Categoria).
#
# @see core.forms
# @see core.models

from django.test import TestCase
from core.forms import CustomUserCreationForm, CustomAuthenticationForm
from core.models import Usuario, Categoria, Marca, Produto, Loja, Categoria, Oferta
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from core.forms import ProdutoForm, LojaForm, OfertaForm, CategoriaForm

## Obtém o modelo de usuário ativo do Django.
User = get_user_model()

## @brief Conjunto de testes para o formulário CustomUserCreationForm.
#
# Testa a criação de usuários com dados válidos, campos ausentes e senhas incompatíveis.
class CustomUserCreationFormTests(TestCase):
    ## @brief Testa a validade do formulário com dados de usuário completos e válidos.
    #
    # Verifica se o formulário é válido e se o usuário é salvo corretamente no banco de dados,
    # incluindo email, nome e verificação de senha.
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

    ## @brief Testa a validação do formulário quando o campo de e-mail está ausente.
    #
    # Verifica se o formulário é inválido e se há um erro associado ao campo 'email'.
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

    ## @brief Testa a validação do formulário quando as senhas não correspondem.
    #
    # Verifica se o formulário é inválido e se há um erro no campo 'password2'.
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

## @brief Conjunto de testes para o formulário CustomAuthenticationForm.
#
# Testa o processo de login de usuários com diferentes cenários de credenciais.
class CustomAuthenticationFormTests(TestCase):
    ## @brief Configura o ambiente de teste antes de cada método de teste.
    #
    # Cria uma instância de RequestFactory e um usuário de teste para simular requisições.
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="usuario_teste",
            email="teste@example.com",
            first_name="Test",
            last_name="User",
            password="senha123"
        )
    ## @brief Testa o login bem-sucedido usando o nome de usuário.
    #
    # Verifica se o formulário é válido e se retorna o usuário correto.
    def test_login_with_username(self):
        form = CustomAuthenticationForm(
            request=self.factory.post("/login/"),
            data={"username": "usuario_teste", "password": "senha123"}
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    ## @brief Testa o login com um nome de usuário não encontrado.
    #
    # Verifica se o formulário é inválido e se um erro geral é retornado.
    def test_login_with_username_not_found(self):
        form = CustomAuthenticationForm(
            request=self.factory.post("/login/"),
            data={"username": "usuario_inexistente", "password": "senha123"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
 

    ## @brief Testa o login bem-sucedido usando o e-mail (funcionalidade customizada).
    #
    # Verifica se o formulário é válido e se retorna o usuário correto ao logar com e-mail.
    def test_login_with_email(self):
        form = CustomAuthenticationForm(
            request=self.factory.post("/login/"),
            data={"username": "teste@example.com", "password": "senha123"}
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    ## @brief Testa o login com credenciais inválidas (nome de usuário ou senha incorretos).
    #
    # Verifica se o formulário é inválido e se um erro geral é retornado.
    def test_login_invalid_credentials(self):
        form = CustomAuthenticationForm(
            request=self.factory.post("/login/"),
            data={"username": "usuario_teste", "password": "senha_errada"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)


## @brief Conjunto de testes para o formulário ProdutoForm.
#
# Testa a inicialização e os atributos dos campos do formulário Produto.
class ProdutoFormTest(TestCase):
    ## @brief Configura o ambiente de teste antes de cada método de teste.
    #
    # Cria instâncias de Categoria, Marca e Produto para uso nos testes.
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
    ## @brief Testa se os campos do formulário possuem a classe 'form-control'.
    #
    # Verifica se a classe CSS 'form-control' é aplicada a todos os widgets dos campos.
    def test_form_fields_have_form_control_class(self):
        form = ProdutoForm()
        for field in form.fields.values():
            self.assertIn("form-control", field.widget.attrs.get("class", ""))

    ## @brief Testa os querysets e rótulos vazios dos campos 'categoria' e 'marca'.
    #
    # Verifica se os querysets incluem as instâncias criadas e se os rótulos de seleção estão corretos.
    def test_categoria_e_marca_querysets_and_labels(self):
        form = ProdutoForm()
        self.assertIn(self.cat, form.fields["categoria"].queryset)
        self.assertIn(self.marca, form.fields["marca"].queryset)
        self.assertEqual(form.fields["categoria"].empty_label, "Selecione uma categoria")
        self.assertEqual(form.fields["marca"].empty_label, "Selecione uma marca")
    
    ## @brief Testa o valor inicial do campo oculto 'product_id_hidden'.
    #
    # Verifica se o campo oculto é inicializado corretamente com a chave primária do produto.
    def test_product_id_hidden_initial(self):
        form = ProdutoForm(instance=self.produto)
        self.assertEqual(form.fields["product_id_hidden"].initial, self.produto.pk)
    
## @brief Conjunto de testes para o formulário LojaForm.
#
# Testa a inicialização e os atributos dos campos do formulário Loja.
class LojaFormTest(TestCase):
    ## @brief Configura o ambiente de teste antes de cada método de teste.
    #
    # Cria uma instância de Loja para uso nos testes.
    def setUp(self):
        self.loja = Loja.objects.create(
            nome="Loja Teste",
            url="http://lojinha.com",
            logo_url="http://lojinha.com/logo.png"
        )

    ## @brief Testa se os campos do formulário possuem a classe 'form-control'.
    #
    # Verifica se a classe CSS 'form-control' é aplicada a todos os widgets dos campos.
    def test_form_fields_have_form_control_class(self):
        form = LojaForm()
        for field in form.fields.values():
            self.assertIn("form-control", field.widget.attrs.get("class", ""))

    ## @brief Testa o valor inicial do campo oculto 'store_id_hidden'.
    #
    # Verifica se o campo oculto é inicializado corretamente com a chave primária da loja.
    def test_store_id_hidden_initial(self):
        form = LojaForm(instance=self.loja)
        self.assertEqual(form.fields["store_id_hidden"].initial, self.loja.pk)

## @brief Conjunto de testes para o formulário OfertaForm.
#
# Testa a inicialização e os atributos dos campos do formulário Oferta.
class OfertaFormTest(TestCase):
    ## @brief Configura o ambiente de teste antes de cada método de teste.
    #
    # Cria instâncias de Produto, Loja e Oferta para uso nos testes.
    def setUp(self):
        self.produto = Produto.objects.create(nome="Produto Y")
        self.loja = Loja.objects.create(nome="Loja Z")
        self.oferta = Oferta.objects.create(produto=self.produto, loja=self.loja, preco=99.99)
    
    ## @brief Testa se os campos do formulário possuem a classe 'form-control'.
    #
    # Verifica se a classe CSS 'form-control' é aplicada a todos os widgets dos campos.
    def test_form_fields_have_form_control_class(self):
        form = OfertaForm()
        for field in form.fields.values():
            self.assertIn("form-control", field.widget.attrs.get("class", ""))

    ## @brief Testa os querysets e rótulos vazios dos campos 'produto' e 'loja'.
    #
    # Verifica se os querysets incluem as instâncias criadas e se os rótulos de seleção estão corretos.
    def test_produto_e_loja_querysets_and_labels(self):
        form = OfertaForm()
        self.assertIn(self.produto, form.fields["produto"].queryset)
        self.assertIn(self.loja, form.fields["loja"].queryset)
        self.assertEqual(form.fields["produto"].empty_label, "Selecione um produto")
        self.assertEqual(form.fields["loja"].empty_label, "Selecione uma loja")

    ## @brief Testa o valor inicial do campo oculto 'offer_id_hidden'.
    #
    # Verifica se o campo oculto é inicializado corretamente com a chave primária da oferta.
    def test_offer_id_hidden_initial(self):
        form = OfertaForm(instance=self.oferta)
        self.assertEqual(form.fields["offer_id_hidden"].initial, self.oferta.pk)

## @brief Conjunto de testes para o formulário CategoriaForm.
#
# Testa a inicialização e os atributos dos campos do formulário Categoria.
class CategoriaFormTest(TestCase):
    ## @brief Testa se o campo 'nome' do formulário possui a classe 'form-control'.
    #
    # Verifica se a classe CSS 'form-control' é aplicada ao widget do campo 'nome'.
    def test_nome_field_has_form_control_class(self):
        form = CategoriaForm()
        self.assertIn("form-control", form.fields["nome"].widget.attrs.get("class", ""))