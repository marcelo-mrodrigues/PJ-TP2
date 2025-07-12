from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.middleware.csrf import get_token
from django.db.models import Q # Importado Q novamente
from django.contrib.admin.views.decorators import staff_member_required # Para exigir que seja staff/admin
from django.contrib.auth.decorators import login_required 


from .utils import get_product_info, search_products
from .models import ProdutoIndicado, Produto

from .forms import CustomUserCreationForm
from .forms import CustomAuthenticationForm
from .forms import ProdutoForm
from .forms import LojaForm
from .forms import OfertaForm

Usuario = get_user_model()

# Se precisar de logout no futuro, adicione de volta.
# Se precisar do modelo Usuario, garanta que seja usado.


# View para a página inicial
def home_view(request):
    """
    Renderiza a página inicial.
    Por enquanto, contém botões para Registro e Login.
    """

    html_content = (
        """<div style="font-family: sans-serif; text-align: center; """
        """margin-top: 50px;">"""
        """<h1>Bem-vindo à Tela Inicial!</h1>"""
        """<p>Esta é uma tela básica para navegação inicial.</p>"""
        """<div style="margin-top: 30px;">"""
        """<a href="/register/" style="padding: 10px 20px; """
        """background-color: #4CAF50; color: white; text-decoration: none; """
        """border-radius: 5px; margin-right: 10px;">Registrar</a>"""
        """<a href="/login/" style="padding: 10px 20px; """
        """background-color: #008CBA; color: white; text-decoration: none; """
        """border-radius: 5px;">Login</a>"""
        """</div>"""
        """</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})


# View para Registro de Usuário (agora usando UserCreationForm)
def register_view(request):
    """
    Permite que novos usuários se registrem usando o formulário customizado.
    Cria um usuário no modelo core.Usuario.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Usuário {user.username} registrado com sucesso! "
                f"Faça login agora.",
            )
            return redirect("login")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm() 

    csrf_token_value = get_token(request)

    messages_html = ""
    if messages.get_messages(request):
        messages_html = "".join([
            f'<p style="color:red;">{msg}</p>'
            for msg in messages.get_messages(request)
        ])

    html_content = (
        f"""<div style="font-family: sans-serif; text-align: center; """
        f"""margin-top: 50px;">"""
        f"""<h2>Registro</h2>"""
        f"""<form method="post" action="">"""
        f"""{messages_html}"""
        f"""{form.as_p()}"""
        f"""<input type="hidden" name="csrfmiddlewaretoken" """
        f"""value="{csrf_token_value}">"""
        f"""<button type="submit" style="padding: 10px 20px; """
        f"""background-color: #28a745; color: white; border: none; """
        f"""border-radius: 5px; cursor: pointer;">Registrar</button>"""
        f"""<br><br>"""
        f"""<a href="/login/" style="color: #007bff; text-decoration: none;">"""
        f"""Já tem uma conta? Faça login.</a>"""
        f"""</form>"""
        f"""</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})



# View para Login de Usuário (agora usando CustomAuthenticationForm)
def login_view(request):
    """
    Permite que usuários existentes façam login usando o formulário customizado.
    Autentica o usuário e inicia a sessão, permitindo login apenas por nome de usuário.
    """
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        # --- INÍCIO: LINHAS TEMPORÁRIAS PARA DEPURAR O LOGIN ---
        print(f"\n--- DEPURANDO LOGIN ---")
        print(f"Dados do formulário recebidos: {request.POST}")
        print(f"Formulário é válido? {form.is_valid()}")
        if not form.is_valid():
            print(f"Erros do formulário: {form.errors.as_data()}")
        # --- FIM: LINHAS TEMPORÁRIAS PARA DEPURAR ---

        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Login realizado com sucesso!")
            return redirect("home")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = CustomAuthenticationForm()

    csrf_token_value = get_token(request)

    messages_html = ""
    if messages.get_messages(request):
        messages_html = "".join([
            f'<p style="color:red;">{msg}</p>'
            for msg in messages.get_messages(request)
        ])

    html_content = (
        f"""<div style="font-family: sans-serif; text-align: center; """
        f"""margin-top: 50px;">"""
        f"""<h2>Login</h2>"""
        f"""<form method="post" action="">"""
        f"""{messages_html}"""
        f"""{form.as_p()}"""
        f"""<input type="hidden" name="csrfmiddlewaretoken" """
        f"""value="{csrf_token_value}">"""
        f"""<button type="submit" style="padding: 10px 20px; """
        f"""background-color: #007bff; color: white; border: none; """
        f"""border-radius: 5px; cursor: pointer;">Entrar</button>"""
        f"""<br><br>"""
        f"""<a href="/register/" style="color: #007bff; text-decoration: none;">"""
        f"""Ainda não tem uma conta? Registre-se.</a>"""
        f"""</form>"""
        f"""</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})

def product_catalog_view(request):
    """
    Exibe o catálogo de produtos com dados fixos. Só para teste.
    """
    produtos_data = [
        {"id": 1, "name": "Livro", "imageUrl": "https://placehold.co/150x150/E0E0E0/333333?text=Livro"},
        {"id": 2, "name": "Smartphone", "imageUrl": "https://placehold.co/150x150/E0E0E0/333333?text=Phone"},
        {"id": 3, "name": "Fone de Ouvido", "imageUrl": "https://placehold.co/150x150/E0E0E0/333333?text=Fone"},
        {"id": 4, "name": "Câmera", "imageUrl": "https://placehold.co/150x150/E0E0E0/333333?text=Camera"},
        {"id": 5, "name": "Teclado", "imageUrl": "https://placehold.co/150x150/E0E0E0/333333?text=Teclado"}
    ]

    ofertas_data = {
        1: [
            {"store": "Livraria Leitura", "price": 40.00, "date": "2025-06-27"},
            {"store": "Submarino", "price": 58.00, "date": "2025-06-26"},
            {"store": "Amazon", "price": 45.00, "date": "2025-06-28"}
        ],
        2: [
            {"store": "Magazine Luiza", "price": 1500.00, "date": "2025-06-28"},
            {"store": "Casas Bahia", "price": 1550.00, "date": "2025-06-27"}
        ],
        3: [
            {"store": "Áudio", "price": 120.00, "date": "2025-06-28"},
            {"store": "Ponto Frio", "price": 125.00, "date": "2025-06-27"}
        ],
        4: [
            {"store": "Kalunga", "price": 800.00, "date": "2025-06-28"},
            {"store": "Canon Store", "price": 820.00, "date": "2025-06-27"}
        ],
        5: [
            {"store": "Kabum", "price": 300.00, "date": "2025-06-28"},
            {"store": "TerabyteShop", "price": 310.00, "date": "2025-06-27"}
        ]
    }

    # Geração dos cards de produtos
    produtos_cards_html = "".join([
        f"""
        <div class="product-card" data-product-id="{produto['id']}">
            <img src="{produto['imageUrl']}" alt="{produto['name']} Imagem">
            <h3>{produto['name']}</h3>
        </div>
        """ for produto in produtos_data
    ])

    html_content = f"""
    <head>
        <title>Catálogo de Produtos</title>
        <style>
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }}
            .product-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 25px;
            }}
            .product-card {{
                padding: 20px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Catálogo de Produtos</h1>
            <p class="welcome">Bem-vindo ao catálogo!</p>
            <div class="search-bar">
                <input type="text" id="searchInput" placeholder="Pesquisar produtos...">
                <button id="searchButton">Pesquisar</button>
            </div>
            <div class="product-grid" id="productGrid">
                {produtos_cards_html}
            </div>
            <div id="offersSection">
                <h2 id="offersTitle"></h2>
                <div id="offersList">
                </div>
            </div>
        </div>
        <script>
            // Dados simulados 
            const productsData = {produtos_data};
            const offersData = {ofertas_data};
            const offersSection = document.getElementById('offersSection');
            const offersTitle = document.getElementById('offersTitle');
            const offersList = document.getElementById('offersList');

            // event listeners nos cards de produto
            function initializeProductCardListeners() {{
                const productCards = document.querySelectorAll('.product-card');
                productCards.forEach(card => {{
                    card.addEventListener('click', () => {{
                        const productId = parseInt(card.dataset.productId);
                        // Apenas pegamos o texto do h3, que é o nome do produto
                        const productName = card.querySelector('h3').textContent;
                        showProductOffers(productId, productName);
                    }});
                }});
            }}

            function showProductOffers(productId, productName) {{
                offersTitle.textContent = `Ofertas para ${{productName}}`;
                offersList.innerHTML = ''; // Limpa ofertas anteriores
                const productOffers = offersData[productId];

                productOffers.sort((a, b) => a.price - b.price); // Ordena por preço
                productOffers.forEach((offer, index) => {{
                    const offerItem = document.createElement('div');
                    offerItem.classList.add('offer-item');
                    offerItem.innerHTML = `
                        <span class="store-name">${{offer.store}}</span>
                        <span class="offer-price">R$ ${{offer.price.toFixed(2).replace('.', ',')}}</span>
                    `;
                    offersList.appendChild(offerItem);
                }});

                offersSection.style.display = 'block';
                offersSection.scrollIntoView({{ behavior: 'smooth' }});
            }}

            // Inicializa os listeners quando a página carrega
            document.addEventListener('DOMContentLoaded', initializeProductCardListeners);
        </script>
    </body>
    </html>
    """
    return render(request, "core/base_html_template.html", {"content": html_content})

def product_catalog_view2(request): #pra teste
    """
    Exibe o catálogo de produtos, agora usando a função search_products.
    """
    search_query = request.GET.get('q', '') # Pega o parâmetro 'q' da URL
    produtos_data = search_products(search_query) # Usa a função de utilitário

    # Geração dos cards de produtos
    produtos_cards_html = "".join([
        f"""
        <div class="product-card" data-product-id="{produto['id']}">
            <img src="{produto['imageUrl']}" alt="{produto['name']} Imagem">
            <h3>{produto['name']}</h3>
            <p>R$ {produto['min_price'] if produto.get('min_price') else 'N/A'}</p>
        </div>
        """ for produto in produtos_data
    ])

    html_content = f"""
    <head>
        <title>Catálogo de Produtos</title>
        <style>
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }}
            .product-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 25px;
            }}
            .product-card {{
                padding: 20px;
                text-align: center;
                border: 1px solid #ddd;
                border-radius: 8px;
                cursor: pointer;
                transition: transform 0.2s ease-in-out;
            }}
            .product-card:hover {{
                transform: translateY(-5px);
            }}
            .product-card img {{
                max-width: 100%;
                height: auto;
                border-radius: 4px;
                margin-bottom: 10px;
            }}
            .product-card h3 {{
                margin: 10px 0;
                font-size: 1.1em;
            }}
            .product-card p {{
                font-weight: bold;
                color: #28a745;
            }}
            .search-bar {{
                margin-bottom: 20px;
                display: flex;
                gap: 10px;
            }}
            .search-bar input[type="text"] {{
                flex-grow: 1;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }}
            .search-bar button {{
                padding: 10px 15px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            #offersSection {{
                margin-top: 40px;
                padding: 20px;
                border: 1px solid #eee;
                border-radius: 8px;
                background-color: #f9f9f9;
                display: none; /* Escondido por padrão */
            }}
            #offersTitle {{
                color: #333;
                margin-bottom: 15px;
            }}
            .offer-item {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px dashed #eee;
            }}
            .offer-item:last-child {{
                border-bottom: none;
            }}
            .store-name {{
                font-weight: bold;
            }}
            .offer-price {{
                color: #28a745;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Catálogo de Produtos</h1>
            <p class="welcome">Bem-vindo ao catálogo!</p>
            <div class="search-bar">
                <input type="text" id="searchInput" placeholder="Pesquisar produtos..." value="{search_query}">
                <button id="searchButton">Pesquisar</button>
            </div>
            <div class="product-grid" id="productGrid">
                {produtos_cards_html}
            </div>
            <div id="offersSection">
                <h2 id="offersTitle"></h2>
                <div id="offersList">
                </div>
            </div>
        </div>
        <script>
            // Os dados agora são buscados dinamicamente ou passados do backend.
            // Para este exemplo, manteremos a simulação JS para ofertas.
            const allProductsData = {produtos_data}; // Passa os produtos filtrados/buscados
            // Em um cenário real, offersData viria de uma API ou do backend para o produto específico
            const offersData = {{
                1: [
                    {{"store": "Livraria Leitura", "price": 40.00, "date": "2025-06-27"}},
                    {{"store": "Submarino", "price": 58.00, "date": "2025-06-26"}},
                    {{"store": "Amazon", "price": 45.00, "date": "2025-06-28"}}
                ],
                2: [
                    {{"store": "Magazine Luiza", "price": 1500.00, "date": "2025-06-28"}},
                    {{"store": "Casas Bahia", "price": 1550.00, "date": "2025-06-27"}}
                ],
                3: [
                    {{"store": "Áudio Perfeito", "price": 120.00, "date": "2025-06-28"}},
                    {{"store": "Ponto Frio", "price": 125.00, "date": "2025-06-27"}}
                ],
                4: [
                    {{"store": "Kalunga", "price": 800.00, "date": "2025-06-28"}},
                    {{"store": "Canon Store", "price": 820.00, "date": "2025-06-27"}}
                ],
                5: [
                    {{"store": "Kabum", "price": 300.00, "date": "2025-06-28"}},
                    {{"store": "TerabyteShop", "price": 310.00, "date": "2025-06-27"}}
                ]
            }};

            const offersSection = document.getElementById('offersSection');
            const offersTitle = document.getElementById('offersTitle');
            const offersList = document.getElementById('offersList');
            const searchInput = document.getElementById('searchInput');
            const searchButton = document.getElementById('searchButton');

            // Event listener para o botão de pesquisa
            searchButton.addEventListener('click', () => {{
                const query = searchInput.value;
                window.location.href = `/product_catalog/?q=${{query}}`;
            }});

            // event listeners nos cards de produto
            function initializeProductCardListeners() {{
                const productCards = document.querySelectorAll('.product-card');
                productCards.forEach(card => {{
                    card.addEventListener('click', () => {{
                        const productId = parseInt(card.dataset.productId);
                        // Redireciona para a página de detalhes do produto
                        window.location.href = `/produto/${{productId}}/`;
                    }});
                }});
            }}

            // Não precisamos mais desta função aqui, pois o clique do card redireciona
            // function showProductOffers(productId, productName) {{ ... }}

            // Inicializa os listeners quando a página carrega
            document.addEventListener('DOMContentLoaded', initializeProductCardListeners);
        </script>
    </body>
    </html>
    """
    return render(request, "core/base_html_template.html", {"content": html_content})

# View para a Tela de Visualização de Solicitações de Produto (Admin)
def solicitar_produto_view(request):
    """
    Placeholder: Permite que usuários solicitem a adição de um novo produto.
    """
    html_content = (
        """<div style="font-family: sans-serif; text-align: center; """
        """margin-top: 50px;">"""
        """<h2>Página de Solicitação de Produto (Em Construção)</h2>"""
        """<p>Esta é uma página de placeholder para a solicitação de produtos.</p>"""
        """<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
        """</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})


