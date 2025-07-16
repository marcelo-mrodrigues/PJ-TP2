# core/views.py (Adaptado para o seu urls.py)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from .utils import render_lojas_html, process_loja_form, _get_base_html_context


# Funções e modelos do seu projeto
from .utils import get_product_info, search_products
from .models import Produto, Oferta, Categoria, Marca, Loja
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    ProdutoForm,
    LojaForm,
    OfertaForm,
)
from django.contrib.auth import logout

Usuario = get_user_model()


# ================================================================= #
#                  VIEWS DE AUTENTICAÇÃO E PÁGINAS BÁSICAS          #
# ================================================================= #
# (Nenhuma mudança aqui)


def home_view(request):
    """
    Renderiza a página inicial, passando todas as categorias do banco de dados.
    """
    # Busca TODAS as categorias do banco de dados
    categorias = Categoria.objects.all().order_by("nome")  # ordena por nome
    return render(request, "core/home.html", {"categorias": categorias})


def logout_view(request):
    """Faz o logout do usuário e o redireciona para a página inicial."""
    logout(request)
    messages.success(request, "Você saiu da sua conta com sucesso.")
    return redirect("core:home")


def register_view(request):
    """Página de registro de novos usuários."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Usuário {user.username} registrado com sucesso! Faça o login.",
            )
            return redirect("core:login")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = CustomUserCreationForm()
    return render(request, "core/register.html", {"form": form})


def login_view(request):
    """Página de login de usuários."""
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(
                request, f"Login realizado com sucesso, bem-vindo(a) {user.username}!"
            )
            return redirect("core:home")
        else:
            messages.error(request, "Nome de usuário ou senha inválidos.")
    else:
        form = CustomAuthenticationForm()
    return render(request, "core/login.html", {"form": form})


# ================================================================= #
#           VIEWS E API PARA O FRONTEND (CLIENTE FINAL)             #
# ================================================================= #
# (Nomes e lógica adaptados ao seu urls.py)


def product_catalog_view(request):
    """API: Retorna os dados do catálogo de produtos em formato JSON."""
    search_query = request.GET.get("q", "")
    produtos_data = search_products(search_query)
    return JsonResponse({"products": produtos_data})


def produto_view(request, product_id):
    # === CORREÇÃO AQUI: Passar a URL RELATIVA do proxy para o template ===
    # Esta URL deve ser o prefixo do proxy + a URL da API real no Django
    endpoint_url = reverse(
        "core:get_product_data_api", args=[product_id]
    )  # Ex: /api/produto-dados/1/
    # O browser fará o fetch para /api/produto-dados/1/
    # E o next.config.mjs vai reescrever para http://localhost:8000/api/produto-dados/1/

    return render(
        request,
        "core/produto.html",
        {
            "product_id": product_id,
            "endpoint_url": endpoint_url,  # Agora passa a URL relativa do proxy
        },
    )


def get_product_data_api(request, product_id):
    """API: Retorna os detalhes de um produto específico em formato JSON."""
    product_data = get_product_info(product_id)
    if not product_data:
        return JsonResponse({"error": "Produto não encontrado"}, status=404)
    return JsonResponse({"product": product_data})


# ================================================================= #
#                  VIEWS DE PLACEHOLDER (EM CONSTRUÇÃO)             #
# ================================================================= #
# (Todas as suas views de placeholder foram adicionadas)


@login_required(
    login_url="/login/"
)  # Redireciona para a URL de login se o usuário não estiver autenticado
def solicitar_produto_view(request):
    """
    Renderiza o formulário de solicitação de produto e processa o envio.
    Apenas usuários autenticados podem acessar esta view.
    """
    if request.method == "POST":
        nome = request.POST.get("nome")
        descricao = request.POST.get("descricao")
        imagem_url = request.POST.get("imagem_url")
        categoria_nome = request.POST.get("categoria")
        marca_nome = request.POST.get("marca")

        if not nome:
            messages.error(request, "O nome do produto é obrigatório.")
            return render(request, "core/solicitar_produto.html")

        categoria, _ = Categoria.objects.get_or_create(nome=categoria_nome or "Outros")
        marca, _ = Marca.objects.get_or_create(nome=marca_nome or "Genérica")

        Produto.objects.create(
            nome=nome,
            descricao=descricao,
            imagem_url=imagem_url,
            categoria=categoria,
            marca=marca,
            adicionado_por=request.user,
        )

        messages.success(request, "Produto solicitado com sucesso!")
        return redirect("core:ver_solicitacao_produtos")

    return render(request, "core/solicitar_produto.html")


@staff_member_required(
    login_url="/admin/login/"
)  # Redireciona para a URL de login do admin se não for staff
def aprovar_produto_view(request):
    """
    Permite que apenas usuários com status de staff (administradores) aprovem produtos.
    """
    if request.method == "POST":
        produto_id = request.POST.get("produto_id")
        produto = get_object_or_404(Produto, id=produto_id)

        produto.aprovado = True
        produto.save()

        messages.success(request, f"Produto '{produto.nome}' aprovado com sucesso!")
        return redirect("core:ver_aprovar_produtos")

    produtos_pendentes = Produto.objects.filter(aprovado=False)
    return render(
        request, "core/aprovar_produto.html", {"produtos": produtos_pendentes}
    )


def buscar_produtos_view(request):
    # Nota: a busca da API já é feita pela 'product_catalog_view'.
    # Esta seria para uma página de resultados renderizada pelo servidor.
    return render(request, "core/placeholder.html", {"title": "Resultado da Busca"})


def product_catalog_page_view(request):
    """Apenas renderiza a PÁGINA do catálogo. O JS faz o resto."""
    return render(request, "core/product_catalog.html")


def solicitacao_produto_view(request):
    return render(
        request, "core/placeholder.html", {"title": "Ver Solicitações de Produto"}
    )


@login_required
def perfil_view(request):
    return render(request, "core/perfil.html", {"title": "Meu Perfil"})


@login_required
def lista_de_compras_view(request):
    return render(request, "core/placeholder.html", {"title": "Minha Lista de Compras"})


@login_required
def historico_view(request):
    return render(request, "core/placeholder.html", {"title": "Histórico de Compras"})


# ================================================================= #
#          VIEWS DE GERENCIAMENTO (LÓGICA ADAPTADA)                 #
# ================================================================= #
# (Lógica de Adicionar, Editar e Excluir em uma única função/URL)


@staff_member_required
def manage_stores_view(request):
    form = LojaForm()
    additional_info = ""

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_or_update_store":
            form, redirect_needed, additional_info = process_loja_form(request)
            if redirect_needed:
                return redirect("core:manage_stores")

        elif action == "delete_store":
            store_id = request.POST.get("store_id")
            if store_id:
                loja = get_object_or_404(Loja, id=store_id)
                loja.delete()
                messages.success(request, f"Loja '{loja.nome}' excluída com sucesso!")
            return redirect("core:manage_stores")

        elif action == "edit_store":
            store_id = request.POST.get("store_id")
            if store_id:
                loja = get_object_or_404(Loja, id=store_id)
                form = LojaForm(instance=loja)
                additional_info = f"<p>Editando loja: <strong>{loja.nome}</strong></p>"

    lojas = Loja.objects.all().order_by("nome")
    lojas_html = render_lojas_html(request, lojas)

    return render(
        request,
        "core/manage_stores.html",
        _get_base_html_context(
            request,
            "Gerenciar Lojas",
            form_obj=form,
            existing_items_html=lojas_html,
            additional_info_html=additional_info,
        ),
    )


@staff_member_required
def manage_products_view(request):
    form = ProdutoForm()
    additional_info = ""

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "edit":
            product_id = request.POST.get("id")
            instance = get_object_or_404(Produto, id=product_id)
            form = ProdutoForm(instance=instance)
            messages.info(request, f"Editando o produto: {instance.nome}")

        elif action == "delete":
            product_id = request.POST.get("id")
            instance = get_object_or_404(Produto, id=product_id)
            instance.delete()
            messages.success(
                request, f"Produto '{instance.nome}' excluído com sucesso!"
            )
            return redirect("core:manage_products")

        else:  # Adicionar ou salvar edição
            product_id = request.POST.get("product_id_hidden")
            instance = get_object_or_404(Produto, id=product_id) if product_id else None
            form = ProdutoForm(request.POST, instance=instance)
            if form.is_valid():
                product = form.save(commit=False)
                if not instance:
                    product.adicionado_por = request.user
                product.save()
                messages.success(
                    request, f"Produto '{product.nome}' salvo com sucesso!"
                )
                return redirect("core:manage_products")
            else:
                messages.error(request, "Erro ao salvar. Verifique os campos.")

    all_products = Produto.objects.select_related("categoria", "marca").order_by("nome")
    context = {
        "form": form,
        "items": all_products,
        "title": "Gerenciar Produtos",
        "item_type": "Produto",
        "additional_info_html": additional_info,
    }
    return render(request, "core/manage_produtos.html", context)


@staff_member_required
def manage_offers_view(request):
    """Gerencia Ofertas (Adicionar, Listar, Editar e Excluir em uma única URL)."""
    form = OfertaForm()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "edit":
            offer_id = request.POST.get("id")
            instance = get_object_or_404(Oferta, id=offer_id)
            form = OfertaForm(instance=instance)
            messages.info(request, f"Editando oferta: {instance}")

        elif action == "delete":
            offer_id = request.POST.get("id")
            instance = get_object_or_404(Oferta, id=offer_id)
            messages.success(request, f"Oferta '{instance}' excluída com sucesso!")
            instance.delete()
            return redirect("core:manage_offers")

        else:
            offer_id = request.POST.get("offer_id_hidden")
            instance = get_object_or_404(Oferta, id=offer_id) if offer_id else None
            form = OfertaForm(request.POST, instance=instance)
            if form.is_valid():
                offer = form.save()
                messages.success(
                    request, f"Oferta para '{offer.produto.nome}' salva com sucesso!"
                )
                return redirect("core:manage_offers")
            else:
                messages.error(request, "Erro ao salvar. Verifique os campos.")

    all_offers = Oferta.objects.select_related("produto", "loja").order_by(
        "-data_captura"
    )
    context = {
        "form": form,
        "items": all_offers,
        "title": "Gerenciar Ofertas",
        "item_type": "Oferta",
    }
    return render(request, "core/manage_ofertas.html", context)
