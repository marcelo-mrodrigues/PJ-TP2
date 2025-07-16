## @file tests/test_views.py
#
# @brief Contém testes de unidade para as views do aplicativo 'core' do Django.
#
# Este arquivo testa o comportamento das views, incluindo:
# - Views básicas de navegação (home, registro, login, logout).
# - Views protegidas que exigem autenticação (perfil, listas de compras, histórico).
# - Views de API (catálogo de produtos, detalhes de produto).
# - Views de gerenciamento que exigem permissões de staff (lojas, produtos, ofertas).
#
# Utiliza o `django.test.TestCase` e `django.test.Client` para simular
# requisições HTTP e verificar respostas, redirecionamentos e uso de templates.
#
# @see core.views
# @see core.models
# @see core.forms

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Loja, Produto, Categoria, Marca, Oferta
from datetime import datetime
from decimal import Decimal

## Obtém o modelo de usuário ativo do Django.
Usuario = get_user_model()

## @brief Conjunto de testes para as views básicas do aplicativo.
#
# Inclui testes para as views de página inicial, registro, login e logout.
class BasicViewsTest(TestCase):
    ## @brief Configura o ambiente de teste antes de cada método de teste.
    #
    # Cria uma instância de `Client` para simular requisições HTTP
    # e um usuário básico para testes de login/logout.
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username="usuario1", password="senha123", email="u@u.com"
        )

    ## @brief Testa a view da página inicial (`home_view`).
    #
    # Verifica se a view retorna um status HTTP 200 (OK) e se o template correto é utilizado.
    def test_home_view(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    ## @brief Testa o acesso GET à view de registro (`register_view`).
    #
    # Verifica se a view retorna um status HTTP 200 (OK) ao exibir o formulário de registro.
    def test_register_view_get(self):
        response = self.client.get(reverse("core:register"))
        self.assertEqual(response.status_code, 200)

    ## @brief Testa o envio POST de dados válidos para a view de registro (`register_view`).
    #
    # Verifica se um novo usuário é criado com sucesso e se há um redirecionamento para a página de login.
    def test_register_view_post(self):
        response = self.client.post(reverse("core:register"), {
            "username": "novo",
            "email": "novo@email.com",
            "first_name": "Novo",
            "last_name": "Usuário",
            "password1": "SenhaTest123",
            "password2": "SenhaTest123",
        })
        self.assertRedirects(response, reverse("core:login"))
        self.assertTrue(Usuario.objects.filter(username="novo").exists())

    ## @brief Testa o acesso GET à view de login (`login_view`).
    #
    # Verifica se a view retorna um status HTTP 200 (OK) ao exibir o formulário de login.
    def test_login_view_get(self):
        response = self.client.get(reverse("core:login"))
        self.assertEqual(response.status_code, 200)

    ## @brief Testa o envio POST de credenciais válidas para a view de login (`login_view`).
    #
    # Verifica se o login é bem-sucedido e se há um redirecionamento para a página inicial.
    def test_login_view_post_success(self):
        response = self.client.post(reverse("core:login"), {
            "username": "usuario1",
            "password": "senha123"
        })
        self.assertRedirects(response, reverse("core:home"))

    ## @brief Testa o envio POST de credenciais inválidas para a view de login (`login_view`).
    #
    # Verifica se o login falha e se a mensagem de erro apropriada é exibida.
    def test_login_view_post_failure(self):
        response = self.client.post(reverse("core:login"), {
            "username": "usuario1",
            "password": "errada"
        })
        self.assertContains(response, "Nome de usuário ou senha inválidos")

    ## @brief Testa a view de logout (`logout_view`).
    #
    # Verifica se o usuário é deslogado e se há um redirecionamento para a página inicial.
    def test_logout_view(self):
        self.client.login(username="usuario1", password="senha123")
        response = self.client.get(reverse("core:logout"))
        self.assertRedirects(response, reverse("core:home"))

## @brief Conjunto de testes para as views protegidas por autenticação.
#
# Inclui testes para as views de perfil, lista de compras e histórico.
class ProtectedViewsTest(TestCase):
    ## @brief Configura o ambiente de teste antes de cada método de teste.
    #
    # Cria um usuário e realiza o login para testar o acesso a views protegidas.
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(username="user", password="senha")
        self.client.login(username="user", password="senha")

    ## @brief Testa o acesso à view de perfil (`perfil_view`).
    #
    # Verifica se a view retorna um status HTTP 200 (OK) para um usuário logado.
    def test_perfil_view(self):
        response = self.client.get(reverse("core:perfil"))
        self.assertEqual(response.status_code, 200)

    ## @brief Testa o acesso à view de lista de compras (`lista_de_compras_view`).
    #
    # Verifica se a view retorna um status HTTP 200 (OK) para um usuário logado.
    def test_lista_de_compras_view(self):
        response = self.client.get(reverse("core:lista_de_compras"))
        self.assertEqual(response.status_code, 200)

    ## @brief Testa o acesso à view de histórico de compras (`historico_view`).
    #
    # Verifica se a view retorna um status HTTP 200 (OK) para um usuário logado.
    def test_historico_view(self):
        response = self.client.get(reverse("core:historico"))
        self.assertEqual(response.status_code, 200)

## @brief Conjunto de testes para as views de API.
#
# Inclui testes para o catálogo de produtos e detalhes de produtos via API.
class ApiViewsTest(TestCase):
    ## @brief Configura o ambiente de teste antes de cada método de teste.
    #
    # Cria um cliente de teste, um usuário e um produto para simular cenários de API.
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(username="u", password="s")
        self.produto = Produto.objects.create(nome="Sabonete")

    ## @brief Testa a view de catálogo de produtos via API (`product_catalog_view`).
    #
    # Verifica se a view retorna um status HTTP 200 (OK) e se a resposta JSON
    # contém a chave 'products'.
    def test_product_catalog_view(self):
        response = self.client.get(reverse("core:product_catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("products", response.json())

    ## @brief Testa a view de detalhes de produto via API (`get_product_data_api`) para um produto existente.
    #
    # Verifica se a view retorna um status HTTP 200 (OK) e se a resposta JSON
    # contém a chave 'product'.
    def test_get_product_data_api_found(self):
        response = self.client.get(reverse("core:get_product_data_api", args=[self.produto.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("product", response.json())

    ## @brief Testa a view de detalhes de produto via API (`get_product_data_api`) para um produto não existente.
    #
    # Verifica se a view retorna um status HTTP 404 (Not Found) para um ID de produto inválido.
    def test_get_product_data_api_not_found(self):
        response = self.client.get(reverse("core:get_product_data_api", args=[999]))
        self.assertEqual(response.status_code, 404)

## @brief Conjunto de testes para as views de gerenciamento (requerem staff).
#
# Inclui testes para as views de gerenciamento de lojas, produtos e ofertas.
class ManagementViewsTest(TestCase):
    ## @brief Configura o ambiente de teste antes de cada método de teste.
    #
    # Cria um cliente de teste, um usuário staff (administrador) e realiza o login.
    # Também cria instâncias de modelos (Categoria, Marca, Produto, Loja, Oferta)
    # para uso nos testes de gerenciamento.
    def setUp(self):
        self.client = Client()
        self.staff_user = Usuario.objects.create_user(
            username="admin", password="admin123", is_staff=True
        )
        self.client.login(username="admin", password="admin123")

        self.categoria = Categoria.objects.create(nome="Higiene")
        self.marca = Marca.objects.create(nome="Marca1")
        self.produto = Produto.objects.create(nome="Creme", categoria=self.categoria, marca=self.marca)
        self.loja = Loja.objects.create(nome="Loja1")
        self.oferta = Oferta.objects.create(produto=self.produto, loja=self.loja, preco=Decimal('5.99')) # Usar Decimal

    ## @brief Testa o acesso GET à view de gerenciamento de lojas (`manage_stores_view`).
    #
    # Verifica se a view retorna um status HTTP 200 (OK) para um usuário staff.
    def test_manage_stores_view_get(self):
        response = self.client.get(reverse("core:manage_stores"))
        self.assertEqual(response.status_code, 200)

    ## @brief Testa o acesso GET à view de gerenciamento de produtos (`manage_products_view`).
    #
    # Verifica se a view retorna um status HTTP 200 (OK) para um usuário staff.
    def test_manage_products_view_get(self):
        response = self.client.get(reverse("core:manage_products"))
        self.assertEqual(response.status_code, 200)

    ## @brief Testa o acesso GET à view de gerenciamento de ofertas (`manage_offers_view`).
    #
    # Verifica se a view retorna um status HTTP 200 (OK) para um usuário staff.
    def test_manage_offers_view_get(self):
        response = self.client.get(reverse("core:manage_offers"))
        self.assertEqual(response.status_code, 200)

    ## @brief Testa a exclusão de uma loja via POST na view de gerenciamento de lojas.
    #
    # Cria uma loja, envia uma requisição POST para excluí-la e verifica o redirecionamento
    # e se a loja foi realmente removida do banco de dados.
    def test_manage_stores_delete(self):
        loja = Loja.objects.create(nome="Apagar")
        response = self.client.post(reverse("core:manage_stores"), {
            "action": "delete",
            "id": loja.id,
        })
        self.assertRedirects(response, reverse("core:manage_stores"))
        self.assertFalse(Loja.objects.filter(id=loja.id).exists())

    ## @brief Testa a criação de um novo produto via POST na view de gerenciamento de produtos.
    #
    # Envia uma requisição POST com dados de um novo produto e verifica se há um redirecionamento,
    # indicando que o produto foi salvo com sucesso.
    def test_manage_products_create(self):
        response = self.client.post(reverse("core:manage_products"), {
            "nome": "Produto Novo",
            "descricao": "desc",
            "imagem_url": "http://img.com/p.png",
            "categoria": self.categoria.id,
            "marca": self.marca.id,
        })
        self.assertEqual(response.status_code, 302)  # redireciona se salvar

    ## @brief Testa o envio de dados inválidos para a criação de oferta na view de gerenciamento de ofertas.
    #
    # Envia uma requisição POST com dados incompletos ou inválidos para uma oferta
    # e verifica se a view retorna um status 200 (OK) e contém a mensagem de erro.
    def test_manage_offers_create_invalid(self):
        response = self.client.post(reverse("core:manage_offers"), {
            "produto": "",  # inválido
            "loja": "",
            "preco": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erro ao salvar")