# View para a Tela de Aprovação de Produto (Apenas para administradores)
def aprovar_produto_view(request):
    """
    Placeholder: Exibe uma lista de produtos indicados pendentes para aprovação/rejeição.
    """
    html_content = (
        """<div style="font-family: sans-serif; text-align: center; """
        """margin-top: 50px;">"""
        """<h2>Página de Aprovação de Produto (Em Construção)</h2>"""
        """<p>Esta é uma página de placeholder para aprovação de produtos.</p>"""
        """<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
        """</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})


# View para a Tela de Resultado de Busca
def buscar_produtos_view(request):
    """
    Placeholder: Realiza uma busca de produtos com base em um termo e exibe os resultados.
    """
    html_content = (
        """<div style="font-family: sans-serif; text-align: center; """
        """margin-top: 50px;">"""
        """<h2>Página de Busca de Produtos (Em Construção)</h2>"""
        """<p>Esta é uma página de placeholder para resultados de busca.</p>"""
        """<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
        """</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})



# View para a Tela de Visualização de Solicitações de Produto (Admin)
def solicitacao_produto_view(request):
    """
    Placeholder: Exibe uma lista de solicitações de produtos pendentes.
    Apenas para administradores.
    """
    html_content = (
        """<div style="font-family: sans-serif; text-align: center; """
        """margin-top: 50px;">"""
        """<h2>Página de Visualização de Solicitações de Produto (Em Construção)</h2>"""
        """<p>Esta é uma página de placeholder para visualização de solicitações de produtos.</p>"""
        """<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
        """</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})

