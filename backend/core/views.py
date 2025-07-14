# core/views.py (Adaptado para o seu urls.py)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

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
    """Renderiza a página inicial."""
    return render(request, "core/home.html")


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
    """Página que irá exibir um único produto.
    Esta view apenas renderiza o 'esqueleto' da página.
    O JavaScript nesta página será responsável por chamar a API para obter os dados.
    """
    return render(request, "core/produto.html", {"product_id": product_id})


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


def solicitar_produto_view(request):
    return render(request, "core/placeholder.html", {"title": "Solicitar um Produto"})


def aprovar_produto_view(request):
    return render(
        request, "core/placeholder.html", {"title": "Aprovar Produtos Indicados"}
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
    """Gerencia Lojas (Adicionar, Listar, Editar e Excluir em uma única URL)."""
    form = LojaForm()

    if request.method == "POST":
        action = request.POST.get("action")

        # Ação para carregar um item no formulário para edição
        if action == "edit":
            store_id = request.POST.get("id")
            instance = get_object_or_404(Loja, id=store_id)
            form = LojaForm(instance=instance)
            messages.info(request, f"Editando a loja: {instance.nome}")

        # Ação para excluir um item
        elif action == "delete":
            store_id = request.POST.get("id")
            instance = get_object_or_404(Loja, id=store_id)
            messages.success(request, f"Loja '{instance.nome}' excluída com sucesso!")
            instance.delete()
            return redirect("core:manage_stores")

        # Ação para salvar um item (novo ou editado)
        else:  # Ação padrão é salvar
            store_id = request.POST.get("id")
            instance = get_object_or_404(Loja, id=store_id) if store_id else None
            form = LojaForm(request.POST, instance=instance)
            if form.is_valid():
                loja = form.save()
                messages.success(request, f"Loja '{loja.nome}' salva com sucesso!")
                return redirect("core:manage_stores")
            else:
                messages.error(request, "Erro ao salvar. Verifique os campos.")

    all_stores = Loja.objects.all().order_by("nome")
    context = {
        "form": form,
        "items": all_stores,
        "title": "Gerenciar Lojas",
        "item_type": "Loja",
    }
    return render(request, "core/management_page_single_url.html", context)


@staff_member_required
def manage_products_view(request):
    """Gerencia Produtos (Adicionar, Listar, Editar e Excluir em uma única URL)."""
    form = ProdutoForm()

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
            messages.success(
                request, f"Produto '{instance.nome}' excluído com sucesso!"
            )
            instance.delete()
            return redirect("core:manage_products")

        else:
            product_id = request.POST.get("id")
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
                return redirect("manage_products")
            else:
                messages.error(request, "Erro ao salvar. Verifique os campos.")

    all_products = Produto.objects.select_related("categoria", "marca").order_by("nome")
    context = {
        "form": form,
        "items": all_products,
        "title": "Gerenciar Produtos",
        "item_type": "Produto",
    }
    return render(request, "core/management_page_single_url.html", context)


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
            return redirect("manage_offers")

        else:
            offer_id = request.POST.get("id")
            instance = get_object_or_404(Oferta, id=offer_id) if offer_id else None
            form = OfertaForm(request.POST, instance=instance)
            if form.is_valid():
                offer = form.save()
                messages.success(
                    request, f"Oferta para '{offer.produto.nome}' salva com sucesso!"
                )
                return redirect("manage_offers")
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
    return render(request, "core/management_page_single_url.html", context)
