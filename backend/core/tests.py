# core/tests.py

from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from .models import Categoria, Marca, Produto, Loja, Oferta, Usuario, Comentario, ProdutoIndicado, ItemComprado, ItemLista # Importe Usuario explicitamente
from django.urls import reverse
from django.db import IntegrityError # Importe para testar unique_together
import decimal # Para lidar com valores DecimalFields
from django.contrib.auth import get_user_model # Para obter o modelo de usuário configurado
from django.contrib.auth import authenticate, login # Para testar login na view
from unittest.mock import patch # Para mockar timezone.now se necessário para testes precisos




class ComentarioModelTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="usuario", password="senha")
        self.produto = Produto.objects.create(nome="Produto Teste", adicionado_por=self.user)
        self.loja = Loja.objects.create(nome="Loja Teste")

    def test_create_comentario_produto(self):
        comentario = Comentario.objects.create(usuario=self.user, produto=self.produto, texto="Muito bom!", nota=5)
        self.assertEqual(str(comentario), f"Comentário de {self.user} sobre Produto: {self.produto.nome}")

    def test_create_comentario_loja(self):
        comentario = Comentario.objects.create(usuario=self.user, loja=self.loja, texto="Atendimento ruim", nota=2)
        self.assertEqual(str(comentario), f"Comentário de {self.user} sobre Loja: {self.loja.nome}")

    def test_invalid_nota_range(self):
        with self.assertRaises(Exception):
            Comentario.objects.create(usuario=self.user, produto=self.produto, texto="Ruim", nota=6)  # fora do intervalo 1-5


class ProdutoIndicadoTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="user", password="123")
        self.produto = Produto.objects.create(nome="Produto Existente", adicionado_por=self.user)

    def test_create_indicacao_pendente(self):
        indicacao = ProdutoIndicado.objects.create(usuario=self.user, nome_produto="Produto Novo")
        self.assertEqual(indicacao.status, "pendente")
        self.assertIn("Indicação de", str(indicacao))

    def test_relacionar_com_produto_existente(self):
        indicacao = ProdutoIndicado.objects.create(
            usuario=self.user,
            nome_produto="Produto Novo",
            produto_existente=self.produto,
            status="aprovado"
        )
        self.assertEqual(indicacao.produto_existente, self.produto)

class ItemCompradoTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="user", password="123")
        self.produto = Produto.objects.create(nome="Produto", adicionado_por=self.user)
        self.loja = Loja.objects.create(nome="Loja")

    def test_create_item_comprado(self):
        item = ItemComprado.objects.create(
            usuario=self.user,
            produto=self.produto,
            loja=self.loja,
            preco_pago=50.0,
            data_compra="2024-05-01"
        )
        self.assertIn("Compra de", str(item))


class ListaCompraTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="user", password="123")
        self.produto = Produto.objects.create(nome="Produto", adicionado_por=self.user)
        self.lista = ListaCompra.objects.create(usuario=self.user, nome="Minha Lista")

    def test_adicionar_item_na_lista(self):
        item = ItemLista.objects.create(lista=self.lista, produto=self.produto)
        self.assertIn(self.produto.nome, str(item))



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
        )
        # Criar um usuário normal
        cls.normal_user = Usuario.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpassword',
        )

        # Criar categorias e marcas
        cls.categoria_eletronicos = Categoria.objects.create(nome='Eletrônicos')
        cls.marca_samsung = Marca.objects.create(nome='Samsung')
        cls.marca_apple = Marca.objects.create(nome='Apple')
        
        # Criar um produto para uso em ofertas
        cls.produto_base = Produto.objects.create(
            nome='Produto Base para Oferta',
            categoria=cls.categoria_eletronicos,
            adicionado_por=cls.admin_user
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

    def test_oferta_unique_together(self):
        current_time = timezone.now()
        Oferta.objects.create(produto=self.produto_base, loja=self.loja_base, preco=decimal.Decimal('100.00'), data_captura=current_time)
        with self.assertRaises(IntegrityError):
             Oferta.objects.create(produto=self.produto_base, loja=self.loja_base, preco=decimal.Decimal('99.00'), data_captura=current_time)
        self.assertEqual(Oferta.objects.filter(produto=self.produto_base, loja=self.loja_base).count(), 1)

    def test_oferta_unique_together_different_time(self):
        Oferta.objects.create(produto=self.produto_base, loja=self.loja_base, preco=decimal.Decimal('300.00'), data_captura=timezone.now())
        future_time = timezone.now() + timedelta(seconds=1)
        Oferta.objects.create(produto=self.produto_base, loja=self.loja_base, preco=decimal.Decimal('290.00'), data_captura=future_time)
        self.assertEqual(Oferta.objects.filter(produto=self.produto_base, loja=self.loja_base).count(), 2)


class ProductInfoUtilsTest(TestCase):
    """
    Testes para as funções utilitárias que interagem com o ORM.
    """
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = Usuario.objects.create_user(
            username='testadmin', email='test@example.com', password='password', is_staff=True
        )
        cls.categoria = Categoria.objects.create(nome='Testes')
        cls.loja1 = Loja.objects.create(nome='Loja Teste 1')
        cls.loja2 = Loja.objects.create(nome='Loja Teste 2')
        cls.produto_com_ofertas = Produto.objects.create(
            nome='Produto Teste com Ofertas', categoria=cls.categoria, adicionado_por=cls.admin_user, imagem_url='http://img.com/oferta.jpg'
        )
        # Usamos patch para fixar o tempo, garantindo que as datas de captura sejam diferentes para unique_together
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = timezone.now() - timedelta(minutes=5)
            Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja1, preco=decimal.Decimal('100.00'))
            mock_now.return_value = timezone.now() - timedelta(minutes=3)
            Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja2, preco=decimal.Decimal('90.00'))
            mock_now.return_value = timezone.now() - timedelta(minutes=1)
            Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja1, preco=decimal.Decimal('110.00'))

        cls.produto_sem_ofertas = Produto.objects.create(
            nome='Produto Teste sem Ofertas', categoria=cls.categoria, adicionado_por=cls.admin_user, imagem_url='http://img.com/sem-oferta.jpg'
        )
        # Crie alguns produtos extras para testar a busca
        Produto.objects.create(nome='Câmera DSLR', categoria=cls.categoria, adicionado_por=cls.admin_user, descricao="Ótima para fotos")
        Produto.objects.create(nome='Lente 50mm', categoria=cls.categoria, adicionado_por=cls.admin_user)
        Loja.objects.create(nome='Loja Câmeras')

    def test_get_product_info_lowest_price(self):
        from .utils import get_product_info
        product_info = get_product_info(self.produto_com_ofertas.id)
        self.assertIsNotNone(product_info)
        self.assertEqual(product_info['min_price'], 90.00) # Espera o menor preço das ofertas
        self.assertTrue('offers' in product_info)
        self.assertEqual(len(product_info['offers']), 3) # Deve ter 3 ofertas

    def test_get_product_info_no_offers(self):
        from .utils import get_product_info
        product_info = get_product_info(self.produto_sem_ofertas.id)
        self.assertIsNotNone(product_info)
        self.assertIsNone(product_info['min_price'])
        self.assertEqual(len(product_info['offers']), 0)

    def test_search_products_by_name(self):
        from .utils import search_products
        results = search_products('câmera')
        self.assertTrue(len(results) >= 1) # Pode ter outros produtos de setupTestData
        self.assertIn('Câmera DSLR', [p['name'] for p in results])

    def test_search_products_empty_query(self):
        from .utils import search_products
        all_results = search_products('')
        self.assertEqual(len(all_results), Produto.objects.count())


