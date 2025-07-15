from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Categoria, Marca, Produto, Loja, Oferta, Usuario, ItemComprado # Importe Usuario explicitamente

from django.db import IntegrityError # Importe para testar unique_together
import decimal # Para lidar com valores DecimalFields

from unittest.mock import patch # Para mockar timezone.now se necessário para testes precisos


class ModelCreationTest(TestCase):
    """
    Testes para a criação e propriedades básicas dos modelos.
    """
    @classmethod
    def setUpTestData(cls):
        # Criar um usuário administrador para associar aos produtos
        cls.admin_user = Usuario.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
            # REMOVIDO: 'role' não é mais um campo no modelo Usuario
        )
        # Criar um usuário normal
        cls.normal_user = Usuario.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpassword',
            first_name='Normal', # Adicionado first_name/last_name para consistência
            last_name='User'
            # REMOVIDO: 'role' não é mais um campo no modelo Usuario
        )

        # Criar categorias e marcas
        cls.categoria_eletronicos = Categoria.objects.create(nome='Eletrônicos')
        cls.marca_samsung = Marca.objects.create(nome='Samsung')
        cls.marca_apple = Marca.objects.create(nome='Apple')
        
        # Criar um produto para uso em ofertas
        cls.produto_base = Produto.objects.create(
            nome='Produto Base para Oferta',
            categoria=cls.categoria_eletronicos,
            adicionado_por=cls.admin_user,
            imagem_url='http://example.com/base_prod.jpg' # Adicionado imagem_url para consistência
        )
        cls.loja_base = Loja.objects.create(nome='Loja Base')

    def test_create_categoria(self):
        initial_count = Categoria.objects.count()
        categoria = Categoria.objects.create(nome='Livros')
        self.assertEqual(categoria.nome, 'Livros')
        self.assertEqual(Categoria.objects.count(), initial_count + 1)
        self.assertTrue(isinstance(categoria, Categoria))
        self.assertEqual(str(categoria), 'Livros')

    def test_create_marca(self):
        initial_count = Marca.objects.count()
        marca = Marca.objects.create(nome='Dell')
        self.assertEqual(marca.nome, 'Dell')
        self.assertEqual(Marca.objects.count(), initial_count + 1)
        self.assertTrue(isinstance(marca, Marca))
        self.assertEqual(str(marca), 'Dell')

    def test_create_product(self):
        product_count_before = Produto.objects.count()
        produto = Produto.objects.create(
            nome='Smartphone Galaxy S23',
            descricao='Celular top de linha da Samsung.',
            imagem_url='http://example.com/galaxy.jpg',
            categoria=self.categoria_eletronicos,
            marca=self.marca_samsung,
            adicionado_por=self.admin_user
        )
        self.assertIsNotNone(produto.id)
        self.assertEqual(Produto.objects.count(), product_count_before + 1)
        self.assertEqual(produto.nome, 'Smartphone Galaxy S23')
        self.assertEqual(produto.descricao, 'Celular top de linha da Samsung.')
        self.assertEqual(produto.imagem_url, 'http://example.com/galaxy.jpg')
        self.assertEqual(produto.categoria, self.categoria_eletronicos)
        self.assertEqual(produto.marca, self.marca_samsung)
        self.assertEqual(produto.adicionado_por, self.admin_user)
        self.assertIsNotNone(produto.data_adicao)
        self.assertTrue(isinstance(produto, Produto))
        self.assertEqual(str(produto), 'Smartphone Galaxy S23')

    def test_create_loja(self):
        loja_count_before = Loja.objects.count()
        loja = Loja.objects.create(
            nome='Magazine Luiza',
            url='http://magazineluiza.com.br',
            logo_url='http://magazineluiza.com.br/logo.png'
        )
        self.assertIsNotNone(loja.id)
        self.assertEqual(Loja.objects.count(), loja_count_before + 1)
        self.assertEqual(loja.nome, 'Magazine Luiza')
        self.assertEqual(loja.url, 'http://magazineluiza.com.br')
        self.assertEqual(loja.logo_url, 'http://magazineluiza.com.br/logo.png')
        self.assertTrue(isinstance(loja, Loja))
        self.assertEqual(str(loja), 'Magazine Luiza')

    def test_create_oferta(self):
        oferta_count_before = Oferta.objects.count()
        oferta = Oferta.objects.create(
            produto=self.produto_base,
            loja=self.loja_base,
            preco=decimal.Decimal('8500.50')
        )
        self.assertIsNotNone(oferta.id)
        self.assertEqual(Oferta.objects.count(), oferta_count_before + 1)
        self.assertEqual(oferta.produto, self.produto_base)
        self.assertEqual(oferta.loja, self.loja_base)
        self.assertEqual(oferta.preco, decimal.Decimal('8500.50'))
        self.assertIsNotNone(oferta.data_captura)
        self.assertTrue(isinstance(oferta, Oferta))
        expected_str = f"Oferta de {self.produto_base.nome} na {self.loja_base.nome} por R$8500.50"
        self.assertEqual(str(oferta), expected_str)


    def test_oferta_unique_together_different_time(self):
        Oferta.objects.create(produto=self.produto_base, loja=self.loja_base, preco=decimal.Decimal('300.00'), data_captura=timezone.now())
        future_time = timezone.now() + timedelta(seconds=1)
        Oferta.objects.create(produto=self.produto_base, loja=self.loja_base, preco=decimal.Decimal('290.00'), data_captura=future_time)
        self.assertEqual(Oferta.objects.filter(produto=self.produto_base, loja=self.loja_base).count(), 2)

    def test_usuario_creation(self):
        user_count_before = Usuario.objects.count()
        user = Usuario.objects.create_user(
            username='newtestuser', email='new@example.com', password='testpassword',
            first_name='Test', last_name='User'
        )
        self.assertIsNotNone(user.id)
        self.assertEqual(Usuario.objects.count(), user_count_before + 1)
        self.assertEqual(user.username, 'newtestuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        # O __str__ deve retornar o full_name ou username
        self.assertEqual(str(user), 'Test User')


    def test_item_comprado(self):
        data_compra_hoje = timezone.localdate()
        itens_comprados_antes = ItemComprado.objects.count()
        iten_comprado = ItemComprado.objects.create(
            preco_pago= decimal.Decimal('8500.50'),
            data_compra= data_compra_hoje,
            produto = self.produto_base,
            loja = self.loja_base,
            usuario=self.normal_user
        )
        self.assertIsNotNone(iten_comprado.id)
        self.assertEqual(ItemComprado.objects.count(), itens_comprados_antes + 1)
        self.assertEqual(iten_comprado.preco_pago, decimal.Decimal('8500.50'))
        self.assertEqual(iten_comprado.data_compra, data_compra_hoje)
        self.assertEqual(iten_comprado.produto, self.produto_base)
        self.assertEqual(iten_comprado.loja, self.loja_base)
        self.assertEqual(iten_comprado.usuario, self.normal_user)
        self.assertTrue(isinstance(iten_comprado, ItemComprado))
        expected_str = f"Compra de {self.produto_base.nome} por {self.normal_user.get_full_name() if self.normal_user.first_name else self.normal_user.username}"
        self.assertEqual(str(iten_comprado), expected_str)