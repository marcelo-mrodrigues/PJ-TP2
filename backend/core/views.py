from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.middleware.csrf import get_token
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse

from .utils import get_product_info, search_products
from .models import ProdutoIndicado, Produto, Oferta, Categoria, Marca, Loja
from .forms import CustomUserCreationForm
from .forms import CustomAuthenticationForm
from .forms import ProdutoForm
from .forms import LojaForm
from .forms import OfertaForm

# Importe também CategoriaForm se for criar manage_categories_view no futuro
# from .forms import CategoriaForm

Usuario = get_user_model()

# Se precisar de logout no futuro, adicione de volta.
# Se precisar do modelo Usuario, garanta que seja usado.


# --- Funções Auxiliares
# --- Funções Auxiliares
def _get_messages_html(request):
    messages_html = ""
    if messages.get_messages(request):
        messages_html = "".join(
            [
                f'<p style="color:{"green" if msg.tags == "success" else "red" if msg.tags == "error" else "blue"};">{msg}</p>'
                for msg in messages.get_messages(request)
            ]
        )
    return messages_html


def _get_base_html_context(
    request, title, form_obj=None, existing_items_html="", additional_info_html=""
):
    # Inicializa form_header_text com um valor padrão.
    # Esta linha garante que a variável sempre terá um valor.
    item_type = title.split(" ")[-1].replace("s", "").replace("Oferta", "Oferta")
    form_header_text = f"Adicionar Novo {item_type}"  # Valor padrão (para caso form_obj seja None ou sem pk)

    if form_obj and form_obj.instance and form_obj.instance.pk:
        # Se form_obj existe, tem uma instância e ela tem uma PK, é uma edição
        form_header_text = f"Editar {item_type}"
    # Não precisamos de um 'else' explícito aqui, pois 'form_header_text' já tem um valor padrão.

    return {
        "content": (
            f"""<div style="font-family: sans-serif; text-align: center; margin-top: 50px; max-width: 800px; margin-left: auto; margin-right: auto; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); border-radius: 8px;">"""
            f"""<h2>{title}</h2>"""
            f"""{_get_messages_html(request)}"""
            f"""{additional_info_html}"""
            f"""<h3>{form_header_text}</h3>"""  # Usa a variável que agora está garantida
            f"""<form method="post" action="">"""
            f"""<input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">"""
            f"""<input type="hidden" name="action" value="{_get_action_value_for_form(title)}">"""  # Chamada para função auxiliar de action_value
            f"""{form_obj.as_p() if form_obj else ''}"""
            f"""<button type="submit" style="padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">Salvar</button>"""
            f"""</form>"""
            f"""<h3 style="margin-top: 40px;">{title.replace('Gerenciar', 'Listar')} Existentes</h3>"""
            f"""<div style="text-align: left; margin-top: 20px;">"""
            f"""{existing_items_html}"""
            f"""</div>"""
            f"""<br><br>"""
            f"""<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
            f"""</div>"""
        )
    }


# === NOVA FUNÇÃO AUXILIAR PARA DETERMINAR O VALOR DO CAMPO 'action' ===
def _get_action_value_for_form(title):
    """Retorna o valor correto para o campo 'action' do formulário principal."""
    if "Loja" in title:
        return "add_or_update_store"
    elif "Produto" in title:
        return "add_or_update_product"
    elif "Oferta" in title:
        return "add_or_update"
    return ""  # Fallback caso o título não corresponda a nenhum


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
    return render(request, "core/home.html")


# View para Registro de Usuário (agora usando UserCreationForm)
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Usuário {user.username} registrado com sucesso! Faça login agora.")
            return redirect("login") # Redireciona para a view de login do Django
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            # Se o formulário for inválido, ele re-renderiza a página com o formulário e erros
    else: # GET request
        form = CustomUserCreationForm() 
    
    # Renderiza o template 'register.html'
    return render(request, "core/register.html", {"form": form})


# View para Login de Usuário (AGORA RENDERIZANDO TEMPLATE DJANGO)
def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.success(request, "Login realizado com sucesso!")
                return redirect("home") # Redireciona para a home do Django
            else:
                messages.error(request, "Nome de usuário ou senha inválidos.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else: # GET request
        form = CustomAuthenticationForm()

    # Renderiza o template 'login.html'
    return render(request, "core/login.html", {"form": form})




def product_catalog_view(request):  # MANTÉM O NOME ORIGINAL
    """
    Retorna os dados do catálogo de produtos em formato JSON.
    Permite busca por query param 'q'.
    """
    search_query = request.GET.get("q", "")  # Pega o parâmetro 'q' da URL
    produtos_data = search_products(
        search_query
    )  # Usa a função de utilitário do utils.py

    # Retorna os dados em formato JSON
    return JsonResponse({"products": produtos_data})


# === A NOVA product_detail_view QUE RETORNA JSON ===
def product_detail_view(request, product_id):  # MANTÉM O NOME ORIGINAL
    """
    Retorna os detalhes de um produto específico em formato JSON,
    usando a função get_product_info do utils.
    """
    product = get_product_info(product_id)  # Esta função vem do utils

    if not product:
        return JsonResponse({"error": "Produto não encontrado"}, status=404)

    # Retorna os dados do produto (já incluindo ofertas e menor preço)
    return JsonResponse({"product": product})


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


# View para a Tela do Produto (Usuário/Admin)
def produto_view(request, product_id):
    return render(request, "core/produto.html", {"product_id": product_id})

def get_product_data_api(request, product_id):
    product_data = get_product_info(product_id) # Usa o utilitário para obter dados
    if not product_data:
        return JsonResponse({"error": "Produto não encontrado"}, status=404)
    return JsonResponse({"product": product_data}) # Retorna o JSON aninhado


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


# --- Views de Gerenciamento Unificadas (Lojas, Produtos, Ofertas) ---


@staff_member_required
@login_required
def manage_stores_view(request):  # Sem store_id como parâmetro na função
    """
    Permite que administradores adicionem, editem ou excluam lojas.
    Apresenta um formulário para nova loja e uma lista das lojas existentes.
    """
    all_stores = Loja.objects.all().order_by("nome")
    stores_list_html = ""
    if all_stores.exists():
        for store in all_stores:
            stores_list_html += f"""
            <div class="item-entry" style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; margin-bottom: 5px;">
                <span>{store.nome} ({store.url})</span>
                <div>
                    <form method="post" action="{reverse('manage_stores')}" style="display: inline-block;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        <input type="hidden" name="action" value="edit_store"> 
                        <input type="hidden" name="store_id" value="{store.id}">
                        <button type="submit" style="background-color: #ffc107; color: #333; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; margin-right: 5px;">Editar</button>
                    </form>
                    <form method="post" action="{reverse('manage_stores')}" style="display: inline-block;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        <input type="hidden" name="action" value="delete_store">
                        <input type="hidden" name="store_id" value="{store.id}">
                        <button type="submit" style="background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">Excluir</button>
                    </form>
                </div>
            </div>
            """
    else:
        stores_list_html = "<p>Nenhuma loja cadastrada ainda.</p>"

    # Inicializa o formulário padrão (para adicionar)
    form = LojaForm()
    additional_info = ""  # Mensagem para indicar edição (se for o caso)

    if request.method == "POST":
        action = request.POST.get("action")  # Obtenha a ação primeiro

        if action == "add_or_update_store":
            # === Lógica de Instância para POST (adicionar ou salvar edição) ===
            store_id_from_post = request.POST.get(
                "store_id_hidden"
            )  # Campo oculto do formulário
            store_instance_for_post = None
            if store_id_from_post:
                store_instance_for_post = get_object_or_404(Loja, id=store_id_from_post)

            form = LojaForm(
                request.POST, instance=store_instance_for_post
            )  # Passa a instância (ou None)

            if form.is_valid():
                loja = form.save()
                messages.success(request, f"Loja '{loja.nome}' salva com sucesso!")
                return redirect("manage_stores")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Erro no campo '{field}': {error}")
                # Se inválido, o form já tem os erros. Apenas re-popula a instância para o template.
                if (
                    store_instance_for_post
                ):  # Se está editando, carrega a instância novamente no form
                    form = LojaForm(
                        instance=store_instance_for_post
                    )  # Isso pré-preenche o form para reexibição
                    additional_info = f"<p style='color:blue;'>Editando loja: <strong>{store_instance_for_post.nome}</strong></p>"

        elif action == "delete_store":
            store_id_to_delete = request.POST.get("store_id")
            if store_id_to_delete:
                try:
                    loja_to_delete = get_object_or_404(Loja, id=store_id_to_delete)
                    loja_name = loja_to_delete.nome
                    loja_to_delete.delete()
                    messages.success(
                        request,
                        f"Loja '{loja_name}' e suas ofertas relacionadas foram excluídas com sucesso!",
                    )
                except Exception as e:
                    messages.error(request, f"Erro ao excluir loja: {e}")
            return redirect("manage_stores")

        elif (
            action == "edit_store"
        ):  # Este é o action quando o botão "Editar" é clicado na lista
            store_id_to_edit = request.POST.get("store_id")
            if store_id_to_edit:
                store_instance_for_edit = get_object_or_404(Loja, id=store_id_to_edit)
                # === AQUI: Pré-popula o formulário principal com a instância para edição ===
                form = LojaForm(instance=store_instance_for_edit)
                additional_info = f"<p style='color:blue;'>Editando loja: <strong>{store_instance_for_edit.nome}</strong></p>"
            # Não há redirect aqui; o fluxo continua para renderizar a página com o formulário populado

    # Renderiza a página
    return render(
        request,
        "core/base_html_template.html",
        _get_base_html_context(
            request,
            "Gerenciar Lojas",
            form_obj=form,  # Passa o formulário (vazio, pré-preenchido ou com erros)
            existing_items_html=stores_list_html,
            additional_info_html=additional_info,
        ),
    )


@staff_member_required
@login_required
def manage_products_view(request):  # *** SEM product_id como parâmetro na função ***
    """
    Permite que administradores adicionem, editem ou excluam produtos.
    Apresenta um formulário para novo produto e uma lista dos produtos existentes.
    """
    all_products = Produto.objects.select_related("categoria", "marca").order_by("nome")
    form = ProdutoForm()  # Formulário padrão para adicionar novo produto
    additional_info = ""  # Mensagem para indicar edição (se for o caso)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_or_update_product":
            # === Lógica de Instância para POST (adicionar ou salvar edição) ===
            product_id_from_post = request.POST.get(
                "product_id_hidden"
            )  # Campo oculto do formulário
            product_instance_for_post = None
            if (
                product_id_from_post
            ):  # Se um ID foi enviado, busca a instância para edição
                product_instance_for_post = get_object_or_404(
                    Produto, id=product_id_from_post
                )

            form = ProdutoForm(
                request.POST, instance=product_instance_for_post
            )  # Passa a instância (ou None)

            if form.is_valid():
                product = form.save(commit=False)
                product.adicionado_por = request.user  # Associa ao usuário logado
                product.save()
                messages.success(
                    request, f"Produto '{product.nome}' salvo com sucesso!"
                )
                return redirect("manage_products")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Erro no campo '{field}': {error}")
                if product_instance_for_post:
                    form = ProdutoForm(instance=product_instance_for_post)
                    additional_info = f"<p style='color:blue;'>Editando produto: <strong>{product_instance_for_post.nome}</strong></p>"

        elif action == "delete_product":
            product_id_to_delete = request.POST.get("product_id")
            if product_id_to_delete:
                try:
                    product_to_delete = get_object_or_404(
                        Produto, id=product_id_to_delete
                    )
                    product_name = product_to_delete.nome
                    product_to_delete.delete()
                    messages.success(
                        request,
                        f"Produto '{product_name}' e suas ofertas relacionadas foram excluídos com sucesso!",
                    )
                except Exception as e:
                    messages.error(request, f"Erro ao excluir produto: {e}")
            return redirect("manage_products")

        elif action == "edit_product":  # Action para o POST de edição
            product_id_to_edit = request.POST.get("product_id")
            if product_id_to_edit:
                product_instance_for_edit = get_object_or_404(
                    Produto, id=product_id_to_edit
                )
                form = ProdutoForm(
                    instance=product_instance_for_edit
                )  # Pré-popula o formulário principal
                additional_info = f"<p style='color:blue;'>Editando produto: <strong>{product_instance_for_edit.nome}</strong></p>"

        else:  # Se a 'action' não for reconhecida
            print(
                f"--- manage_products_view: Ação '{action}' não reconhecida ---"
            )  # <--- ADICIONE ESTE PRINT
            messages.error(
                request, "Ação inválida ou não reconhecida."
            )  # <--- E esta mensagem de erro
            # O formulário será re-renderizado com a mensagem de erro.

    # Construção do HTML para a listagem dos produtos
    products_list_html = ""
    if all_products.exists():
        for product in all_products:
            products_list_html += f"""
            <div class="item-entry" style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; margin-bottom: 5px;">
                <span>{product.nome} (Categoria: {product.categoria.nome if product.categoria else 'N/A'})</span>
                <div>
                    <form method="post" action="{reverse('manage_products')}" style="display: inline-block;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        <input type="hidden" name="action" value="edit_product"> 
                        <input type="hidden" name="product_id" value="{product.id}">
                        <button type="submit" style="background-color: #ffc107; color: #333; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; margin-right: 5px;">Editar</button>
                    </form>
                    <form method="post" action="{reverse('manage_products')}" style="display: inline-block;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        <input type="hidden" name="action" value="delete_product">
                        <input type="hidden" name="product_id" value="{product.id}">
                        <button type="submit" style="background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">Excluir</button>
                    </form>
                </div>
            </div>
            """
    else:
        products_list_html = "<p>Nenhum produto cadastrado ainda.</p>"

    return render(
        request,
        "core/base_html_template.html",
        _get_base_html_context(
            request,
            "Gerenciar Produtos",
            form_obj=form,
            existing_items_html=products_list_html,
            additional_info_html=additional_info,
        ),
    )


@staff_member_required
@login_required
def manage_offers_view(request):
    """
    Permite que administradores adicionem, editem ou excluam ofertas.
    Apresenta um formulário para nova oferta e uma lista das ofertas existentes.
    """
    all_offers = Oferta.objects.select_related("produto", "loja").order_by(
        "produto__nome", "loja__nome", "-data_captura"
    )

    form = OfertaForm()  # Formulário para adicionar nova oferta

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_or_update":
            form = OfertaForm(request.POST)
            if form.is_valid():
                produto = form.cleaned_data["produto"]
                loja = form.cleaned_data["loja"]
                preco = form.cleaned_data["preco"]

                # Lógica de UPSERT:
                # 1. Busca a última oferta para o mesmo produto e loja
                latest_offer = (
                    Oferta.objects.filter(produto=produto, loja=loja)
                    .order_by("-data_captura")
                    .first()
                )  # Pega a mais recente

                if latest_offer:
                    # Se existe uma oferta, atualiza ela
                    latest_offer.preco = preco
                    latest_offer.data_captura = (
                        timezone.now()
                    )  # Atualiza a data de captura
                    latest_offer.save()
                    messages.success(
                        request,
                        f"Oferta para '{produto.nome}' na '{loja.nome}' atualizada com sucesso para R${preco}!",
                    )
                else:
                    # Se não existe, cria uma nova
                    new_offer = form.save()
                    messages.success(
                        request,
                        f"Oferta para '{new_offer.produto.nome}' na '{new_offer.loja.nome}' adicionada com sucesso por R${new_offer.preco}!",
                    )

                return redirect("manage_offers")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Erro no campo '{field}': {error}")
                # Se o formulário for inválido, o mesmo formulário com erros será renderizado novamente.

        elif action == "delete_offer":
            offer_id = request.POST.get("offer_id")
            if offer_id:
                try:
                    offer_to_delete = get_object_or_404(Oferta, id=offer_id)
                    product_name = offer_to_delete.produto.nome
                    loja_name = offer_to_delete.loja.nome
                    offer_to_delete.delete()
                    messages.success(
                        request,
                        f"Oferta de '{product_name}' na '{loja_name}' excluída com sucesso!",
                    )
                except Exception as e:
                    messages.error(request, f"Erro ao excluir oferta: {e}")
            return redirect("manage_offers")

        elif action == "edit_offer":
            # Esta parte é para carregar a oferta no formulário para edição
            # mas o salvamento ainda acontece via 'add_or_update'
            offer_id_to_edit = request.POST.get(
                "offer_id"
            )  # Recebe o ID via POST (do botão Editar)
            if offer_id_to_edit:
                offer_instance = get_object_or_404(Oferta, id=offer_id_to_edit)
                form = OfertaForm(
                    instance=offer_instance
                )  # Popula o formulário com a instância
                messages.info(
                    request,
                    f"Editando oferta de '{offer_instance.produto.nome}' na '{offer_instance.loja.nome}'.",
                )

    csrf_token_value = get_token(request)
    messages_html = "".join(
        [
            f'<p style="color:{"green" if msg.tags == "success" else "red" if msg.tags == "error" else "blue"};">{msg}</p>'
            for msg in messages.get_messages(request)
        ]
    )

    # Construção do HTML para a listagem das ofertas
    offers_list_html = ""
    if all_offers.exists():
        for offer in all_offers:
            offers_list_html += f"""
            <div class="offer-item" style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; margin-bottom: 5px;">
                <span>{offer.produto.nome} na {offer.loja.nome} por <strong>R$ {offer.preco:.2f}</strong> (Capturado em: {offer.data_captura.strftime('%d/%m/%Y %H:%M')})</span>
                <div>
                    <form method="post" action="" style="display: inline-block;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token_value}">
                        <input type="hidden" name="action" value="edit_offer">
                        <input type="hidden" name="offer_id" value="{offer.id}">
                        <button type="submit" style="background-color: #ffc107; color: #333; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; margin-right: 5px;">Editar</button>
                    </form>
                    <form method="post" action="" style="display: inline-block;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token_value}">
                        <input type="hidden" name="action" value="delete_offer">
                        <input type="hidden" name="offer_id" value="{offer.id}">
                        <button type="submit" style="background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">Excluir</button>
                    </form>
                </div>
            </div>
            """
    else:
        offers_list_html = "<p>Nenhuma oferta cadastrada ainda.</p>"

    html_content = (
        f"""<div style="font-family: sans-serif; text-align: center; margin-top: 50px; max-width: 800px; margin-left: auto; margin-right: auto; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); border-radius: 8px;">"""
        f"""<h2>Gerenciar Ofertas</h2>"""
        f"""{messages_html}"""
        f"""<h3>Adicionar/Atualizar Oferta</h3>"""
        f"""<form method="post" action="">"""
        f"""<input type="hidden" name="action" value="add_or_update">"""
        f"""{form.as_p()}"""
        f"""<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token_value}">"""
        f"""<button type="submit" style="padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">Salvar Oferta</button>"""
        f"""</form>"""
        f"""<h3 style="margin-top: 40px;">Ofertas Existentes</h3>"""
        f"""<div style="text-align: left; margin-top: 20px;">"""
        f"""{offers_list_html}"""
        f"""</div>"""
        f"""<br><br>"""
        f"""<a href="/" style="color: #007bff; text-decoration: none;">Voltar para a Home</a>"""
        f"""</div>"""
    )
    return render(request, "core/base_html_template.html", {"content": html_content})
