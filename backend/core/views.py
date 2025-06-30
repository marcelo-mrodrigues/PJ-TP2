from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.middleware.csrf import get_token
from django.db.models import Q # Importado Q novamente



from .models import ProdutoIndicado, Produto

from .forms import CustomUserCreationForm
from .forms import CustomAuthenticationForm

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