# View para a Tela de Criação de Produto (Admin)
@staff_member_required # Garante que apenas usuários staff (administradores) acessem
@login_required # Garante que o usuário esteja logado
def ciar_produto_view(request):
    """
    Permite que administradores criem um novo produto.
    Processa o formulário de Produto.
    """
    if request.method == "POST":
        form = ProdutoForm(request.POST)
        if form.is_valid():
            # Não salvamos diretamente aqui, pois 'adicionado_por' é um campo ForeignKey
            # e precisa ser preenchido com o usuário logado.
            product = form.save(commit=False) # commit=False impede o salvamento imediato
            product.adicionado_por = request.user # Associa o produto ao usuário logado
            product.save() # Agora salva o produto com o usuário associado
            messages.success(request, f"Produto '{product.nome}' adicionado com sucesso!")
            return redirect("product_catalog") # Redireciona para o catálogo ou detalhes do produto
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo '{field}': {error}")
    else:
        form = ProdutoForm() # Formulário vazio para requisição GET

    csrf_token_value = get_token(request)

    messages_html = ""
    if messages.get_messages(request):
        messages_html = "".join([
            f'<p style="color:red;">{msg}</p>' # Estilo básico para mensagens de erro
            for msg in messages.get_messages(request)
        ])

    html_content = (
        f"""<div style="font-family: sans-serif; text-align: center; """
        f"""margin-top: 50px;">"""
        f"""<h2>Adicionar Novo Produto</h2>"""
        f"""<form method="post" action="">"""
        f"""{messages_html}"""
        f"""{form.as_p()}""" # Renderiza o formulário como parágrafos
        f"""<input type="hidden" name="csrfmiddlewaretoken" """
        f"""value="{csrf_token_value}">"""
        f"""<button type="submit" style="padding: 10px 20px; """
        f"""background-color: #28a745; color: white; border: none; """
        f"""border-radius: 5px; cursor: pointer;">Adicionar Produto</button>"""
        f"""<br><br>"""
        f"""<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
        f"""</form>"""
        f"""</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})


