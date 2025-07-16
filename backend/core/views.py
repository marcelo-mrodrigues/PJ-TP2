# core/views.py (Adaptado para o seu urls.py)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.utils import timezone
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date
from django.urls import reverse
from .utils import render_lojas_html, process_loja_form, _get_base_html_context
from django.http import JsonResponse
from .models import Produto


# Funções e modelos do seu projeto
from .utils import get_product_info, search_products, merge_session_cart_to_db
from .models import Produto, Oferta, Categoria, Marca, Loja, ItemComprado, ListaCompra, ItemLista
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    ProdutoForm,
    LojaForm,
    OfertaForm,
    CategoriaForm, 
    MarcaForm,
    ListaCompraForm,
    ItemListaForm,
    ComentarioForm,
)
from django.contrib.auth import logout

Usuario = get_user_model()


def get_cart_data(request):
    """Função auxiliar para obter os dados do carrinho da sessão."""
    cart = request.session.get("cart", {})
    cart_items = []
    total_geral = 0

    for product_id, item_data in cart.items():
        try:
            produto = Produto.objects.get(id=product_id)
            oferta = produto.ofertas.order_by("preco").first()

            # Protege contra produto sem oferta
            if oferta:
                preco_unitario = float(oferta.preco)
            else:
                preco_unitario = 0.0

            total_item = item_data["quantity"] * preco_unitario

            cart_items.append(
                {
                    "id": produto.id,
                    "nome": produto.nome,
                    "quantity": item_data["quantity"],
                    "preco": f"{preco_unitario:.2f}",
                    "total_item": f"{total_item:.2f}",
                    "imagem_url": produto.imagem_url,
                }
            )

            total_geral += total_item

        except Produto.DoesNotExist:
            continue  # Ignora produtos deletados

    return {
        "items": cart_items,
        "total": f"{total_geral:.2f}",
        "item_count": sum(item["quantity"] for item in cart.values()),
    }


def add_to_cart_view(request):
    """API para adicionar um item ao carrinho."""
    if request.method == "POST":
        product_id = request.POST.get("product_id")

        # Inicializa o carrinho se não existir
        cart = request.session.get("cart", {})

        if product_id in cart:
            cart[product_id]["quantity"] += 1
        else:
            cart[product_id] = {"quantity": 1}

        request.session["cart"] = cart

        # Retorna os dados atualizados do carrinho
        return JsonResponse(get_cart_data(request))

    return JsonResponse({"error": "Método inválido"}, status=400)


@login_required
def checkout_view(request):
    """
    Exibe a página de finalização de compra.
    Esta view busca os dados do carrinho da sessão e os envia para o template.
    """
    # 1. Busca os dados do carrinho usando nossa função auxiliar
    cart_data = get_cart_data(request)

    # 2. Se o carrinho estiver vazio, redireciona para a página do catálogo com uma mensagem.
    if not cart_data["items"]:
        messages.warning(
            request,
            "Seu carrinho está vazio. Adicione itens antes de finalizar a compra.",
        )
        return redirect("core:product_catalog_page")

    # 3. Cria o contexto para enviar os dados para o template
    context = {"cart": cart_data}

    # 4. Renderiza a página de checkout, passando os dados do carrinho
    return render(request, "core/checkout.html", context)


@login_required
def finalizar_compra_view(request):
    """
    Processa a compra a partir dos dados do carrinho e salva como itens comprados.
    Redireciona para a home ao final.
    """
    if request.method == "POST":
        cart = request.session.get("cart", {})

        if not cart:
            messages.warning(request, "Seu carrinho está vazio.")
            return redirect("core:product_catalog_page")

        for product_id, item_data in cart.items():
            try:
                produto = Produto.objects.get(id=product_id)
                oferta = produto.ofertas.order_by("preco").first()

                ItemComprado.objects.create(
                    usuario=request.user,
                    produto=produto,
                    loja=oferta.loja if oferta else None,
                    preco_pago=oferta.preco if oferta else 0,
                    data_compra=timezone.now().date(),
                )
            except Produto.DoesNotExist:
                continue  # Ignora se o produto foi deletado

        # Limpa o carrinho da sessão
        request.session["cart"] = {}
        messages.success(request, "Compra finalizada com sucesso!")
        return redirect("core:home")

    return redirect("core:checkout")

