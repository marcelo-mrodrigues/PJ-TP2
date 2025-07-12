from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Categoria, Marca, Produto, Loja, Oferta, Usuario


# Exemplo de teste básico para evitar o erro F401
class MySimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


# Adicione seus testes de modelos e views aqui conforme o desenvolvimento
class ModelCreationTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Configura dados que serão usados por todos os métodos de teste
        nesta classe, executado apenas uma vez.
        """
        # Criar um usuário administrador para associar aos produtos
        cls.admin_user = Usuario.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User',
            role=True, # Define como administrador
            is_staff=True,
            is_superuser=True
        )

        # Criar uma categoria e marca para os produtos
        cls.categoria_eletronicos = Categoria.objects.create(nome='Eletrônicos')
        cls.marca_samsung = Marca.objects.create(nome='Samsung')
        cls.marca_apple = Marca.objects.create(nome='Apple')

    def test_create_categoria(self):
        """
        Testa a criação de uma nova categoria.
        """
        categoria = Categoria.objects.create(nome='Livros')
        self.assertEqual(categoria.nome, 'Livros')
        self.assertEqual(Categoria.objects.count(), 3) # Eletrônicos, Samsung (criadas em setUpTestData) + Livros
        self.assertTrue(isinstance(categoria, Categoria))
        self.assertEqual(str(categoria), 'Livros')

    def test_create_marca(self):
        """
        Testa a criação de uma nova marca.
        """
        marca = Marca.objects.create(nome='Dell')
        self.assertEqual(marca.nome, 'Dell')
        self.assertEqual(Marca.objects.count(), 3) # Samsung, Apple (criadas em setUpTestData) + Dell
        self.assertTrue(isinstance(marca, Marca))
        self.assertEqual(str(marca), 'Dell')

    def test_create_product(self):
        """
        Testa a criação de um novo Produto.
        """
        produto = Produto.objects.create(
            nome='Smartphone Galaxy S23',
            descricao='Celular top de linha da Samsung.',
            imagem_url='http://example.com/galaxy.jpg',
            categoria=self.categoria_eletronicos,
            marca=self.marca_samsung,
            adicionado_por=self.admin_user
        )
        self.assertIsNotNone(produto.id)
        self.assertEqual(produto.nome, 'Smartphone Galaxy S23')
        self.assertEqual(produto.categoria, self.categoria_eletronicos)
        self.assertEqual(produto.marca, self.marca_samsung)
        self.assertEqual(produto.adicionado_por, self.admin_user)
        self.assertIsNotNone(produto.data_adicao)
        self.assertTrue(isinstance(produto, Produto))
        self.assertEqual(str(produto), 'Smartphone Galaxy S23')

    def test_create_loja(self):
        """
        Testa a criação de uma nova Loja.
        """
        loja = Loja.objects.create(
            nome='Magazine Luiza',
            url='http://magazineluiza.com.br',
            logo_url='http://magazineluiza.com.br/logo.png'
        )
        self.assertIsNotNone(loja.id)
        self.assertEqual(loja.nome, 'Magazine Luiza')
        self.assertEqual(loja.url, 'http://magazineluiza.com.br')
        self.assertTrue(isinstance(loja, Loja))
        self.assertEqual(str(loja), 'Magazine Luiza')

    def test_create_oferta(self):
        """
        Testa a criação de uma nova Oferta.
        """
        # Primeiro, precisamos de um produto e uma loja para a oferta
        produto = Produto.objects.create(
            nome='Notebook Apple MacBook Air',
            descricao='Notebook leve e potente.',
            imagem_url='http://example.com/macbook.jpg',
            categoria=self.categoria_eletronicos,
            marca=self.marca_apple,
            adicionado_por=self.admin_user
        )
        loja = Loja.objects.create(
            nome='Amazon Brasil',
            url='http://amazon.com.br',
            logo_url='http://amazon.com.br/logo.png'
        )

        oferta = Oferta.objects.create(
            produto=produto,
            loja=loja,
            preco=8500.50
        )
        self.assertIsNotNone(oferta.id)
        self.assertEqual(oferta.produto, produto)
        self.assertEqual(oferta.loja, loja)
        self.assertEqual(float(oferta.preco), 8500.50) # Use float para comparação de Decimal
        self.assertIsNotNone(oferta.data_captura)
        self.assertTrue(isinstance(oferta, Oferta))
        expected_str = f"Oferta de Notebook Apple MacBook Air na Amazon Brasil por R$8500.50"
        self.assertEqual(str(oferta), expected_str)

    def test_oferta_unique_together(self):
        """
        Testa a restrição unique_together em Oferta (produto, loja, data_captura).
        Duas ofertas para o mesmo produto na mesma loja no mesmo segundo
        não devem ser permitidas.
        """
        produto = Produto.objects.create(
            nome='Mouse Gamer',
            descricao='Mouse de alta precisão.',
            categoria=self.categoria_eletronicos,
            adicionado_por=self.admin_user
        )
        loja = Loja.objects.create(nome='Kabum')

        Oferta.objects.create(produto=produto, loja=loja, preco=100.00)

        # Tentando criar outra oferta exatamente no mesmo produto, loja e data/hora
        with self.assertRaises(Exception) as cm: # Expecta uma exceção de integridade de DB
             Oferta.objects.create(produto=produto, loja=loja, preco=99.00)
        # O tipo exato da exceção pode variar, mas geralmente é IntegrityError
        # (django.db.utils.IntegrityError) ou ValidationError dependendo de como a restrição é aplicada.
        # Para um `unique_together` em nível de banco de dados, é mais provável IntegrityError.
        self.assertIn('duplicate key value', str(cm.exception).lower()) # Mensagem comum de erro de unicidade

    def test_oferta_unique_together_different_time(self):
        """
        Testa se duas ofertas para o mesmo produto na mesma loja
        são permitidas se a data_captura for diferente.
        """
        produto = Produto.objects.create(
            nome='Teclado Mecânico',
            descricao='Teclado RGB.',
            categoria=self.categoria_eletronicos,
            adicionado_por=self.admin_user
        )
        loja = Loja.objects.create(nome='TerabyteShop')

        # Cria a primeira oferta
        Oferta.objects.create(produto=produto, loja=loja, preco=300.00)

        # Cria a segunda oferta um segundo depois
        # Para simular isso em um teste, precisamos criar uma data diferente
        future_time = timezone.now() + timedelta(seconds=1)
        Oferta.objects.create(produto=produto, loja=loja, preco=290.00, data_captura=future_time)

        # Deve haver duas ofertas para este produto/loja
        self.assertEqual(Oferta.objects.filter(produto=produto, loja=loja).count(), 2)


# Exemplo de teste para verificar o menor preço (usando funções de utils.py se existirem)
# Se você moveu a lógica de get_product_info para operar com os modelos reais,
# o teste seria assim:

# class ProductInfoUtilsTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         # Crie dados reais no banco para os testes
#         cls.admin_user = Usuario.objects.create_user(
#             username='testadmin', email='test@example.com', password='password', is_staff=True
#         )
#         cls.categoria = Categoria.objects.create(nome='Testes')
#         cls.loja1 = Loja.objects.create(nome='Loja Teste 1')
#         cls.loja2 = Loja.objects.create(nome='Loja Teste 2')
#         cls.produto_com_ofertas = Produto.objects.create(
#             nome='Produto Teste com Ofertas', categoria=cls.categoria, adicionado_por=cls.admin_user
#         )
#         cls.oferta1 = Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja1, preco=100.00)
#         cls.oferta2 = Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja2, preco=90.00)
#         cls.oferta3 = Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja1, preco=110.00) # Preço maior

#     def test_get_product_info_lowest_price(self):
#         """
#         Testa se get_product_info retorna o menor preço correto.
#         """
#         # Certifique-se de que sua função get_product_info agora consulta o DB
#         product_info = get_product_info(self.produto_com_ofertas.id)
#         self.assertIsNotNone(product_info)
#         self.assertEqual(product_info['min_price'], 90.00) # Espera o menor preço das ofertas

#     def test_get_product_info_no_offers(self):
#         """
#         Testa get_product_info para um produto sem ofertas.
#         """
#         produto_sem_ofertas = Produto.objects.create(
#             nome='Produto Teste sem Ofertas', categoria=self.categoria, adicionado_por=self.admin_user
#         )
#         product_info = get_product_info(produto_sem_ofertas.id)
#         self.assertIsNotNone(product_info)
#         self.assertIsNone(product_info['min_price']) # Espera None se não houver ofertas
#         self.assertEqual(len(product_info['offers']), 0)