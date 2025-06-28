from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.middleware.csrf import get_token

# Removido import de logout (F401) e Usuario (F401) pois não são usados diretamente aqui
# Se precisar de logout no futuro, adicione de volta.
# Se precisar do modelo Usuario, garanta que seja usado.


# View para a página inicial
def home_view(request):
    """
    Renderiza a página inicial.
    Por enquanto, contém botões para Registro e Login.
    """
    # Linhas de html_content divididas para E501
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
    Permite que novos usuários se registrem usando o formulário padrão do Django.
    Cria um usuário no modelo django.contrib.auth.models.User.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Salva o usuário. Variável 'user' é usada para msgs.
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
        form = UserCreationForm()

    csrf_token_value = get_token(request)

    # NOVO: Gera o HTML das mensagens separadamente para evitar linhas longas
    messages_html = ""
    if messages.get_messages(request):
        messages_html = "".join(
            [
                f'<p style="color:red;">{msg}</p>'
                for msg in messages.get_messages(request)
            ]
        )

    # Linhas longas de f-string divididas para E501
    html_content = (
        f"""<div style="font-family: sans-serif; text-align: center; """
        f"""margin-top: 50px;">"""
        f"""<h2>Registro</h2>"""
        f"""<form method="post" action="">"""
        f"""{messages_html}"""  # Usa a variável gerada
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


# View para Login de Usuário (agora usando AuthenticationForm)
def login_view(request):
    """
    Permite que usuários existentes façam login usando o formulário padrão do Django.
    Autentica o usuário e inicia a sessão.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login realizado com sucesso!")
                return redirect("product_catalog")
            else:
                messages.error(request, "Nome de usuário ou senha inválidos.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = AuthenticationForm()

    csrf_token_value = get_token(request)

    # NOVO: Gera o HTML das mensagens separadamente para evitar linhas longas
    messages_html = ""
    if messages.get_messages(request):
        messages_html = "".join(
            [
                f'<p style="color:red;">{msg}</p>'
                for msg in messages.get_messages(request)
            ]
        )

    # Linhas longas de f-string divididas para E501
    html_content = (
        f"""<div style="font-family: sans-serif; text-align: center; """
        f"""margin-top: 50px;">"""
        f"""<h2>Login</h2>"""
        f"""<form method="post" action="">"""
        f"""{messages_html}"""  # Usa a variável gerada
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
    Exibe o catálogo de produtos apenas para usuários autenticados.
    O decorador @login_required verifica automaticamente se o usuário está logado.
    Se não estiver, redireciona para a tela de login.
    """

    # Exemplo de produtos simples
    produtos = [
        {"nome": "Produto 1", "preco": "R$ 10,00"},
        {"nome": "Produto 2", "preco": "R$ 20,00"},
        {"nome": "Produto 3", "preco": "R$ 30,00"},
        {"nome": "Produto 4", "preco": "R$ 40,00"},
        {"nome": "Produto 5", "preco": "R$ 50,00"},
        {"nome": "Produto 6", "preco": "R$ 60,00"},
        {"nome": "Produto 7", "preco": "R$ 70,00"},
        {"nome": "Produto 8", "preco": "R$ 80,00"},
        {"nome": "Produto 9", "preco": "R$ 90,00"},
        {"nome": "Produto 10", "preco": "R$ 100,00"},
    ]

    # Grid de produtos
    produtos_html = "".join(
        [
            f"""<div style='border:1px solid #ddd; border-radius:8px;
            padding:16px; margin:8px; background:#fafafa; min-width:150px;'>
                <strong>{p['nome']}</strong><br>
                <span>{p['preco']}</span>
            </div>"""
            for p in produtos
        ]
    )

    html_content = (
        f"""<div style="font-family: sans-serif;
        text-align: center; margin-top: 50px;">"""
        f"""<h2>Catálogo de Produtos</h2>"""
        f"""<p>Bem-vindo ao catálogo!</p>"""
        f"""<div style="margin-bottom: 20px;">"""
        f"""<input type="text" placeholder="Pesquisar produtos..." """
        f"""style="width: 300px; padding: 8px; border-radius: 5px;
        border: 1px solid #ccc;">"""
        f"""<button style="padding: 8px 16px; border-radius: 5px; border: none;
        background: #007bff; color: white; cursor: pointer;">Pesquisar</button>"""
        f"""</div>"""
        f"""<div style="display: flex; flex-wrap: wrap; gap: 16px;
        justify-content: center;"""
        f"""max-height: 300px; overflow-y: auto; border: 1px solid #eee;
        border-radius: 8px; padding: 16px; background: #fff;">"""
        f"""{produtos_html}"""
        f"""</div>"""
        f"""</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})