@login_required
def finalizar_compra_view(request):
    if request.method == "POST":
        cart = request.session.get("cart", {})

        if not cart:
            messages.error(request, "Seu carrinho está vazio.")
            return redirect("core:product_catalog_page")

        for product_id, item_data in cart.items():
            try:
                produto = Produto.objects.get(id=product_id)
                oferta = produto.ofertas.order_by("preco").first()

                ItemComprado.objects.create(
                    usuario=request.user,
                    produto=produto,
                    loja=oferta.loja if oferta else None,
                    preco_pago=oferta.preco if oferta else 0.0,
                    data_compra=date.today(),
                )
            except Produto.DoesNotExist:
                continue  

        # Limpa carrinho
        del request.session["cart"]
        messages.success(request, "Compra finalizada com sucesso!")

        return redirect("core:home")

    # Se alguém acessar via GET, redireciona para o checkout
    return redirect("core:checkout")


def remove_from_cart_view(request):
    """API para remover um item completamente do carrinho."""
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        cart = request.session.get("cart", {})

        if product_id in cart:
            del cart[product_id]  # Remove o item do dicionário

        request.session["cart"] = cart

        # Retorna os dados atualizados do carrinho
        return JsonResponse(get_cart_data(request))

    return JsonResponse({"error": "Método inválido"}, status=400)

def manage_shopping_lists_view(request):
    form_lista = ListaCompraForm()
    form_item = ItemListaForm()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_lista":
            form_lista = ListaCompraForm(request.POST)
            if form_lista.is_valid():
                nova_lista = form_lista.save(commit=False)
                nova_lista.usuario = request.user
                nova_lista.save()
                messages.success(request, f"Lista '{nova_lista.nome}' criada!")
                return redirect("core:manage_shopping_lists")

        elif action == "add_item":
            lista_id = request.POST.get("lista_id")
            lista = get_object_or_404(ListaCompra, id=lista_id, usuario=request.user)
            form_item = ItemListaForm(request.POST)
            if form_item.is_valid():
                novo_item = form_item.save(commit=False)
                novo_item.lista = lista
                try:
                    novo_item.save()
                    messages.success(request, f"Item adicionado à lista '{lista.nome}'!")
                except Exception as e:
                    messages.error(request, "Esse produto já está na lista.")
                return redirect("core:manage_shopping_lists")

        elif action == "delete_item":
            item_id = request.POST.get("item_id")
            item = get_object_or_404(ItemLista, id=item_id, lista__usuario=request.user)
            item.delete()
            messages.success(request, f"Item removido da lista.")
            return redirect("core:manage_shopping_lists")

        elif action == "popular_carrinho":
            lista_id = request.POST.get("lista_id")
            lista = get_object_or_404(ListaCompra, id=lista_id, usuario=request.user)
            session_cart = request.session.get("cart", {})

            for item in lista.itens.all():
                product_id = str(item.produto.id)
                if product_id not in session_cart:
                    session_cart[product_id] = {
                        "quantity": 1,
                        "added_from_list": True
                    }

            request.session["cart"] = session_cart
            messages.success(request, f"Carrinho populado com os itens da lista '{lista.nome}'!")
            return redirect("core:manage_shopping_lists")

    # GET: Renderizar página
    listas = ListaCompra.objects.filter(usuario=request.user).prefetch_related("itens__produto")

    return render(
        request,
        "core/manage_listas.html",
        {
            "form_lista": form_lista,
            "form_item": form_item,
            "listas": listas,
        },
    )

def deletar_item_lista(request, item_id):
    item = get_object_or_404(ItemLista, id=item_id)
    
    if item.lista.usuario == request.user:
        item.delete()
    
    return redirect("core:editar_lista", lista_id=item.lista.id)


def usar_lista_como_carrinho(request, lista_id):
    lista = get_object_or_404(ListaCompra, id=lista_id, usuario=request.user)
    
    cart = request.session.get("cart", {})

    for item in lista.itens.all():
        produto_id = str(item.produto.id)
        if produto_id in cart:
            cart[produto_id]["quantity"] += 1  # ou += item.quantidade se tiver
        else:
            cart[produto_id] = {"quantity": 1}

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("core:ver_carrinho") 

