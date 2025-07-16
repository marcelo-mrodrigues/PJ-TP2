## @file core/testUtils.py
#
# @brief Contém testes de unidade para as funções utilitárias que interagem com o ORM do Django.
#
# Este arquivo testa as funções `get_product_info` e `search_products` localizadas
# no módulo `core.utils`, verificando seu comportamento ao buscar e processar
# informações de produtos e ofertas do banco de dados.
#
# @see core.utils
# @see core.models

from django.test import TestCase
from django.utils import timezone 
from datetime import timedelta 
import datetime # Importar datetime para criar objetos datetime concretos
from .models import Categoria, Marca, Produto, Loja, Oferta, Usuario 
import decimal 
from unittest.mock import patch 

# Importa as funções do seu arquivo utils.py
from .utils import get_product_info, search_products


## @brief Conjunto de testes para as funções utilitárias que interagem com o ORM.
#
# Testa o comportamento das funções `get_product_info` e `search_products`
# em diferentes cenários, incluindo produtos com e sem ofertas, e diversas consultas de busca.
class ProductInfoUtilsTest(TestCase):
    ## @brief Configura os dados de teste que serão usados por todos os métodos da classe.
    #
    # Cria instâncias de usuários, categorias, marcas, lojas e produtos,
    # incluindo produtos com e sem ofertas, para simular um ambiente de banco de dados.
    # Utiliza `unittest.mock.patch` para controlar `timezone.now` e garantir
    # datas de captura de ofertas previsíveis.
    @classmethod
    def setUpTestData(cls):
        ## @var admin_user
        # @brief Usuário com permissões de administrador para testes.
        # @type Usuario
        cls.admin_user = Usuario.objects.create_user(
            username='testadmin', email='test@example.com', password='password',
            first_name='Test', last_name='Admin', is_staff=True, is_superuser=True
        )
        ## @var normal_user
        # @brief Usuário normal para testes.
        # @type Usuario
        cls.normal_user = Usuario.objects.create_user(
            username='testuser', email='user@example.com', password='password',
            first_name='Test', last_name='User'
        )

        ## @var categoria_eletronicos
        # @brief Instância da categoria 'Eletrônicos'.
        # @type Categoria
        cls.categoria_eletronicos = Categoria.objects.create(nome='Eletrônicos')
        ## @var categoria_livros
        # @brief Instância da categoria 'Livros'.
        # @type Categoria
        cls.categoria_livros = Categoria.objects.create(nome='Livros')
        ## @var marca_sony
        # @brief Instância da marca 'Sony'.
        # @type Marca
        cls.marca_sony = Marca.objects.create(nome='Sony')
        ## @var marca_logitech
        # @brief Instância da marca 'Logitech'.
        # @type Marca
        cls.marca_logitech = Marca.objects.create(nome='Logitech')

        ## @var loja_a
        # @brief Instância da loja 'Loja A'.
        # @type Loja
        cls.loja_a = Loja.objects.create(nome='Loja A', url='http://loja_a.com')
        ## @var loja_b
        # @brief Instância da loja 'Loja B'.
        # @type Loja
        cls.loja_b = Loja.objects.create(nome='Loja B', url='http://loja_b.com')

        ## @var produto_com_ofertas
        # @brief Produto com múltiplas ofertas para teste.
        # @type Produto
        cls.produto_com_ofertas = Produto.objects.create(
            nome='Console de Videogame',
            descricao='Console de última geração para jogos.',
            imagem_url='http://img.com/console.jpg',
            categoria=cls.categoria_eletronicos,
            marca=cls.marca_sony,
            adicionado_por=cls.admin_user
        )
        
        # Cria ofertas para o produto_com_ofertas em momentos específicos
        with patch('django.utils.timezone.now') as mock_now:
            # Para a primeira oferta
            mock_now.return_value = datetime.datetime(2025, 7, 14, 10, 0, 0, tzinfo=datetime.timezone.utc)
            Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja_b, preco=decimal.Decimal('2500.00'))

            # Para a segunda oferta (menor preço)
            mock_now.return_value = datetime.datetime(2025, 7, 14, 10, 5, 0, tzinfo=datetime.timezone.utc) # 5 minutos depois
            Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja_a, preco=decimal.Decimal('2300.50')) # Menor preço

            # Para a terceira oferta
            mock_now.return_value = datetime.datetime(2025, 7, 14, 10, 10, 0, tzinfo=datetime.timezone.utc) # 10 minutos depois
            Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja_b, preco=decimal.Decimal('2400.00'))

        ## @var produto_sem_ofertas
        # @brief Produto sem ofertas para teste.
        # @type Produto
        cls.produto_sem_ofertas = Produto.objects.create(
            nome='Livro de Programação',
            descricao='Guia completo para desenvolvimento web.',
            imagem_url='http://img.com/livro.jpg',
            categoria=cls.categoria_livros,
            adicionado_por=cls.normal_user
        )

        ## @var produto_mouse
        # @brief Produto adicional para teste de busca.
        # @type Produto
        cls.produto_mouse = Produto.objects.create(
            nome='Mouse Gamer Wireless',
            descricao='Mouse ergonômico para jogos e produtividade.',
            imagem_url='http://img.com/mouse.jpg',
            categoria=cls.categoria_eletronicos,
            marca=cls.marca_logitech,
            adicionado_por=cls.admin_user
        )
        # Cria uma oferta para o produto_mouse
        Oferta.objects.create(produto=cls.produto_mouse, loja=cls.loja_a, preco=decimal.Decimal('150.00'))

    ## @brief Testa a função `get_product_info` com um produto existente que possui ofertas.
    #
    # Verifica se as informações do produto são retornadas corretamente, incluindo
    # o menor preço e a lista de ofertas associadas.
    def test_get_product_info_existing_product(self):
        product_info = get_product_info(self.produto_com_ofertas.id)
        self.assertIsNotNone(product_info)
        self.assertEqual(product_info['id'], self.produto_com_ofertas.id)
        self.assertEqual(product_info['nome'], 'Console de Videogame')
        self.assertEqual(product_info['imagem_url'], 'http://img.com/console.jpg')
        self.assertEqual(product_info['descricao'], 'Console de última geração para jogos.')
        self.assertEqual(product_info['categoria'], 'Eletrônicos')
        self.assertEqual(product_info['marca'], 'Sony')
        self.assertEqual(product_info['menor_preco'], 2300.50)
        self.assertIsInstance(product_info['ofertas'], list)
        self.assertEqual(len(product_info['ofertas']), 3)
        self.assertEqual(product_info['ofertas'][0]['preco'], 2300.50)
        self.assertEqual(product_info['ofertas'][0]['loja'], 'Loja A')

    ## @brief Testa a função `get_product_info` com um ID de produto não existente.
    #
    # Verifica se a função retorna `None` quando o produto não é encontrado.
    def test_get_product_info_non_existing_product(self):
        product_info = get_product_info(99999)
        self.assertIsNone(product_info)

    ## @brief Testa a função `get_product_info` com um produto que não possui ofertas.
    #
    # Verifica se as informações do produto são retornadas corretamente, e se
    # `menor_preco` é `None` e a lista de `ofertas` está vazia.
    def test_get_product_info_product_without_offers(self):
        product_info = get_product_info(self.produto_sem_ofertas.id)
        self.assertIsNotNone(product_info)
        self.assertEqual(product_info['id'], self.produto_sem_ofertas.id)
        self.assertIsNone(product_info['menor_preco'])
        self.assertEqual(len(product_info['ofertas']), 0)

    ## @brief Testa a função `search_products` buscando produtos pelo nome.
    #
    # Verifica se os resultados da busca contêm os produtos esperados e seus menores preços.
    # @param query Termo de busca (ex: 'console', 'mouse').
    def test_search_products_by_name(self):
        results = search_products('console')
        self.assertTrue(len(results) >= 1)
        self.assertIn('Console de Videogame', [p['nome'] for p in results])
        self.assertEqual(results[0]['menor_preco'], 2300.50)

        results = search_products('mouse')
        self.assertTrue(len(results) >= 1)
        self.assertIn('Mouse Gamer Wireless', [p['nome'] for p in results])
        self.assertEqual(results[0]['menor_preco'], 150.00)

    ## @brief Testa a função `search_products` buscando produtos por descrição e categoria.
    #
    # Verifica se a busca funciona com termos presentes na descrição e nomes de categoria.
    # @param query Termo de busca (ex: 'geração', 'livros').
    def test_search_products_by_description_and_category(self):
        results_desc = search_products('geração')
        self.assertIn('Console de Videogame', [p['nome'] for p in results_desc])

        results_cat = search_products('livros')
        self.assertIn('Livro de Programação', [p['nome'] for p in results_cat])

    ## @brief Testa a função `search_products` com uma consulta que não retorna resultados.
    #
    # Verifica se a lista de resultados está vazia quando nenhum produto corresponde à busca.
    def test_search_products_no_results(self):
        results = search_products('produtoinexistente123')
        self.assertEqual(len(results), 0)

    ## @brief Testa a função `search_products` com uma consulta vazia.
    #
    # Verifica se todos os produtos no banco de dados são retornados quando a consulta é vazia,
    # e se as informações de menor preço estão corretas para produtos com e sem ofertas.
    def test_search_products_empty_query(self):
        all_products_in_db = Produto.objects.count()
        results = search_products('')
        self.assertEqual(len(results), all_products_in_db)
        
        console_in_results = next((p for p in results if p['id'] == self.produto_com_ofertas.id), None)
        self.assertIsNotNone(console_in_results)
        self.assertEqual(console_in_results['menor_preco'], 2300.50)

        livro_in_results = next((p for p in results if p['id'] == self.produto_sem_ofertas.id), None)
        self.assertIsNotNone(livro_in_results)
        self.assertIsNone(livro_in_results['menor_preco'])