# View para a Tela do Produto (Usuário/Admin)
def produto_view(request, product_id):
    """
    Exibe os detalhes de um produto específico, usando a função get_product_info.
    """
    product = get_product_info(product_id)

    if not product:
        return render(request, "core/base_html_template.html", {"content": "<h2>Produto não encontrado</h2>"})

    offers_html = ""
    if product["offers"]:
        for offer in product["offers"]:
            offers_html += f"""
            <div class="offer-item">
                <span class="store-name">{offer['store']}</span>
                <span class="offer-price">R$ {offer['price']:.2f}</span>
            </div>
            """
    else:
        offers_html = "<p>Nenhuma oferta encontrada para este produto.</p>"

    html_content = f"""
    <head>
        <title>{product['name']} - Detalhes</title>
        <style>
            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                text-align: center;
            }}
            .product-detail-card {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 20px;
            }}
            .product-detail-card img {{
                max-width: 250px;
                height: auto;
                border-radius: 8px;
            }}
            .product-info {{
                text-align: left;
            }}
            .product-info h2 {{
                color: #333;
                margin-bottom: 10px;
            }}
            .product-info p {{
                color: #555;
                line-height: 1.6;
                margin-bottom: 8px;
            }}
            .product-info .price {{
                font-size: 1.5em;
                font-weight: bold;
                color: #28a745;
                margin-top: 15px;
            }}
            .offers-section {{
                margin-top: 30px;
                text-align: left;
                width: 100%;
            }}
            .offers-section h3 {{
                color: #333;
                margin-bottom: 15px;
            }}
            .offer-item {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px dashed #eee;
            }}
            .offer-item:last-child {{
                border-bottom: none;
            }}
            .store-name {{
                font-weight: bold;
                color: #007bff;
            }}
            .offer-price {{
                color: #28a745;
                font-weight: bold;
                font-size: 1.1em;
            }}
            .comment-section {{
                margin-top: 40px;
                text-align: left;
                width: 100%;
            }}
            .comment-section h3 {{
                color: #333;
                margin-bottom: 15px;
            }}
            .comment-section textarea {{
                width: calc(100% - 22px);
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                min-height: 80px;
                margin-bottom: 10px;
            }}
            .comment-section button {{
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            .admin-actions {{
                margin-top: 30px;
                display: flex;
                gap: 10px;
                justify-content: center;
            }}
            .admin-actions button {{
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            .admin-actions .edit-btn {{
                background-color: #ffc107;
                color: #333;
            }}
            .admin-actions .delete-btn {{
                background-color: #dc3545;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="product-detail-card">
                <img src="{product['imageUrl']}" alt="{product['name']} Imagem">
                <div class="product-info">
                    <h2>{product['name']}</h2>
                    <p><strong>ID:</strong> {product['id']}</p>
                    <p><strong>Descrição:</strong> {product['description']}</p>
                    <p><strong>Categoria:</strong> {product['category']}</p>
                    <p class="price">Menor Preço: R$ {product['min_price']:.2f}</p>
                </div>

                <div class="offers-section">
                    <h3>Ofertas Encontradas</h3>
                    <div id="offersList">
                        {offers_html}
                    </div>
                </div>

                <div class="comment-section">
                    <h3>Deixe seu Comentário</h3>
                    <textarea placeholder="Escreva seu comentário sobre o produto, loja ou ambos..."></textarea>
                    <button>Enviar Comentário</button>
                </div>

                <div class="admin-actions">
                    <button class="edit-btn">Editar Produto</button>
                    <button class="delete-btn">Excluir Produto</button>
                </div>
            </div>
            <br>
            <a href="/product_catalog/" style="color: #007bff; text-decoration: none;">Voltar ao Catálogo</a>
        </div>
    </body>
    </html>
    """
    return render(request, "core/base_html_template.html", {"content": html_content})


