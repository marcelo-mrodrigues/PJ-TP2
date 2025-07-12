# core/tests.py

from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from .models import Categoria, Marca, Produto, Loja, Oferta, Usuario
from django.urls import reverse
from django.db import IntegrityError # Importe para testar unique_together
import decimal # Para lidar com valores DecimalFields


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
        initial_count = Categoria.objects.count() # Pega a contagem antes
        categoria = Categoria.objects.create(nome='Livros')
        self.assertEqual(categoria.nome, 'Livros')
        # Agora deve ser o número inicial de categorias (1) + 1 nova
        self.assertEqual(Categoria.objects.count(), initial_count + 1)
        self.assertTrue(isinstance(categoria, Categoria))
        self.assertEqual(str(categoria), 'Livros')

    def test_create_marca(self):
        """
        Testa a criação de uma nova marca.
        """
        initial_count = Marca.objects.count()
        marca = Marca.objects.create(nome='Dell')
        self.assertEqual(marca.nome, 'Dell')
        self.assertEqual(Marca.objects.count(), initial_count + 1)
        self.assertTrue(isinstance(marca, Marca))
        self.assertEqual(str(marca), 'Dell')

    def test_create_product(self): # Renomeei de 'test_ciar_produto_view' para seguir o padrão de teste de modelo
        """
        Testa a criação de um novo Produto.
        """
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
        """
        Testa a criação de uma nova Loja.
        """
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

        oferta_count_before = Oferta.objects.count()
        oferta = Oferta.objects.create(
            produto=produto,
            loja=loja,
            preco=decimal.Decimal('8500.50') # Use Decimal para igualdade precisa
        )
        self.assertIsNotNone(oferta.id)
        self.assertEqual(Oferta.objects.count(), oferta_count_before + 1)
        self.assertEqual(oferta.produto, produto)
        self.assertEqual(oferta.loja, loja)
        self.assertEqual(oferta.preco, decimal.Decimal('8500.50')) # Compare como Decimal
        self.assertIsNotNone(oferta.data_captura)
        self.assertTrue(isinstance(oferta, Oferta))
        expected_str = f"Oferta de Notebook Apple MacBook Air na Amazon Brasil por R$8500.50"
        # O str(oferta) já deve formatar corretamente, sem necessidade de adicionar '0'
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

        # Use timezone.now() para simular a data_captura
        current_time = timezone.now()

        Oferta.objects.create(produto=produto, loja=loja, preco=decimal.Decimal('100.00'), data_captura=current_time)

        # Tentando criar outra oferta exatamente no mesmo produto, loja e data/hora
        with self.assertRaises(IntegrityError): # A exceção esperada é IntegrityError
             Oferta.objects.create(produto=produto, loja=loja, preco=decimal.Decimal('99.00'), data_captura=current_time)
        # O count deve ser 1, pois a segunda tentativa falhou
        self.assertEqual(Oferta.objects.filter(produto=produto, loja=loja).count(), 1)


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
        Oferta.objects.create(produto=produto, loja=loja, preco=decimal.Decimal('300.00'), data_captura=timezone.now())

        # Cria a segunda oferta um segundo depois
        future_time = timezone.now() + timedelta(seconds=1)
        Oferta.objects.create(produto=produto, loja=loja, preco=decimal.Decimal('290.00'), data_captura=future_time)

        # Deve haver duas ofertas para este produto/loja
        self.assertEqual(Oferta.objects.filter(produto=produto, loja=loja).count(), 2)


