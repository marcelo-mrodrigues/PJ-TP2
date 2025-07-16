## @file tests/testViews.py
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
# tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Loja, Produto, Categoria, Marca, Oferta, ItemComprado, ListaCompra, ItemLista, Comentario, Usuario
from datetime import datetime
from decimal import Decimal
from django.utils import timezone # Para testar datas em ofertas/compras
import json # Para JsonResponse
from django.contrib.messages import get_messages # Para verificar mensagens após redirecionamento

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
        # Certifique-se de que o Usuario.objects.create_user tem todos os REQUIRED_FIELDS
        self.user = Usuario.objects.create_user(
            username="usuario1", password="senha123", email="u@u.com",
            first_name="User", last_name="One"
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
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Usuário novo registrado com sucesso!", [m.message for m in messages])


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
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Login realizado com sucesso", [m.message for m in messages])


    ## @brief Testa o envio POST de credenciais inválidas para a view de login (`login_view`).
    #
    # Verifica se o login falha e se a mensagem de erro apropriada é exibida.
    def test_login_view_post_failure(self):
        response = self.client.post(reverse("core:login"), {
            "username": "usuario1",
            "password": "errada"
        })
        # Não é um redirecionamento, então o contexto está disponível
        self.assertContains(response, "Nome de usuário ou senha inválidos")

    ## @brief Testa a view de logout (`logout_view`).
    #
    # Verifica se o usuário é deslogado e se há um redirecionamento para a página inicial.
    def test_logout_view(self):
        self.client.login(username="usuario1", password="senha123")
        response = self.client.get(reverse("core:logout"))
        self.assertRedirects(response, reverse("core:home"))
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Você saiu da sua conta com sucesso.", [m.message for m in messages])


## @brief Conjunto de testes para as views protegidas por autenticação.
#
# Inclui testes para as views de perfil, lista de compras e histórico.
class ProtectedViewsTest(TestCase):
    ## @brief Configura o ambiente de teste antes de cada método de teste.
    #
    # Cria um usuário e realiza o login para testar o acesso a views protegidas.
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(username="user", password="senha", email="user@test.com", first_name="Test", last_name="User")
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

    ## @brief Testa o acesso à view de perfil sem login.
    #
    # Verifica se o usuário é redirecionado para a página de login.
    def test_perfil_view_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("core:perfil"))
        self.assertRedirects(response, reverse("core:login") + '?next=/perfil/')

    ## @brief Testa o acesso à view de lista de compras sem login.
    #
    # Verifica se o usuário é redirecionado para a página de login.
    def test_lista_de_compras_view_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("core:lista_de_compras"))
        self.assertRedirects(response, reverse("core:login") + '?next=/lista-de-compras/')

    ## @brief Testa o acesso à view de histórico de compras sem login.
    #
    # Verifica se o usuário é redirecionado para a página de login.
    def test_historico_view_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("core:historico"))
        self.assertRedirects(response, reverse("core:login") + '?next=/historico/')