# View para a Tela de Perfil (Usuário)
def perfil_view(request):
    """
    Placeholder: Exibe o perfil do usuário logado.
    """
    html_content = (
        """<div style="font-family: sans-serif; text-align: center; """
        """margin-top: 50px;">"""
        """<h2>Página de Perfil (Em Construção)</h2>"""
        """<p>Esta é uma página de placeholder para o perfil do usuário.</p>"""
        """<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
        """</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})

# View para a Tela de Lista de Compras (Usuário)
def lista_de_compras_view(request):
    """
    Placeholder: Exibe a lista de compras do usuário.
    """
    html_content = (
        """<div style="font-family: sans-serif; text-align: center; """
        """margin-top: 50px;">"""
        """<h2>Página de Lista de Compras (Em Construção)</h2>"""
        """<p>Esta é uma página de placeholder para a lista de compras do usuário.</p>"""
        """<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
        """</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})

# View para a Tela de Histórico de Compras (Usuário)
def historico_view(request):
    """
    Placeholder: Exibe o histórico de compras do usuário.
    """
    html_content = (
        """<div style="font-family: sans-serif; text-align: center; """
        """margin-top: 50px;">"""
        """<h2>Página de Histórico de Compras (Em Construção)</h2>"""
        """<p>Esta é uma página de placeholder para o histórico de compras do usuário.</p>"""
        """<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
        """</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})