def finalizar_lista(request, lista_id):
    lista = get_object_or_404(ListaCompra, id=lista_id, usuario=request.user)
    lista.finalizada = True
    lista.save()
    return redirect("core:ver_listas")

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
    """Página de login de usuários com redirecionamento e fusão de carrinho."""
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(
                request, f"Login realizado com sucesso, bem-vindo(a) {user.username}!"
            )

            # --- LÓGICA DO CARRINHO ---
            # Transfere o carrinho da sessão para o banco de dados do usuário
            merge_session_cart_to_db(request)

            # --- LÓGICA DE REDIRECIONAMENTO ---
            # Verifica se há um parâmetro 'next' na URL (ex: /login/?next=/checkout/)
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            else:
                # Se não houver, redireciona para a página inicial como padrão
                return redirect("core:home")
        else:
            # Se o formulário for inválido, a própria classe do formulário
            # já gera a mensagem de erro "usuário ou senha inválidos".
            # Não precisamos de uma mensagem extra aqui.
            pass
    else:
        form = CustomAuthenticationForm()

    return render(request, "core/login.html", {"form": form})


def get_cart_view(request):
    """API para buscar os dados atuais do carrinho na sessão."""
    cart_data = get_cart_data(request)  # Reutiliza a função que já criamos
    return JsonResponse(cart_data)


def product_catalog_view(request):
    """API: Retorna os dados do catálogo de produtos em formato JSON."""
    search_query = request.GET.get("q", "")
    produtos_data = search_products(search_query)
    return JsonResponse({"products": produtos_data})



def produto_view(request, product_id):
    endpoint_url = reverse("core:get_product_data_api", args=[product_id])
    produto = get_object_or_404(Produto, id=product_id)
    comentarios = produto.comentarios.select_related("usuario").all()
    form_comentario = ComentarioForm()

    return render(
        request,
        "core/produto.html",
        {
            "product_id": product_id,
            "endpoint_url": endpoint_url,
            "comentarios": comentarios,
            "form_comentario": form_comentario,
        },
    )

def adicionar_comentario_view(request, product_id):
    produto = get_object_or_404(Produto, id=product_id)

    if request.method == "POST":
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.usuario = request.user
            comentario.produto = produto
            comentario.save()
            messages.success(request, "Comentário enviado com sucesso!")
        else:
            messages.error(request, "Erro ao enviar comentário.")
    return redirect("core:produto", product_id=product_id)

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


def manage_categories_view(request):
    form = CategoriaForm()
    additional_info_html = ""

    if request.method == "POST":
        action = request.POST.get("action")
        category_id = request.POST.get("id")

        if action == "edit":
            instance = get_object_or_404(Categoria, id=category_id)
            form = CategoriaForm(instance=instance)
            additional_info_html = f"Editando categoria: <strong>{instance.nome}</strong>"

        elif action == "delete":
            instance = get_object_or_404(Categoria, id=category_id)
            instance.delete()
            messages.success(request, f"Categoria '{instance.nome}' excluída com sucesso!")
            return redirect("core:manage_categories")

        else:
            instance = get_object_or_404(Categoria, id=category_id) if category_id else None
            form = CategoriaForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                messages.success(request, "Categoria salva com sucesso!")
                return redirect("core:manage_categories")
            else:
                messages.error(request, "Erro ao salvar categoria.")

    items = Categoria.objects.all()
    context = {
        "form": form,
        "items": items,
        "title": "Gerenciar Categorias",
        "item_type": "Categoria",
        "additional_info_html": additional_info_html,
    }
    return render(request, "core/manage_generico.html", context)


@staff_member_required
def manage_brands_view(request):
    form = MarcaForm()
    additional_info_html = ""

    if request.method == "POST":
        action = request.POST.get("action")
        brand_id = request.POST.get("id")

        if action == "edit":
            instance = get_object_or_404(Marca, id=brand_id)
            form = MarcaForm(instance=instance)
            additional_info_html = f"Editando marca: <strong>{instance.nome}</strong>"

        elif action == "delete":
            instance = get_object_or_404(Marca, id=brand_id)
            instance.delete()
            messages.success(request, f"Marca '{instance.nome}' excluída com sucesso!")
            return redirect("core:manage_brands")

        else:
            instance = get_object_or_404(Marca, id=brand_id) if brand_id else None
            form = MarcaForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                messages.success(request, "Marca salva com sucesso!")
                return redirect("core:manage_brands")
            else:
                messages.error(request, "Erro ao salvar marca.")

    items = Marca.objects.all()
    context = {
        "form": form,
        "items": items,
        "title": "Gerenciar Marcas",
        "item_type": "Marca",
        "additional_info_html": additional_info_html,
    }
    return render(request, "core/manage_generico.html", context)
