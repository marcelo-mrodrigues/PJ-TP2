## @file tests/test_models.py
#
# @brief Contém testes de unidade para a criação e validação dos modelos de dados do aplicativo 'core'.
#
# Este arquivo utiliza o framework de testes `unittest` do Django para
# verificar a funcionalidade básica de criação de instâncias para cada modelo,
# bem como a validação de campos e o comportamento de relacionamentos e restrições.
#
# @see core.models
# @see core.forms

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Categoria, Marca, Produto, Loja, Oferta, Usuario, ItemComprado # Importe Usuario explicitamente

from django.db import IntegrityError # Importe para testar unique_together
import decimal # Para lidar com valores DecimalFields

from unittest.mock import patch # Para mockar timezone.now se necessário para testes precisos


## @brief Conjunto de testes para a criação e propriedades básicas dos modelos.
#
# Testa a criação de instâncias para Categoria, Marca, Produto, Loja, Oferta,
# Usuario e ItemComprado, verificando se os dados são salvos corretamente
# e se as representações em string dos objetos estão como esperado.
class ModelCreationTest(TestCase):
    ## @brief Configura os dados de teste que serão usados por todos os métodos da classe.
    #
    # Cria usuários (administrador e normal), categorias, marcas, um produto base e uma loja base
    # para serem utilizados como pré-requisitos nos testes de criação de outros modelos.
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
            # REMOVIDO: 'role' não é mais um campo no modelo Usuario (comentário original)
        )
        ## @var admin_user
        # @brief Instância de usuário com permissões de administrador.
        # @type Usuario

        # Criar um usuário normal
        cls.normal_user = Usuario.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpassword',
            first_name='Normal', # Adicionado first_name/last_name para consistência
            last_name='User'
            # REMOVIDO: 'role' não é mais um campo no modelo Usuario (comentário original)
        )
        ## @var normal_user
        # @brief Instância de usuário com permissões normais.
        # @type Usuario

        # Criar categorias e marcas
        cls.categoria_eletronicos = Categoria.objects.create(nome='Eletrônicos')
        ## @var categoria_eletronicos
        # @brief Instância da categoria 'Eletrônicos'.
        # @type Categoria
        cls.marca_samsung = Marca.objects.create(nome='Samsung')
        ## @var marca_samsung
        # @brief Instância da marca 'Samsung'.
        # @type Marca
        cls.marca_apple = Marca.objects.create(nome='Apple')
        ## @var marca_apple
        # @brief Instância da marca 'Apple'.
        # @type Marca
        
        # Criar um produto para uso em ofertas
        cls.produto_base = Produto.objects.create(
            nome='Produto Base para Oferta',
            categoria=cls.categoria_eletronicos,
            adicionado_por=cls.admin_user,
            imagem_url='http://example.com/base_prod.jpg' # Adicionado imagem_url para consistência
        )
        ## @var produto_base
        # @brief Instância de um produto base para testes de Oferta e ItemComprado.
        # @type Produto
        cls.loja_base = Loja.objects.create(nome='Loja Base')
        ## @var loja_base
        # @brief Instância de uma loja base para testes de Oferta e ItemComprado.
        # @type Loja

    ## @brief Testa a criação de uma instância do modelo Categoria.
    #
    # Verifica se a categoria é criada com o nome correto, se o contador de objetos aumenta
    # e se a representação em string está correta.
    def test_create_categoria(self):
        initial_count = Categoria.objects.count()
        categoria = Categoria.objects.create(nome='Livros')
        self.assertEqual(categoria.nome, 'Livros')
        self.assertEqual(Categoria.objects.count(), initial_count + 1)
        self.assertTrue(isinstance(categoria, Categoria))
        self.assertEqual(str(categoria), 'Livros')

    ## @brief Testa a criação de uma instância do modelo Marca.
    #
    # Verifica se a marca é criada com o nome correto, se o contador de objetos aumenta
    # e se a representação em string está correta.
    def test_create_marca(self):
        initial_count = Marca.objects.count()
        marca = Marca.objects.create(nome='Dell')
        self.assertEqual(marca.nome, 'Dell')
        self.assertEqual(Marca.objects.count(), initial_count + 1)
        self.assertTrue(isinstance(marca, Marca))
        self.assertEqual(str(marca), 'Dell')

    ## @brief Testa a criação de uma instância do modelo Produto.
    #
    # Verifica se o produto é criado com todos os campos corretamente preenchidos,
    # incluindo relacionamentos com Categoria, Marca e Usuario.
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

    ## @brief Testa a criação de uma instância do modelo Loja.
    #
    # Verifica se a loja é criada com todos os campos corretamente preenchidos.
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

    ## @brief Testa a criação de uma instância do modelo Oferta.
    #
    # Verifica se a oferta é criada com os relacionamentos corretos com Produto e Loja,
    # e se o preço e data de captura são registrados.
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


    ## @brief Testa a restrição unique_together do modelo Oferta para diferentes momentos.
    #
    # Verifica se é possível criar múltiplas ofertas para o mesmo produto e loja,
    # desde que a `data_captura` seja diferente.
    def test_oferta_unique_together_different_time(self):
        Oferta.objects.create(produto=self.produto_base, loja=self.loja_base, preco=decimal.Decimal('300.00'), data_captura=timezone.now())
        future_time = timezone.now() + timedelta(seconds=1)
        Oferta.objects.create(produto=self.produto_base, loja=self.loja_base, preco=decimal.Decimal('290.00'), data_captura=future_time)
        self.assertEqual(Oferta.objects.filter(produto=self.produto_base, loja=self.loja_base).count(), 2)

    ## @brief Testa a criação de uma instância do modelo Usuario.
    #
    # Verifica se um usuário normal é criado corretamente com os campos esperados
    # e se as flags de staff/superuser são `False`.
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


    ## @brief Testa a criação de uma instância do modelo ItemComprado.
    #
    # Verifica se um item comprado é registrado corretamente, com o preço pago,
    # data da compra e relacionamentos com Produto, Loja e Usuário.
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

