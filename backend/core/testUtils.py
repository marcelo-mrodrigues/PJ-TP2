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

from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.middleware.csrf import get_token
from django.utils import timezone 
from datetime import timedelta 
import datetime # Importar datetime para criar objetos datetime concretos
from .models import Categoria, Marca, Produto, Loja, Oferta, Usuario 
from django.contrib.messages.storage.fallback import FallbackStorage
import decimal 
from unittest.mock import patch 
from .forms import LojaForm, ListaCompra, ItemLista

# Importa as funções do seu arquivo utils.py
from .utils import get_product_info, search_products, _get_base_html_context, _get_messages_html, _get_action_value_for_form,  process_loja_form, render_lojas_html, merge_session_cart_to_db


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


class BaseHtmlContextTest(TestCase):
    ## @brief Configura o ambiente de testes com uma `RequestFactory`.
    def setUp(self):
        self.factory = RequestFactory()

    ## @brief Cria uma requisição com suporte a mensagens Django.
    #
    # @return Objeto `HttpRequest` com sistema de mensagens configurado.
    def _get_request_with_messages(self):
        request = self.factory.get("/")
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request

    ## @brief Testa o contexto HTML gerado para formulário de adição.
    #
    # Verifica se os elementos esperados estão presentes, como título, botão de voltar e form renderizado.
    def test_base_html_context_add_form(self):
        request = self._get_request_with_messages()
        form = LojaForm()
        title = "Gerenciar Lojas"
        context = _get_base_html_context(request, title, form)
        content = context["content"]

        self.assertIn("<h2>Gerenciar Lojas</h2>", content)
        self.assertIn("Adicionar Novo Loja", content)
        self.assertIn(form.as_p(), content)
        self.assertIn("Voltar para a Home", content)
        self.assertIn("add_or_update_store", content)

    ## @brief Testa o contexto HTML gerado para formulário de edição.
    #
    # Verifica se o nome da loja e o título "Editar Loja" estão presentes no HTML.
    def test_base_html_context_edit_form(self):
        request = self._get_request_with_messages()
        loja = Loja.objects.create(nome="Loja Teste", url="http://teste.com")
        form = LojaForm(instance=loja)
        title = "Gerenciar Lojas"
        context = _get_base_html_context(request, title, form)
        content = context["content"]

        self.assertIn("Editar Loja", content)
        self.assertIn("Loja Teste", content)

    ## @brief Testa o HTML gerado pelas mensagens de sucesso e erro.
    #
    # Garante que mensagens com estilos corretos são exibidas no HTML.
    def test_get_messages_html_with_success_and_error(self):
        request = self._get_request_with_messages()
        from django.contrib import messages
        messages.success(request, "Sucesso!")
        messages.error(request, "Erro!")

        html = _get_messages_html(request)
        self.assertIn('style="color:green;"', html)
        self.assertIn("Sucesso!", html)
        self.assertIn('style="color:red;"', html)
        self.assertIn("Erro!", html)

    ## @brief Testa o retorno de `_get_messages_html` quando não há mensagens.
    def test_get_messages_html_empty(self):
        request = self._get_request_with_messages()
        html = _get_messages_html(request)
        self.assertEqual(html, "")

    ## @brief Testa os valores de ação gerados a partir de diferentes títulos.
    def test_get_action_value_for_form(self):
        self.assertEqual(_get_action_value_for_form("Gerenciar Lojas"), "add_or_update_store")
        self.assertEqual(_get_action_value_for_form("Gerenciar Produtos"), "add_or_update_product")
        self.assertEqual(_get_action_value_for_form("Gerenciar Ofertas"), "add_or_update")
        self.assertEqual(_get_action_value_for_form("Outro título qualquer"), "")

## @brief Testes para a função `merge_session_cart_to_db`.
#
# Verifica o comportamento de mesclagem do carrinho da sessão para o banco de dados, garantindo a
# criação correta de listas de compras e itens, e o tratamento de produtos inválidos.
class MergeSessionCartTests(TestCase):
    ## @brief Configura os dados iniciais: usuário, categoria, marca e produtos.
    def setUp(self):
        self.user = Usuario.objects.create_user(username="user", password="123")
        self.cat = Categoria.objects.create(nome="Categoria")
        self.marca = Marca.objects.create(nome="Marca")
        self.prod1 = Produto.objects.create(nome="Produto 1", categoria=self.cat, marca=self.marca, adicionado_por=self.user)
        self.prod2 = Produto.objects.create(nome="Produto 2", categoria=self.cat, marca=self.marca, adicionado_por=self.user)
        self.factory = RequestFactory()

    ## @brief Testa se a função cria lista e itens corretamente a partir da sessão.
    def test_merge_cart_creates_list_and_items(self):
        request = self.factory.get("/")
        request.user = self.user
        request.session = {
            "cart": {
                str(self.prod1.id): {"quantity": 2},
                str(self.prod2.id): {"quantity": 1},
            }
        }

        merge_session_cart_to_db(request)

        lista = ListaCompra.objects.filter(usuario=self.user, finalizada=False).first()
        self.assertIsNotNone(lista)
        self.assertEqual(lista.itens.count(), 2)

    ## @brief Testa o comportamento ao tentar mesclar um carrinho com ID de produto inválido.
    #
    # A lista não deve ser criada nesse cenário (versão que espera `None`).
    def test_merge_cart_ignores_invalid_product(self):
        request = self.factory.get("/")
        request.user = self.user
        request.session = {
            "cart": {
                "9999": {"quantity": 3},
            }
        }

        merge_session_cart_to_db(request)
        lista = ListaCompra.objects.filter(usuario=self.user, finalizada=False).first()
        self.assertEqual(lista.itens.count(), 0)

    ## @brief Testa se a lista é criada mesmo com produtos inválidos, mas sem adicionar itens.
    #
    # Útil quando a lógica permite criar uma lista de compra vazia.
    def test_merge_cart_creates_empty_list_if_all_invalid(self):
        request = self.factory.get("/")
        request.user = self.user
        request.session = {
            "cart": {
                "9999": {"quantity": 3},
            }
        }

        merge_session_cart_to_db(request)

        lista = ListaCompra.objects.filter(usuario=self.user, finalizada=False).first()
        self.assertIsNotNone(lista)
        self.assertEqual(lista.itens.count(), 0)


## @brief Testes para a função `render_lojas_html`.
#
# Garante que o HTML gerado reflita corretamente o estado da lista de lojas: vazia ou preenchida.
class RenderLojasHtmlTests(TestCase):
    ## @brief Configura requisição de teste sem sessão.
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = {}

    ## @brief Testa o HTML renderizado quando não há lojas cadastradas.
    def test_render_lojas_empty(self):
        html = render_lojas_html(self.request, Loja.objects.none())
        self.assertIn("Nenhuma loja cadastrada ainda", html)

    ## @brief Testa o HTML renderizado com uma loja cadastrada.
    #
    # Verifica se os dados da loja e os botões de editar/excluir aparecem no HTML.
    def test_render_lojas_with_content(self):
        loja = Loja.objects.create(nome="Loja Exemplo", url="https://exemplo.com")
        html = render_lojas_html(self.request, Loja.objects.all())

        self.assertIn("Loja Exemplo", html)
        self.assertIn("https://exemplo.com", html)
        self.assertIn("Editar", html)
        self.assertIn("Excluir", html)