# Exemplo de teste para verificar o menor preço (usando funções de utils.py se existirem)
# (Mantenha este bloco comentado se seu utils.py ainda usa dados mockados)
class ProductInfoUtilsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crie dados reais no banco para os testes
        cls.admin_user = Usuario.objects.create_user(
            username='testadmin', email='test@example.com', password='password', is_staff=True
        )
        cls.categoria = Categoria.objects.create(nome='Testes')
        cls.loja1 = Loja.objects.create(nome='Loja Teste 1')
        cls.loja2 = Loja.objects.create(nome='Loja Teste 2')
        cls.produto_com_ofertas = Produto.objects.create(
            nome='Produto Teste com Ofertas', categoria=cls.categoria, adicionado_por=cls.admin_user
        )
        # Usamos .create sem data_captura aqui, pois o model tem auto_now_add=True
        # Para garantir que haja diferença no tempo para os testes, criaremos em segundos diferentes
        cls.oferta1 = Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja1, preco=decimal.Decimal('100.00'))
        # Espera um segundo para a próxima oferta para garantir data_captura diferente
        timezone.now() + timedelta(seconds=1) # Simula passagem de tempo
        cls.oferta2 = Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja2, preco=decimal.Decimal('90.00'))
        timezone.now() + timedelta(seconds=1)
        cls.oferta3 = Oferta.objects.create(produto=cls.produto_com_ofertas, loja=cls.loja1, preco=decimal.Decimal('110.00')) # Preço maior

        # Produto sem ofertas
        cls.produto_sem_ofertas = Produto.objects.create(
            nome='Produto Teste sem Ofertas', categoria=cls.categoria, adicionado_por=cls.admin_user
        )

    def test_get_product_info_lowest_price(self):
        """
        Testa se get_product_info retorna o menor preço correto.
        """
        from .utils import get_product_info # Importa aqui para evitar circular imports se utils.py depende de models

        product_info = get_product_info(self.produto_com_ofertas.id)
        self.assertIsNotNone(product_info)
        self.assertEqual(product_info['min_price'], 90.00) # Espera o menor preço das ofertas

    def test_get_product_info_no_offers(self):
        """
        Testa get_product_info para um produto sem ofertas.
        """
        from .utils import get_product_info # Importa aqui

        product_info = get_product_info(self.produto_sem_ofertas.id)
        self.assertIsNotNone(product_info)
        self.assertIsNone(product_info['min_price']) # Espera None se não houver ofertas
        self.assertEqual(len(product_info['offers']), 0)

    def test_search_products(self):
        """
        Testa a função search_products do utils.
        """
        from .utils import search_products

        # Criar alguns produtos extras para testar a busca
        Produto.objects.create(nome='Câmera DSLR', categoria=self.categoria, adicionado_por=self.admin_user, descricao="Ótima para fotos")
        Produto.objects.create(nome='Lente 50mm', categoria=self.categoria, adicionado_por=self.admin_user)
        Loja.objects.create(nome='Loja Câmeras')
        
        # Teste de busca por nome
        results = search_products('câmera')
        self.assertGreaterEqual(len(results), 1)
        self.assertIn('Câmera DSLR', [p['name'] for p in results])

        # Teste de busca vazia (deve retornar todos os produtos)
        all_results = search_products('')
        self.assertEqual(len(all_results), Produto.objects.count()) # Deve retornar todos os produtos existentes

        # Teste de menor preço na busca
        offer_for_camera = Oferta.objects.create(produto=Produto.objects.get(nome='Câmera DSLR'), loja=self.loja1, preco=decimal.Decimal('1500.00'))
        
        results_with_price = search_products('câmera')
        camera_result = next((p for p in results_with_price if p['name'] == 'Câmera DSLR'), None)
        self.assertIsNotNone(camera_result)
        self.assertEqual(camera_result['min_price'], 1500.00) # Converte para float para comparação