class ViewAccessAndRenderTest(TestCase):
    """
    Testes para verificar o acesso, redirecionamentos e renderização de templates HTML.
    """
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.admin_user = self.user_model.objects.create_user(
            username='adminuser', email='admin@example.com', password='adminpassword', is_staff=True, is_superuser=True
        )
        self.normal_user = self.user_model.objects.create_user(
            username='normaluser', email='normal@example.com', password='normalpassword'
        )
        self.categoria = Categoria.objects.create(nome='Livros')
        self.marca = Marca.objects.create(nome='Editora X')
        self.produto_existente = Produto.objects.create(
            nome='Produto Teste View', categoria=self.categoria, adicionado_por=self.admin_user, imagem_url='http://viewimg.com/prod.jpg'
        )
        self.loja_existente = Loja.objects.create(nome='Loja Teste View', url='http://loja.com')
        Oferta.objects.create(produto=self.produto_existente, loja=self.loja_existente, preco=decimal.Decimal('99.99'))

    # --- Testes para home_view ---
    def test_home_view_get(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html') # Agora home_view renderiza home.html
        self.assertContains(response, '<h1>Bem-vindo à Tela Inicial!</h1>') # Ou outro conteúdo do seu home.html

    # --- Testes para register_view ---
    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/register.html')
        self.assertContains(response, 'REGISTER ACCOUNT') # Título do formulário
        self.assertContains(response, '<form method="POST"') # Verifica se o formulário está presente

    def test_register_view_post_success(self):
        user_count_before = self.user_model.objects.count()
        response = self.client.post(reverse('register'), {
            'username': 'newuser1',
            'email': 'newuser1@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(self.user_model.objects.count(), user_count_before + 1)
        new_user = self.user_model.objects.get(username='newuser1')
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)

    def test_register_view_post_invalid(self):
        user_count_before = self.user_model.objects.count()
        response = self.client.post(reverse('register'), {
            'username': '', # Nome de usuário vazio
            'email': 'invalid-email',
            'password': 'short',
            'password2': 'pass',
            'first_name': '',
            'last_name': '',
        })
        self.assertEqual(response.status_code, 200) # Re-renderiza a página
        self.assertTemplateUsed(response, 'core/register.html')
        self.assertEqual(self.user_model.objects.count(), user_count_before) # Nenhum usuário criado
        self.assertContains(response, 'Este campo é obrigatório')
        self.assertContains(response, 'Digite um endereço de e-mail válido')
        self.assertContains(response, 'A senha é muito curta.') # Validação de senha

    # --- Testes para login_view ---
    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')
        self.assertContains(response, 'LOGIN') # Título do formulário
        self.assertContains(response, '<form method="POST"')

    def test_login_view_post_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'normaluser',
            'password': 'normalpassword',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(response.client.session['_auth_user_id']) # Verifica se o usuário está logado

    def test_login_view_post_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'normaluser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200) # Re-renderiza a página
        self.assertTemplateUsed(response, 'core/login.html')
        self.assertFalse(response.client.session.get('_auth_user_id')) # Usuário não deve estar logado
        self.assertContains(response, 'Nome de usuário ou senha inválidos')

    # --- Testes para product_catalog_view (agora renderiza HTML) ---
    def test_product_catalog_view_get(self):
        response = self.client.get(reverse('product_catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/product_catalog.html')
        self.assertContains(response, '<h1>Catálogo de Produtos</h1>') # Confirma conteúdo do template
        self.assertContains(response, '<div class="product-grid"') # Verifica a grade de produtos

    def test_product_catalog_view_search_query(self):
        response = self.client.get(reverse('product_catalog'), {'q': 'Produto Teste View'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/product_catalog.html')
        self.assertContains(response, 'Produto Teste View') # Verifica se o produto buscado aparece

    # --- Testes para produto_view (agora renderiza HTML com JS para fetch) ---
    def test_produto_view_get_existing(self):
        response = self.client.get(reverse('produto', args=[self.produto_existente.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/produto.html')
        self.assertContains(response, '<div id="product-detail">') # Verifica a estrutura básica do template
        self.assertContains(response, f'const productId = {self.produto_existente.id};') # Verifica se o ID foi injetado (via json_script)

    def test_produto_view_get_non_existent(self):
        response = self.client.get(reverse('produto', args=[99999])) # ID que não existe
        self.assertEqual(response.status_code, 200) # Ainda renderiza o template, mas o JS vai exibir erro
        self.assertTemplateUsed(response, 'core/produto.html')
        self.assertContains(response, 'id="product-id-data"') # O elemento que contém o ID injetado
        # O script JS no template vai lidar com o erro 404 da API, então a página ainda retorna 200


class APIViewTest(TestCase):
    """
    Testes para os endpoints de API que retornam JSON.
    """
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = Usuario.objects.create_user(
            username='apiadmin', email='api@example.com', password='apipassword', is_staff=True, is_superuser=True
        )
        cls.categoria = Categoria.objects.create(nome='API Testes')
        cls.loja = Loja.objects.create(nome='Loja API')
        cls.produto_api = Produto.objects.create(
            nome='Produto API Teste', categoria=cls.categoria, adicionado_por=cls.admin_user, imagem_url='http://apiimg.com/prod.jpg'
        )
        Oferta.objects.create(produto=cls.produto_api, loja=cls.loja, preco=decimal.Decimal('50.00'))

    def test_get_csrf_token_api(self):
        response = self.client.get(reverse('get_csrf_token'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertIn('csrfToken', data)
        self.assertGreater(len(data['csrfToken']), 10) # Token deve ter um tamanho razoável

    def test_buscar_produtos_api_view_get_all(self):
        response = self.client.get(reverse('buscar_produtos_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        # Assume que há pelo menos um produto do setUpTestData
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Produto API Teste')

    def test_buscar_produtos_api_view_get_search(self):
        response = self.client.get(reverse('buscar_produtos_api'), {'q': 'Produto API'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Produto API Teste')

    def test_get_product_data_api_view_get_existing(self):
        response = self.client.get(reverse('get_product_data_api', args=[self.produto_api.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertIn('product', data) # Espera a chave 'product'
        self.assertEqual(data['product']['id'], self.produto_api.id)
        self.assertEqual(data['product']['name'], 'Produto API Teste')
        self.assertEqual(data['product']['min_price'], 50.0)
        self.assertGreaterEqual(len(data['product']['offers']), 1)

    def test_get_product_data_api_view_get_non_existing(self):
        response = self.client.get(reverse('get_product_data_api', args=[99999]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertIn('error', data)


class ManageViewTest(TestCase):
    """
    Testes para as views de gerenciamento (Lojas, Produtos, Ofertas).
    Essas views renderizam HTML diretamente.
    """
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.admin_user = self.user_model.objects.create_user(
            username='adminuser', email='admin@example.com', password='adminpassword', is_staff=True, is_superuser=False
        )
        self.normal_user = self.user_model.objects.create_user(
            username='normaluser', email='normal@example.com', password='normalpassword', is_staff=False
        )

        self.categoria = Categoria.objects.create(nome='Livros')
        self.marca = Marca.objects.create(nome='Editora X')
        self.produto_manage = Produto.objects.create(
            nome='Produto para Gerenciar', categoria=self.categoria, adicionado_por=self.admin_user, imagem_url='http://manage.com/prod.jpg'
        )
        self.loja_manage = Loja.objects.create(nome='Loja para Gerenciar', url='http://manage.com')
        self.oferta_manage = Oferta.objects.create(produto=self.produto_manage, loja=self.loja_manage, preco=decimal.Decimal('150.00'))

    # --- Testes de Acesso Comum para Todas as Manage Views ---
    def _test_manage_view_access(self, url_name):
        # Não autenticado
        response = self.client.get(reverse(url_name))
        self.assertEqual(response.status_code, 302) # Redireciona para login
        self.assertIn('/login/?next=', response.url)

        # Usuário normal (logado mas não staff)
        self.client.login(username='normaluser', password='normalpassword')
        response = self.client.get(reverse(url_name))
        self.assertEqual(response.status_code, 302) # Redireciona para login (via staff_member_required)
        self.assertIn('/login/?next=', response.url)
        self.client.logout() # Limpa sessão

        # Usuário staff (mas não superadmin, para ManageUsersView)
        if url_name == 'manage_users': # Apenas superadmin pode acessar ManageUsersView
            self.client.login(username='adminuser', password='adminpassword')
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302) # Redireciona para login
            self.assertIn('/login/?next=', response.url)
            self.client.logout()

        # Admin (superuser) - deve ter acesso
        self.client.login(username='superadmin', password='superpassword')
        response = self.client.get(reverse(url_name))
        self.assertEqual(response.status_code, 200) # Acesso permitido
        self.assertContains(response, 'Gerenciar') # Título genérico de gerenciamento

    def test_manage_stores_view_access(self): self._test_manage_view_access('manage_stores')
    def test_manage_products_view_access(self): self._test_manage_view_access('manage_products')
    def test_manage_offers_view_access(self): self._test_manage_view_access('manage_offers')
    def test_manage_users_view_access(self): self._test_manage_view_access('manage_users')


    # --- Testes de Funcionalidade para manage_stores_view ---
    def test_manage_stores_add_new_store(self):
        self.client.login(username='superadmin', password='superpassword')
        store_count_before = Loja.objects.count()
        response = self.client.post(reverse('manage_stores'), {
            'action': 'add_or_update_store',
            'nome': 'Nova Loja Teste',
            'url': 'http://nova.com',
            'logo_url': 'http://nova.com/logo.png',
            'store_id_hidden': '', # Para nova loja, o ID é vazio
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_stores'))
        self.assertEqual(Loja.objects.count(), store_count_before + 1)
        self.assertTrue(Loja.objects.filter(nome='Nova Loja Teste').exists())
        messages = list(response.context['messages'])
        self.assertIn("Loja 'Nova Loja Teste' salva com sucesso!", str(messages[0]))

    def test_manage_stores_edit_store(self):
        self.client.login(username='superadmin', password='superpassword')
        store_id = self.loja_manage.id
        updated_name = "Loja Editada"
        response = self.client.post(reverse('manage_stores'), {
            'action': 'add_or_update_store',
            'nome': updated_name,
            'url': 'http://editada.com',
            'logo_url': 'http://editada.com/logo.png',
            'store_id_hidden': store_id, # ID da loja existente
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_stores'))
        self.loja_manage.refresh_from_db()
        self.assertEqual(self.loja_manage.nome, updated_name)
        messages = list(response.context['messages'])
        self.assertIn(f"Loja '{updated_name}' salva com sucesso!", str(messages[0]))

    def test_manage_stores_delete_store(self):
        self.client.login(username='superadmin', password='superpassword')
        store_id = self.loja_manage.id
        store_name = self.loja_manage.nome
        store_count_before = Loja.objects.count()
        response = self.client.post(reverse('manage_stores'), {
            'action': 'delete_store',
            'store_id': store_id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_stores'))
        self.assertEqual(Loja.objects.count(), store_count_before - 1)
        self.assertFalse(Loja.objects.filter(id=store_id).exists())
        # Verifica se ofertas relacionadas foram apagadas em cascata
        self.assertEqual(Oferta.objects.filter(loja=self.loja_manage).count(), 0)
        messages = list(response.context['messages'])
        self.assertIn(f"Loja '{store_name}' e suas ofertas relacionadas foram excluídas com sucesso!", str(messages[0]))

    # --- Testes de Funcionalidade para manage_products_view ---
    def test_manage_products_add_new_product(self):
        self.client.login(username='superadmin', password='superpassword')
        product_count_before = Produto.objects.count()
        response = self.client.post(reverse('manage_products'), {
            'action': 'add_or_update_product',
            'nome': 'Novo Produto Teste',
            'descricao': 'Descricao do novo produto.',
            'imagem_url': 'http://novo.com/img.jpg',
            'categoria': self.categoria.id,
            'marca': self.marca.id,
            'product_id_hidden': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_products'))
        self.assertEqual(Produto.objects.count(), product_count_before + 1)
        self.assertTrue(Produto.objects.filter(nome='Novo Produto Teste').exists())

    def test_manage_products_edit_product(self):
        self.client.login(username='superadmin', password='superpassword')
        product_id = self.produto_manage.id
        updated_name = "Produto Editado"
        response = self.client.post(reverse('manage_products'), {
            'action': 'add_or_update_product',
            'nome': updated_name,
            'descricao': 'Descricao atualizada.',
            'imagem_url': 'http://editado.com/img.jpg',
            'categoria': self.categoria.id,
            'marca': self.marca.id,
            'product_id_hidden': product_id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_products'))
        self.produto_manage.refresh_from_db()
        self.assertEqual(self.produto_manage.nome, updated_name)

    def test_manage_products_delete_product(self):
        self.client.login(username='superadmin', password='superpassword')
        product_id = self.produto_manage.id
        product_name = self.produto_manage.nome
        product_count_before = Produto.objects.count()
        response = self.client.post(reverse('manage_products'), {
            'action': 'delete_product',
            'product_id': product_id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_products'))
        self.assertEqual(Produto.objects.count(), product_count_before - 1)
        self.assertFalse(Produto.objects.filter(id=product_id).exists())
        self.assertEqual(Oferta.objects.filter(produto=self.produto_manage).count(), 0)

    # --- Testes de Funcionalidade para manage_offers_view ---
    def test_manage_offers_add_new_offer_success(self):
        self.client.login(username='superadmin', password='superpassword')
        offer_count_before = Oferta.objects.count()
        response = self.client.post(reverse('manage_offers'), {
            'action': 'add_or_update',
            'produto': self.produto_manage.id,
            'loja': self.loja_manage.id,
            'preco': '199.99',
            'offer_id_hidden': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_offers'))
        self.assertEqual(Oferta.objects.count(), offer_count_before + 1)
        new_offer = Oferta.objects.get(produto=self.produto_manage, loja=self.loja_manage, preco=decimal.Decimal('199.99'))
        self.assertIsNotNone(new_offer)

    def test_manage_offers_update_existing_offer_success(self):
        self.client.login(username='superadmin', password='superpassword')
        initial_offer = Oferta.objects.create(
            produto=self.produto_manage, loja=self.loja_manage, preco=decimal.Decimal('250.00'), data_captura=timezone.now() - timedelta(days=1)
        )
        offer_count_before = Oferta.objects.count()
        response = self.client.post(reverse('manage_offers'), {
            'action': 'add_or_update',
            'produto': self.produto_manage.id,
            'loja': self.loja_manage.id,
            'preco': '180.50',
            'offer_id_hidden': initial_offer.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_offers'))
        self.assertEqual(Oferta.objects.count(), offer_count_before)
        updated_offer = Oferta.objects.get(id=initial_offer.id)
        self.assertEqual(updated_offer.preco, decimal.Decimal('180.50'))
        self.assertGreater(updated_offer.data_captura, initial_offer.data_captura)

    def test_manage_offers_delete_offer_success(self):
        self.client.login(username='superadmin', password='superpassword')
        offer_to_delete = Oferta.objects.create(
            produto=self.produto_manage, loja=self.loja_manage, preco=decimal.Decimal('50.00')
        )
        offer_count_before = Oferta.objects.count()
        response = self.client.post(reverse('manage_offers'), {
            'action': 'delete_offer',
            'offer_id': offer_to_delete.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_offers'))
        self.assertEqual(Oferta.objects.count(), offer_count_before - 1)
        self.assertFalse(Oferta.objects.filter(id=offer_to_delete.id).exists())


class UserManagementTest(TestCase):
    """
    Testes para a nova view de gerenciamento de usuários (is_staff).
    """
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.superadmin = self.user_model.objects.create_user(
            username='superadmin', email='superadmin@example.com', password='adminpass', is_staff=True, is_superuser=True
        )
        self.normal_user = self.user_model.objects.create_user(
            username='normaluser', email='normal@example.com', password='userpass'
        )
        self.staff_user = self.user_model.objects.create_user(
            username='staffuser', email='staff@example.com', password='staffpass', is_staff=True, is_superuser=False
        )

    # Testes para a view de Registro (sem campo 'role')
    def test_register_view_success_no_role(self):
        user_count_before = self.user_model.objects.count()
        response = self.client.post(reverse('register'), {
            'username': 'newuser_reg',
            'email': 'newuser_reg@example.com',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
            'first_name': 'New',
            'last_name': 'User',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(self.user_model.objects.count(), user_count_before + 1)
        new_user = self.user_model.objects.get(username='newuser_reg')
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)

    # Testes para a nova view de Gerenciamento de Usuários
    def test_manage_users_view_get_authenticated_superadmin(self):
        self.client.login(username='superadmin', password='adminpass')
        response = self.client.get(reverse('manage_users'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gerenciar Usuários")
        self.assertContains(response, self.normal_user.username)
        self.assertContains(response, self.staff_user.username)
        self.assertContains(response, "Tornar Admin")
        self.assertContains(response, "Remover Admin")

    def test_manage_users_view_get_unauthenticated(self):
        response = self.client.get(reverse('manage_users'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/?next=', response.url)

    def test_manage_users_view_get_not_staff(self):
        self.client.login(username='normaluser', password='userpass')
        response = self.client.get(reverse('manage_users'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/?next=', response.url)
    
    def test_manage_users_view_get_staff_not_superuser(self):
        self.client.login(username='staffuser', password='staffpass')
        response = self.client.get(reverse('manage_users'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/?next=', response.url)

    def test_manage_users_make_admin_success(self):
        self.client.login(username='superadmin', password='adminpass')
        self.assertFalse(self.normal_user.is_staff)
        response = self.client.post(reverse('manage_users'), {
            'action': 'make_admin',
            'user_id': self.normal_user.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_users'))
        self.normal_user.refresh_from_db()
        self.assertTrue(self.normal_user.is_staff)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn(f"Usuário '{self.normal_user.username}' agora é um administrador.", str(messages[0]))

    def test_manage_users_remove_admin_success(self):
        self.client.login(username='superadmin', password='adminpass')
        self.assertTrue(self.staff_user.is_staff)
        response = self.client.post(reverse('manage_users'), {
            'action': 'remove_admin',
            'user_id': self.staff_user.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_users'))
        self.staff_user.refresh_from_db()
        self.assertFalse(self.staff_user.is_staff)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn(f"Usuário '{self.staff_user.username}' não é mais um administrador.", str(messages[0]))

    def test_manage_users_cannot_remove_self_admin(self):
        self.client.login(username='superadmin', password='adminpass')
        self.assertTrue(self.superadmin.is_staff)
        response = self.client.post(reverse('manage_users'), {
            'action': 'remove_admin',
            'user_id': self.superadmin.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_users'))
        self.superadmin.refresh_from_db()
        self.assertTrue(self.superadmin.is_staff)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn("Você não pode alterar seu próprio status de administrador.", str(messages[0]))

    def test_manage_users_invalid_user_id(self):
        self.client.login(username='superadmin', password='adminpass')
        response = self.client.post(reverse('manage_users'), {
            'action': 'make_admin',
            'user_id': 99999,
        })
        self.assertEqual(response.status_code, 404)

    def test_manage_users_invalid_action(self):
        self.client.login(username='superadmin', password='adminpass')
        response = self.client.post(reverse('manage_users'), {
            'action': 'invalid_action',
            'user_id': self.normal_user.id,
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn("Ação inválida ou não reconhecida.", str(messages[0]))