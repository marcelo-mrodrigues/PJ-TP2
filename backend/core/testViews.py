# tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Loja, Produto, Categoria, Marca, Oferta
from datetime import datetime
from decimal import Decimal

Usuario = get_user_model()

class BasicViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username="usuario1", password="senha123", email="u@u.com"
        )

    def test_home_view(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    def test_register_view_get(self):
        response = self.client.get(reverse("core:register"))
        self.assertEqual(response.status_code, 200)

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

    def test_login_view_get(self):
        response = self.client.get(reverse("core:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_view_post_success(self):
        response = self.client.post(reverse("core:login"), {
            "username": "usuario1",
            "password": "senha123"
        })
        self.assertRedirects(response, reverse("core:home"))

    def test_login_view_post_failure(self):
        response = self.client.post(reverse("core:login"), {
            "username": "usuario1",
            "password": "errada"
        })
        self.assertContains(response, "Nome de usuário ou senha inválidos")

    def test_logout_view(self):
        self.client.login(username="usuario1", password="senha123")
        response = self.client.get(reverse("core:logout"))
        self.assertRedirects(response, reverse("core:home"))

class ProtectedViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(username="user", password="senha")
        self.client.login(username="user", password="senha")

    def test_perfil_view(self):
        response = self.client.get(reverse("core:perfil"))
        self.assertEqual(response.status_code, 200)

    def test_lista_de_compras_view(self):
        response = self.client.get(reverse("core:lista_de_compras"))
        self.assertEqual(response.status_code, 200)

    def test_historico_view(self):
        response = self.client.get(reverse("core:historico"))
        self.assertEqual(response.status_code, 200)

class ApiViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(username="u", password="s")
        self.produto = Produto.objects.create(nome="Sabonete")

    def test_product_catalog_view(self):
        response = self.client.get(reverse("core:product_catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("products", response.json())

    def test_get_product_data_api_found(self):
        response = self.client.get(reverse("core:get_product_data_api", args=[self.produto.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("product", response.json())

    def test_get_product_data_api_not_found(self):
        response = self.client.get(reverse("core:get_product_data_api", args=[999]))
        self.assertEqual(response.status_code, 404)

from django.contrib.admin.sites import AdminSite

class ManagementViewsTest(TestCase):
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
        self.oferta = Oferta.objects.create(produto=self.produto, loja=self.loja, preco=5.99)

    def test_manage_stores_view_get(self):
        response = self.client.get(reverse("core:manage_stores"))
        self.assertEqual(response.status_code, 200)

    def test_manage_products_view_get(self):
        response = self.client.get(reverse("core:manage_products"))
        self.assertEqual(response.status_code, 200)

    def test_manage_offers_view_get(self):
        response = self.client.get(reverse("core:manage_offers"))
        self.assertEqual(response.status_code, 200)

    def test_manage_stores_delete(self):
        loja = Loja.objects.create(nome="Apagar")
        response = self.client.post(reverse("core:manage_stores"), {
            "action": "delete",
            "id": loja.id,
        })
        self.assertRedirects(response, reverse("core:manage_stores"))
        self.assertFalse(Loja.objects.filter(id=loja.id).exists())

    def test_manage_products_create(self):
        response = self.client.post(reverse("core:manage_products"), {
            "nome": "Produto Novo",
            "descricao": "desc",
            "imagem_url": "http://img.com/p.png",
            "categoria": self.categoria.id,
            "marca": self.marca.id,
        })
        self.assertEqual(response.status_code, 302)  # redireciona se salvar

    def test_manage_offers_create_invalid(self):
        response = self.client.post(reverse("core:manage_offers"), {
            "produto": "",  # inválido
            "loja": "",
            "preco": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erro ao salvar")


