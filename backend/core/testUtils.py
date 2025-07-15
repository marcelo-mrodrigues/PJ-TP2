# core/testUtils.py

from django.test import TestCase
from django.utils import timezone 
from datetime import timedelta 
import datetime # Importar datetime para criar objetos datetime concretos
from .models import Categoria, Marca, Produto, Loja, Oferta, Usuario 
import decimal 
from unittest.mock import patch 

# Importa as funções do seu arquivo utils.py
from .utils import get_product_info, search_products


class ProductInfoUtilsTest(TestCase):
    """
    Testes para as funções utilitárias que interagem com o ORM:
    get_product_info e search_products.
    """
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = Usuario.objects.create_user(
            username='testadmin', email='test@example.com', password='password',
            first_name='Test', last_name='Admin', is_staff=True, is_superuser=True
        )
        cls.normal_user = Usuario.objects.create_user(
            username='testuser', email='user@example.com', password='password',
            first_name='Test', last_name='User'
        )

        cls.categoria_eletronicos = Categoria.objects.create(nome='Eletrônicos')
        cls.categoria_livros = Categoria.objects.create(nome='Livros')
        cls.marca_sony = Marca.objects.create(nome='Sony')
        cls.marca_logitech = Marca.objects.create(nome='Logitech')

        cls.loja_a = Loja.objects.create(nome='Loja A', url='http://loja_a.com')
        cls.loja_b = Loja.objects.create(nome='Loja B', url='http://loja_b.com')

        # --- Produto com ofertas ---
        cls.produto_com_ofertas = Produto.objects.create(
            nome='Console de Videogame',
            descricao='Console de última geração para jogos.',
            imagem_url='http://img.com/console.jpg',
            categoria=cls.categoria_eletronicos,
            marca=cls.marca_sony,
            adicionado_por=cls.admin_user
        )
        
        # === CORREÇÃO AQUI: Usar datetime.timezone.utc para o tzinfo ===
        with patch('django.utils.timezone.now') as mock_now:
            # Para a primeira oferta
            mock_now.return_value = datetime.datetime(2025, 7, 14, 10, 0, 0, tzinfo=datetime.timezone.utc)
            Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja_b, preco=decimal.Decimal('2500.00'))

            # Para a segunda oferta
            mock_now.return_value = datetime.datetime(2025, 7, 14, 10, 5, 0, tzinfo=datetime.timezone.utc) # 5 minutos depois
            Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja_a, preco=decimal.Decimal('2300.00')) # Menor preço

            # Para a terceira oferta
            mock_now.return_value = datetime.datetime(2025, 7, 14, 10, 10, 0, tzinfo=datetime.timezone.utc) # 10 minutos depois
            Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja_b, preco=decimal.Decimal('2400.00'))

        # --- Produto sem ofertas ---
        cls.produto_sem_ofertas = Produto.objects.create(
            nome='Livro de Programação',
            descricao='Guia completo para desenvolvimento web.',
            imagem_url='http://img.com/livro.jpg',
            categoria=cls.categoria_livros,
            adicionado_por=cls.normal_user
        )

        # --- Produto para busca ---
        cls.produto_mouse = Produto.objects.create(
            nome='Mouse Gamer Wireless',
            descricao='Mouse ergonômico para jogos e produtividade.',
            imagem_url='http://img.com/mouse.jpg',
            categoria=cls.categoria_eletronicos,
            marca=cls.marca_logitech,
            adicionado_por=cls.admin_user
        )
        Oferta.objects.create(produto=cls.produto_mouse, loja=cls.loja_a, preco=decimal.Decimal('150.00'))

    def test_get_product_info_existing_product(self):
        product_info = get_product_info(self.produto_com_ofertas.id)
        self.assertIsNotNone(product_info)
        self.assertEqual(product_info['id'], self.produto_com_ofertas.id)
        self.assertEqual(product_info['name'], 'Console de Videogame')
        self.assertEqual(product_info['imageUrl'], 'http://img.com/console.jpg')
        self.assertEqual(product_info['description'], 'Console de última geração para jogos.')
        self.assertEqual(product_info['category'], 'Eletrônicos')
        self.assertEqual(product_info['brand'], 'Sony')
        self.assertEqual(product_info['min_price'], 2300.00)
        self.assertIsInstance(product_info['offers'], list)
        self.assertEqual(len(product_info['offers']), 3)
        self.assertEqual(product_info['offers'][0]['price'], 2300.00)
        self.assertEqual(product_info['offers'][0]['store'], 'Loja A')

    def test_get_product_info_non_existing_product(self):
        product_info = get_product_info(99999)
        self.assertIsNone(product_info)

    def test_get_product_info_product_without_offers(self):
        product_info = get_product_info(self.produto_sem_ofertas.id)
        self.assertIsNotNone(product_info)
        self.assertEqual(product_info['id'], self.produto_sem_ofertas.id)
        self.assertIsNone(product_info['min_price'])
        self.assertEqual(len(product_info['offers']), 0)

    def test_search_products_by_name(self):
        results = search_products('console')
        self.assertTrue(len(results) >= 1)
        self.assertIn('Console de Videogame', [p['name'] for p in results])
        self.assertEqual(results[0]['min_price'], 2300.00)

        results = search_products('mouse')
        self.assertTrue(len(results) >= 1)
        self.assertIn('Mouse Gamer Wireless', [p['name'] for p in results])
        self.assertEqual(results[0]['min_price'], 150.00)

    def test_search_products_by_description_and_category(self):
        results_desc = search_products('geração')
        self.assertIn('Console de Videogame', [p['name'] for p in results_desc])

        results_cat = search_products('livros')
        self.assertIn('Livro de Programação', [p['name'] for p in results_cat])

    def test_search_products_no_results(self):
        results = search_products('produtoinexistente123')
        self.assertEqual(len(results), 0)

    def test_search_products_empty_query(self):
        all_products_in_db = Produto.objects.count()
        results = search_products('')
        self.assertEqual(len(results), all_products_in_db)
        
        console_in_results = next((p for p in results if p['id'] == self.produto_com_ofertas.id), None)
        self.assertIsNotNone(console_in_results)
        self.assertEqual(console_in_results['min_price'], 2300.00)

        livro_in_results = next((p for p in results if p['id'] == self.produto_sem_ofertas.id), None)
        self.assertIsNotNone(livro_in_results)
        self.assertIsNone(livro_in_results['min_price'])