@staff_member_required
@login_required
def create_loja_view(request):
    if request.method == "POST":
        form = LojaForm(request.POST)
        if form.is_valid():
            loja = form.save()
            messages.success(request, f"Loja '{loja.nome}' adicionada com sucesso!")
            return redirect("home") # Ou para uma lista de lojas
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo '{field}': {error}")
    else:
        form = LojaForm()

    csrf_token_value = get_token(request)
    messages_html = "".join([f'<p style="color:red;">{msg}</p>' for msg in messages.get_messages(request)])

    html_content = (
        f"""<div style="font-family: sans-serif; text-align: center; margin-top: 50px;">"""
        f"""<h2>Adicionar Nova Loja</h2>"""
        f"""<form method="post" action="">"""
        f"""{messages_html}"""
        f"""{form.as_p()}"""
        f"""<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token_value}">"""
        f"""<button type="submit" style="padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">Adicionar Loja</button>"""
        f"""<br><br>"""
        f"""<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
        f"""</form>"""
        f"""</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})

@staff_member_required
@login_required
def create_oferta_view(request):
    if request.method == "POST":
        form = OfertaForm(request.POST)
        if form.is_valid():
            oferta = form.save()
            messages.success(request, f"Oferta para '{oferta.produto.nome}' na '{oferta.loja.nome}' adicionada com sucesso!")
            return redirect("home") # Ou para a página do produto
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo '{field}': {error}")
    else:
        form = OfertaForm()

    csrf_token_value = get_token(request)
    messages_html = "".join([f'<p style="color:red;">{msg}</p>' for msg in messages.get_messages(request)])

    html_content = (
        f"""<div style="font-family: sans-serif; text-align: center; margin-top: 50px;">"""
        f"""<h2>Adicionar Nova Oferta</h2>"""
        f"""<form method="post" action="">"""
        f"""{messages_html}"""
        f"""{form.as_p()}"""
        f"""<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token_value}">"""
        f"""<button type="submit" style="padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">Adicionar Oferta</button>"""
        f"""<br><br>"""
        f"""<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
        f"""</form>"""
        f"""</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})