class CreateProductViewTest(TestCase): # Renomeei de 'ViewTest' para ser mais específico
    def setUp(self):
        """
        Configura um cliente de teste e usuários para cada método de teste.
        """
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='testuser', email='user@example.com', password='password123'
        )
        self.admin_user = Usuario.objects.create_user(
            username='adminuser', email='admin@example.com', password='adminpassword', is_staff=True, is_superuser=True
        )
        self.categoria = Categoria.objects.create(nome='Livros')
        self.marca = Marca.objects.create(nome='Editora X')

    def test_create_product_view_get_authenticated(self):
        """
        Testa o acesso GET à view de criação de produto por um administrador.
        """
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('create_product')) # Use 'create_product' conforme URL
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar Novo Produto") # Verifica se o título está presente
        self.assertContains(response, '<form method="post"') # Verifica se há um formulário

    def test_create_product_view_get_unauthenticated(self):
        """
        Testa se a view de criação de produto redireciona usuários não autenticados.
        """
        response = self.client.get(reverse('create_product'))
        self.assertEqual(response.status_code, 302) # Deve redirecionar para a página de login
        self.assertIn('/login/?next=', response.url)

    def test_create_product_view_get_not_staff(self):
        """
        Testa se a view de criação de produto redireciona usuários não-staff.
        """
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('create_product'))
        self.assertEqual(response.status_code, 302) # Deve redirecionar para a página de login ou para '/'
        self.assertIn('/login/?next=', response.url)


    def test_create_product_view_post_success(self):
        """
        Testa a submissão POST bem-sucedida do formulário de produto.
        """
        self.client.login(username='adminuser', password='adminpassword')
        product_count_before = Produto.objects.count()

        response = self.client.post(reverse('create_product'), {
            'nome': 'Livro de Teste',
            'descricao': 'Descrição do livro de teste.',
            'imagem_url': 'http://test.com/livro.jpg',
            'categoria': self.categoria.id, # IDs dos objetos criados no setUp
            'marca': self.marca.id,
        })

        self.assertEqual(response.status_code, 302) # Deve redirecionar após o sucesso
        self.assertRedirects(response, reverse('product_catalog')) # Redireciona para o catálogo
        self.assertEqual(Produto.objects.count(), product_count_before + 1) # Um novo produto deve ter sido criado

        new_product = Produto.objects.get(nome='Livro de Teste')
        self.assertEqual(new_product.descricao, 'Descrição do livro de teste.')
        self.assertEqual(new_product.adicionado_por, self.admin_user)
        self.assertEqual(new_product.categoria, self.categoria)
        self.assertEqual(new_product.marca, self.marca)

        # Verifica as mensagens de sucesso
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Produto 'Livro de Teste' adicionado com sucesso!")


    def test_create_product_view_post_invalid(self):
        """
        Testa a submissão POST do formulário de produto com dados inválidos.
        """
        self.client.login(username='adminuser', password='adminpassword')
        product_count_before = Produto.objects.count()

        response = self.client.post(reverse('create_product'), {
            'nome': '', # Nome vazio, deve ser inválido
            'descricao': 'Descrição do livro de teste.',
            'imagem_url': 'http://test.com/livro.jpg',
            'categoria': self.categoria.id,
            'marca': self.marca.id,
        })

        self.assertEqual(response.status_code, 200) # Não redireciona, re-renderiza o formulário
        self.assertEqual(Produto.objects.count(), product_count_before) # Nenhum produto deve ser criado

        # Verifica se as mensagens de erro estão presentes no HTML de resposta
        self.assertContains(response, "Erro no campo &#x27;nome&#x27;: Este campo é obrigatório.") # HTML escaped
        # Opcional: verifica se o formulário renderizado contém os erros
        self.assertContains(response, 'Nome: Este campo é obrigatório.')


class ManageOffersViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = Usuario.objects.create_user(
            username='adminuser', email='admin@example.com', password='adminpassword', is_staff=True, is_superuser=True
        )
        self.product1 = Produto.objects.create(
            nome='Celular XYZ',
            adicionado_por=self.admin_user
        )
        self.product2 = Produto.objects.create(
            nome='Fones Bluetooth',
            adicionado_por=self.admin_user
        )
        self.store1 = Loja.objects.create(nome='Loja A')
        self.store2 = Loja.objects.create(nome='Loja B')

    def test_manage_offers_view_get_authenticated(self):
        """
        Testa o acesso GET à view de gerenciamento de ofertas por um administrador.
        """
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('manage_offers'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gerenciar Ofertas")
        self.assertContains(response, "Adicionar/Atualizar Oferta")
        self.assertContains(response, "Ofertas Existentes")

    def test_manage_offers_view_get_unauthenticated(self):
        """
        Testa se a view de gerenciamento de ofertas redireciona usuários não autenticados.
        """
        response = self.client.get(reverse('manage_offers'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/?next=', response.url)

    def test_manage_offers_view_get_not_staff(self):
        """
        Testa se a view de gerenciamento de ofertas redireciona usuários não-staff.
        """
        self.user = Usuario.objects.create_user(username='normaluser', email='normal@example.com', password='password')
        self.client.login(username='normaluser', password='password')
        response = self.client.get(reverse('manage_offers'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/?next=', response.url)


    def test_manage_offers_add_new_offer_success(self):
        """
        Testa a adição de uma nova oferta.
        """
        self.client.login(username='adminuser', password='adminpassword')
        offer_count_before = Oferta.objects.count()

        response = self.client.post(reverse('manage_offers'), {
            'action': 'add_or_update',
            'produto': self.product1.id,
            'loja': self.store1.id,
            'preco': '199.99',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_offers'))
        self.assertEqual(Oferta.objects.count(), offer_count_before + 1)

        new_offer = Oferta.objects.get(produto=self.product1, loja=self.store1)
        self.assertEqual(new_offer.preco, decimal.Decimal('199.99'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Oferta para '{self.product1.nome}' na '{self.store1.nome}' adicionada com sucesso por R$199.99!")


    def test_manage_offers_update_existing_offer_success(self):
        """
        Testa a atualização de uma oferta existente para o mesmo produto/loja.
        """
        self.client.login(username='adminuser', password='adminpassword')
        
        # Cria uma oferta inicial
        initial_offer = Oferta.objects.create(
            produto=self.product1,
            loja=self.store1,
            preco=decimal.Decimal('250.00'),
            data_captura=timezone.now() - timedelta(days=1) # Data antiga
        )
        offer_count_before = Oferta.objects.count()

        response = self.client.post(reverse('manage_offers'), {
            'action': 'add_or_update',
            'produto': self.product1.id,
            'loja': self.store1.id,
            'preco': '180.50', # Novo preço
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_offers'))
        # A contagem de ofertas não deve mudar, pois foi uma atualização
        self.assertEqual(Oferta.objects.count(), offer_count_before)

        updated_offer = Oferta.objects.get(id=initial_offer.id) # Busca a mesma oferta pelo ID
        self.assertEqual(updated_offer.preco, decimal.Decimal('180.50'))
        self.assertGreater(updated_offer.data_captura, initial_offer.data_captura) # Data de captura deve ser atualizada

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Oferta para '{self.product1.nome}' na '{self.store1.nome}' atualizada com sucesso para R$180.50!")

    def test_manage_offers_delete_offer_success(self):
        """
        Testa a exclusão de uma oferta.
        """
        self.client.login(username='adminuser', password='adminpassword')
        
        # Cria uma oferta para ser excluída
        offer_to_delete = Oferta.objects.create(
            produto=self.product2,
            loja=self.store2,
            preco=decimal.Decimal('50.00')
        )
        offer_count_before = Oferta.objects.count()

        response = self.client.post(reverse('manage_offers'), {
            'action': 'delete_offer',
            'offer_id': offer_to_delete.id,
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manage_offers'))
        self.assertEqual(Oferta.objects.count(), offer_count_before - 1)

        # Tenta buscar a oferta deletada, deve levantar DoesNotExist
        with self.assertRaises(Oferta.DoesNotExist):
            Oferta.objects.get(id=offer_to_delete.id)
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Oferta de '{self.product2.nome}' na '{self.store2.nome}' excluída com sucesso!")

    def test_manage_offers_delete_non_existent_offer(self):
        """
        Testa a exclusão de uma oferta que não existe.
        """
        self.client.login(username='adminuser', password='adminpassword')
        offer_count_before = Oferta.objects.count()

        response = self.client.post(reverse('manage_offers'), {
            'action': 'delete_offer',
            'offer_id': 99999, # ID que não existe
        })

        self.assertEqual(response.status_code, 404) # get_object_or_404 retorna 404 se não encontrar
        self.assertEqual(Oferta.objects.count(), offer_count_before) # Contagem não deve mudar

    def test_manage_offers_add_invalid_data(self):
        """
        Testa a submissão de dados inválidos para adicionar/atualizar oferta.
        """
        self.client.login(username='adminuser', password='adminpassword')
        offer_count_before = Oferta.objects.count()

        response = self.client.post(reverse('manage_offers'), {
            'action': 'add_or_update',
            'produto': self.product1.id,
            'loja': self.store1.id,
            'preco': 'invalido', # Preço inválido
        })

        self.assertEqual(response.status_code, 200) # Re-renderiza a página com erros
        self.assertEqual(Oferta.objects.count(), offer_count_before) # Nenhuma oferta criada/atualizada

        self.assertContains(response, "Erro no campo &#x27;preco&#x27;: Digite um número.")

    def test_manage_offers_edit_prepopulate_form(self):
        """
        Testa se o formulário é pré-preenchido corretamente ao clicar em "Editar".
        """
        self.client.login(username='adminuser', password='adminpassword')
        
        existing_offer = Oferta.objects.create(
            produto=self.product1,
            loja=self.store1,
            preco=decimal.Decimal('123.45')
        )

        response = self.client.post(reverse('manage_offers'), {
            'action': 'edit_offer',
            'offer_id': existing_offer.id,
        })
        
        self.assertEqual(response.status_code, 200) # Deve re-renderizar a página com o formulário populado

        # Verifica se o valor do preço da oferta existente está no input
        self.assertContains(response, f'value="{existing_offer.preco}"')
        
        # Verifica se o produto e loja corretos estão selecionados no formulário
        # Isso é um pouco mais tricky com form.as_p(), mas podemos verificar pelos IDs
        self.assertContains(response, f'<option value="{self.product1.id}" selected="selected">')
        self.assertContains(response, f'<option value="{self.store1.id}" selected="selected">')

        # Verifica a mensagem de informação
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Editando oferta de '{existing_offer.produto.nome}' na '{existing_offer.loja.nome}'.")