## @brief Conjunto de testes para as views de API.
#
# Inclui testes para o catálogo de produtos e detalhes de produtos via API.
class ApiViewsTest(TestCase):
    ## @brief Configura o ambiente de teste antes de cada método de teste.
    #
    # Cria um cliente de teste, um usuário e um produto para simular cenários de API.
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(username="u", password="s", email="u@test.com", first_name="U", last_name="Test")
        self.produto = Produto.objects.create(nome="Sabonete", aprovado=True) # Produto aprovado para catálogo
        self.loja = Loja.objects.create(nome="Loja Teste")
        Oferta.objects.create(produto=self.produto, loja=self.loja, preco=Decimal('10.00'))

    ## @brief Testa a view de detalhes de produto via API (`get_product_data_api`) para um produto existente.
    #
    # Verifica se a view retorna um status HTTP 200 (OK) e se a resposta JSON
    # contém a chave 'product'.
    def test_get_product_data_api_found(self):
        response = self.client.get(reverse("core:get_product_data_api", args=[self.produto.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("product", response.json())
        self.assertEqual(response.json()['product']['nome'], 'Sabonete')

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
            username="admin", password="admin123", email="admin@test.com", is_staff=True, first_name="Admin", last_name="User"
        )
        self.normal_user = Usuario.objects.create_user(
            username="normal", password="normal123", email="normal@test.com", is_staff=False, first_name="Normal", last_name="User"
        )
        self.client.login(username="admin", password="admin123")

        self.categoria = Categoria.objects.create(nome="Higiene")
        self.marca = Marca.objects.create(nome="Marca1")
        self.produto = Produto.objects.create(nome="Creme", categoria=self.categoria, marca=self.marca)
        self.loja = Loja.objects.create(nome="Loja1")
        self.oferta = Oferta.objects.create(produto=self.produto, loja=self.loja, preco=Decimal('5.99'))

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
            "action": "delete_store",
            "store_id": loja.id,
        })
        self.assertRedirects(response, reverse("core:manage_stores"))
        self.assertFalse(Loja.objects.filter(id=loja.id).exists())
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn(f"Loja '{loja.nome}' excluída com sucesso!", [m.message for m in messages])

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
        self.assertEqual(response.status_code, 302)
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Produto 'Produto Novo' salvo com sucesso!", [m.message for m in messages])


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

    ## @brief Testa o acesso GET à view de gerenciamento de lojas para edição.
    #
    # Verifica se a view retorna o formulário preenchido com os dados da loja para edição.
    def test_manage_stores_view_edit_get(self):
        response = self.client.post(reverse("core:manage_stores"), {
            "action": "edit_store",
            "store_id": self.loja.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Editando loja: <strong>{self.loja.nome}</strong>")
        self.assertContains(response, self.loja.nome)

    ## @brief Testa o envio POST de dados válidos para edição de loja.
    #
    # Verifica se a loja é atualizada com sucesso e se há um redirecionamento.
    def test_manage_stores_view_edit_post_success(self):
        response = self.client.post(reverse("core:manage_stores"), {
            "action": "add_or_update_store",
            "store_id_hidden": self.loja.id,
            "nome": "Loja Editada",
            "url": "http://editada.com",
        })
        self.assertRedirects(response, reverse("core:manage_stores"))
        self.loja.refresh_from_db()
        self.assertEqual(self.loja.nome, "Loja Editada")
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Loja 'Loja Editada' salva com sucesso!", [m.message for m in messages])


    ## @brief Testa o envio POST de dados inválidos para edição de loja.
    #
    # Verifica se a edição falha e se a mensagem de erro apropriada é exibida.
    def test_manage_stores_view_edit_post_failure(self):
        response = self.client.post(reverse("core:manage_stores"), {
            "action": "add_or_update_store",
            "store_id_hidden": self.loja.id,
            "nome": "", # Nome vazio
            "url": "http://editada.com",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erro no campo 'nome'")
    
    ## @brief Testa o acesso GET à view de gerenciamento de produtos para edição.
    #
    # Verifica se a view retorna o formulário preenchido com os dados do produto para edição.
    def test_manage_products_view_edit_get(self):
        response = self.client.post(reverse("core:manage_products"), {
            "action": "edit",
            "id": self.produto.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Editando o produto: {self.produto.nome}")
        self.assertContains(response, self.produto.nome)

    ## @brief Testa o envio POST de dados válidos para edição de produto.
    #
    # Verifica se o produto é atualizado com sucesso e se há um redirecionamento.
    def test_manage_products_view_edit_post_success(self):
        response = self.client.post(reverse("core:manage_products"), {
            "action": "add_or_update_product",
            "product_id_hidden": self.produto.id,
            "nome": "Produto Editado",
            "descricao": "nova desc",
            "categoria": self.categoria.id,
            "marca": self.marca.id,
        })
        self.assertRedirects(response, reverse("core:manage_products"))
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.nome, "Produto Editado")
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Produto 'Produto Editado' salvo com sucesso!", [m.message for m in messages])


    ## @brief Testa o envio POST de dados inválidos para edição de produto.
    #
    # Verifica se a edição falha e se a mensagem de erro apropriada é exibida.
    def test_manage_products_view_edit_post_failure(self):
        response = self.client.post(reverse("core:manage_products"), {
            "action": "add_or_update_product",
            "product_id_hidden": self.produto.id,
            "nome": "", # Nome vazio
            "categoria": self.categoria.id,
            "marca": self.marca.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erro ao salvar. Verifique os campos.")

    ## @brief Testa a exclusão de um produto inexistente na view de gerenciamento de produtos.
    #
    # Verifica se a view retorna um status 404 (Not Found) quando o ID do produto não existe.
    def test_manage_products_delete_non_existent(self):
        response = self.client.post(reverse("core:manage_products"), {
            "action": "delete",
            "id": 99999, # ID inexistente
        })
        self.assertEqual(response.status_code, 404)

    ## @brief Testa a criação de uma nova oferta via POST na view de gerenciamento de ofertas.
    #
    # Verifica se a oferta é criada com sucesso e se há um redirecionamento.
    def test_manage_offers_create_success(self):
        produto_novo = Produto.objects.create(nome="Produto para Oferta")
        loja_nova = Loja.objects.create(nome="Loja para Oferta")
        response = self.client.post(reverse("core:manage_offers"), {
            "produto": produto_novo.id,
            "loja": loja_nova.id,
            "preco": 19.99,
        })
        self.assertRedirects(response, reverse("core:manage_offers"))
        self.assertTrue(Oferta.objects.filter(produto=produto_novo, loja=loja_nova, preco=Decimal('19.99')).exists())
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Oferta para 'Produto para Oferta' salva com sucesso!", [m.message for m in messages])

    ## @brief Testa o acesso GET à view de gerenciamento de ofertas para edição.
    #
    # Verifica se a view retorna o formulário preenchido com os dados da oferta para edição.
    def test_manage_offers_view_edit_get(self):
        response = self.client.post(reverse("core:manage_offers"), {
            "action": "edit",
            "id": self.oferta.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Editando oferta: {self.oferta}")

    ## @brief Testa o envio POST de dados válidos para edição de oferta.
    #
    # Verifica se a oferta é atualizada com sucesso e se há um redirecionamento.
    def test_manage_offers_view_edit_post_success(self):
        response = self.client.post(reverse("core:manage_offers"), {
            "action": "add_or_update",
            "offer_id_hidden": self.oferta.id,
            "produto": self.produto.id,
            "loja": self.loja.id,
            "preco": 9.99,
        })
        self.assertRedirects(response, reverse("core:manage_offers"))
        self.oferta.refresh_from_db()
        self.assertEqual(self.oferta.preco, Decimal('9.99'))
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Oferta para 'Creme' salva com sucesso!", [m.message for m in messages])

    ## @brief Testa o envio POST de dados inválidos para edição de oferta.
    #
    # Verifica se a edição falha e se a mensagem de erro apropriada é exibida.
    def test_manage_offers_view_edit_post_failure(self):
        response = self.client.post(reverse("core:manage_offers"), {
            "action": "add_or_update",
            "offer_id_hidden": self.oferta.id,
            "produto": self.produto.id,
            "loja": self.loja.id,
            "preco": "", # Preço vazio
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erro ao salvar. Verifique os campos.")

    ## @brief Testa a exclusão de uma oferta via POST na view de gerenciamento de ofertas.
    #
    # Verifica se a oferta é excluída com sucesso e se há um redirecionamento.
    def test_manage_offers_delete_success(self):
        oferta_to_delete = Oferta.objects.create(produto=self.produto, loja=self.loja, preco=1.00)
        response = self.client.post(reverse("core:manage_offers"), {
            "action": "delete",
            "id": oferta_to_delete.id,
        })
        self.assertRedirects(response, reverse("core:manage_offers"))
        self.assertFalse(Oferta.objects.filter(id=oferta_to_delete.id).exists())
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn(f"Oferta '{oferta_to_delete}' excluída com sucesso!", [m.message for m in messages])

    ## @brief Testa o acesso GET à view de gerenciamento de categorias.
    #
    # Verifica se a view retorna um status HTTP 200 (OK) e o template correto.
    def test_manage_categories_view_get(self):
        response = self.client.get(reverse("core:manage_categories"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/manage_generico.html")
        self.assertContains(response, "Gerenciar Categorias")

    ## @brief Testa a criação de uma nova categoria via POST.
    #
    # Verifica se a categoria é criada com sucesso e se há um redirecionamento.
    def test_manage_categories_view_create_success(self):
        response = self.client.post(reverse("core:manage_categories"), {
            "action": "add_or_update", # Ação padrão
            "nome": "NovaCategoria",
        })
        self.assertRedirects(response, reverse("core:manage_categories"))
        self.assertTrue(Categoria.objects.filter(nome="NovaCategoria").exists())
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Categoria salva com sucesso!", [m.message for m in messages])

    ## @brief Testa o envio de dados inválidos para criação de categoria.
    #
    # Verifica se a criação falha e se a mensagem de erro é exibida.
    def test_manage_categories_view_create_failure(self):
        response = self.client.post(reverse("core:manage_categories"), {
            "action": "add_or_update",
            "nome": "", # Nome vazio
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erro ao salvar categoria.")

    ## @brief Testa o acesso GET à view de gerenciamento de categorias para edição.
    #
    # Verifica se a view retorna o formulário preenchido com os dados da categoria.
    def test_manage_categories_view_edit_get(self):
        categoria_edit = Categoria.objects.create(nome="CategoriaEdit")
        response = self.client.post(reverse("core:manage_categories"), {
            "action": "edit",
            "id": categoria_edit.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Editando categoria: <strong>{categoria_edit.nome}</strong>")

    ## @brief Testa o envio POST de dados válidos para edição de categoria.
    #
    # Verifica se a categoria é atualizada com sucesso e se há um redirecionamento.
    def test_manage_categories_view_edit_post_success(self):
        categoria_edit = Categoria.objects.create(nome="CategoriaOriginal")
        response = self.client.post(reverse("core:manage_categories"), {
            "action": "add_or_update",
            "id": categoria_edit.id,
            "nome": "CategoriaAtualizada",
        })
        self.assertRedirects(response, reverse("core:manage_categories"))
        categoria_edit.refresh_from_db()
        self.assertEqual(categoria_edit.nome, "CategoriaAtualizada")
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Categoria salva com sucesso!", [m.message for m in messages])

    ## @brief Testa a exclusão de uma categoria via POST.
    #
    # Verifica se a categoria é excluída com sucesso e se há um redirecionamento.
    def test_manage_categories_view_delete_success(self):
        categoria_delete = Categoria.objects.create(nome="CategoriaDelete")
        response = self.client.post(reverse("core:manage_categories"), {
            "action": "delete",
            "id": categoria_delete.id,
        })
        self.assertRedirects(response, reverse("core:manage_categories"))
        self.assertFalse(Categoria.objects.filter(id=categoria_delete.id).exists())
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Categoria excluída com sucesso!", [m.message for m in messages])


    ## @brief Testa o acesso GET à view de gerenciamento de marcas.
    #
    # Verifica se a view retorna um status HTTP 200 (OK) e o template correto.
    def test_manage_brands_view_get(self):
        response = self.client.get(reverse("core:manage_brands"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/manage_generico.html")
        self.assertContains(response, "Gerenciar Marcas")

    ## @brief Testa a criação de uma nova marca via POST.
    #
    # Verifica se a marca é criada com sucesso e se há um redirecionamento.
    def test_manage_brands_view_create_success(self):
        response = self.client.post(reverse("core:manage_brands"), {
            "action": "add_or_update",
            "nome": "NovaMarca",
        })
        self.assertRedirects(response, reverse("core:manage_brands"))
        self.assertTrue(Marca.objects.filter(nome="NovaMarca").exists())
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Marca salva com sucesso!", [m.message for m in messages])

    ## @brief Testa o envio de dados inválidos para criação de marca.
    #
    # Verifica se a criação falha e se a mensagem de erro é exibida.
    def test_manage_brands_view_create_failure(self):
        response = self.client.post(reverse("core:manage_brands"), {
            "action": "add_or_update",
            "nome": "", # Nome vazio
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erro ao salvar marca.")

    ## @brief Testa o acesso GET à view de gerenciamento de marcas para edição.
    #
    # Verifica se a view retorna o formulário preenchido com os dados da marca.
    def test_manage_brands_view_edit_get(self):
        marca_edit = Marca.objects.create(nome="MarcaEdit")
        response = self.client.post(reverse("core:manage_brands"), {
            "action": "edit",
            "id": marca_edit.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Editando marca: <strong>{marca_edit.nome}</strong>")

    ## @brief Testa o envio POST de dados válidos para edição de marca.
    #
    # Verifica se a marca é atualizada com sucesso e se há um redirecionamento.
    def test_manage_brands_view_edit_post_success(self):
        marca_edit = Marca.objects.create(nome="MarcaOriginal")
        response = self.client.post(reverse("core:manage_brands"), {
            "action": "add_or_update",
            "id": marca_edit.id,
            "nome": "MarcaAtualizada",
        })
        self.assertRedirects(response, reverse("core:manage_brands"))
        marca_edit.refresh_from_db()
        self.assertEqual(marca_edit.nome, "MarcaAtualizada")
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Marca salva com sucesso!", [m.message for m in messages])

    ## @brief Testa a exclusão de uma marca via POST.
    #
    # Verifica se a marca é excluída com sucesso e se há um redirecionamento.
    def test_manage_brands_view_delete_success(self):
        marca_delete = Marca.objects.create(nome="MarcaDelete")
        response = self.client.post(reverse("core:manage_brands"), {
            "action": "delete",
            "id": marca_delete.id,
        })
        self.assertRedirects(response, reverse("core:manage_brands"))
        self.assertFalse(Marca.objects.filter(id=marca_delete.id).exists())
        # Verificar mensagem após redirecionamento
        follow_response = self.client.get(response.url)
        messages = list(get_messages(follow_response.wsgi_request))
        self.assertIn("Marca excluída com sucesso!", [m.message for m in messages])

    ## @brief Testa o envio POST de dados inválidos para adicionar um comentário.
    #
    # Verifica se a adição falha e se a mensagem de erro é exibida.
    def test_produto_view_post_add_comment_invalid(self):
        self.client.login(username="u", password="s")
        response = self.client.post(reverse("core:produto", args=[self.produto.id]), {
            "action": "add_comentario",
            "texto": "", # Texto vazio
            "nota": 5,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo é obrigatório.")

    ## @brief Testa o acesso GET à view de gerenciamento de listas de compras.
    #
    # Verifica se a view retorna um status HTTP 200 (OK) e o template correto.
    def test_manage_shopping_lists_view_get(self):
        self.client.login(username="u", password="s")
        response = self.client.get(reverse("core:manage_shopping_lists"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/manage_listas.html")
        self.assertIn('form_lista', response.context)
        self.assertIn('form_item', response.context)
        self.assertIn('listas', response.context)

    ## @brief Testa o envio de dados inválidos para adição de lista de compras.
    #
    # Verifica se a criação falha e se a mensagem de erro é exibida.
    def test_manage_shopping_lists_view_add_lista_post_failure(self):
        self.client.login(username="u", password="s")
        response = self.client.post(reverse("core:manage_shopping_lists"), {
            "action": "add_lista",
            "nome": "", # Nome vazio
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo é obrigatório.")