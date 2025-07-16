## @file core/utils.py
#
# @brief Contém funções utilitárias para manipulação de dados e lógica de negócio do aplicativo 'core'.
#
# Este arquivo agrupa funções auxiliares que interagem com os modelos do Django
# para buscar informações de produtos, gerenciar o carrinho de compras na sessão,
# realizar buscas no catálogo e renderizar componentes HTML para o backend.
#
# @see core.models
# @see core.forms

from .models import Produto, Oferta
from django.db.models import Q, Min
from django.urls import reverse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Loja
from .forms import LojaForm
from .models import Produto, ListaCompra, ItemLista


## @brief Busca informações detalhadas de um produto por ID, incluindo todas as suas ofertas.
#
# @param product_id O ID do produto a ser buscado.
# @return Um dicionário contendo os detalhes do produto, seu menor preço e uma lista de ofertas,
#         ou None se o produto não for encontrado.
def get_product_info(product_id):
    try:
        # Usar prefetch_related para ofertas é mais eficiente quando há muitos resultados
        produto = (
            Produto.objects.select_related("categoria", "marca")
            .prefetch_related("ofertas__loja")
            .get(id=product_id)
        )
    except Produto.DoesNotExist:
        return None

    # Graças ao prefetch_related, esta consulta não fará um novo hit no banco
    ofertas = sorted(produto.ofertas.all(), key=lambda o: o.preco)

    ofertas_data = []
    for oferta in ofertas:
        ofertas_data.append(
            {
                "loja": oferta.loja.nome,
                "preco": float(f"{oferta.preco:.2f}"),
                "data_captura": oferta.data_captura.isoformat(),
            }
        )

    produto_info = {
        "id": produto.id,
        "nome": produto.nome,
        "imagem_url": produto.imagem_url,
        "descricao": produto.descricao,
        "categoria": produto.categoria.nome if produto.categoria else None,
        "marca": produto.marca.nome if produto.marca else None,
        "menor_preco": (
            float(ofertas[0].preco) if ofertas else None
        ),  # Converte Decimal para float
        "ofertas": ofertas_data,
    }
    return produto_info


## @brief Transfere o conteúdo do carrinho da sessão para o carrinho permanente do usuário no banco de dados.
#
# Esta função é chamada após o login de um usuário para mesclar itens
# que foram adicionados ao carrinho enquanto o usuário estava anônimo.
#
# @param request O objeto HttpRequest do Django, contendo a sessão e o usuário.
def merge_session_cart_to_db(request):
    if "cart" in request.session and request.user.is_authenticated:
        session_cart = request.session.get("cart", {})

        if not session_cart:
            return  # Sai se o carrinho da sessão estiver vazio

        # Pega ou cria a lista de compras ativa do usuário
        user_cart, created = ListaCompra.objects.get_or_create(
            usuario=request.user, finalizada=False
        )

        for product_id, item_data in session_cart.items():
            try:
                produto = Produto.objects.get(id=product_id)
                quantidade_sessao = item_data.get("quantity", 1)

                # Verifica se o item já existe no carrinho do banco de dados
                item_bd, item_created = ItemLista.objects.get_or_create(
                    lista=user_cart, produto=produto
                )

                if item_created:
                    # Se o item foi criado agora, define a quantidade da sessão
                    item_bd.quantidade = quantidade_sessao
                else:
                    # Se o item já existia, soma as quantidades
                    item_bd.quantidade += quantidade_sessao

                item_bd.save()

            except Produto.DoesNotExist:
                continue  # Pula para o próximo item se o produto não existir mais

        # Limpa o carrinho da sessão após a fusão
        del request.session["cart"]


## @brief Busca produtos com base em um termo de consulta e anota o menor preço para cada um.
#
# A busca é realizada nos campos de nome, descrição, nome da categoria e nome da marca.
#
# @param query O termo de busca (string). Se vazio, retorna todos os produtos.
# @return Uma lista de dicionários, onde cada dicionário representa um produto
#         com suas informações básicas e o menor preço encontrado em suas ofertas.
def search_products(query=""):
    # Começa com todos os produtos
    produtos = Produto.objects.all()

    # Se houver um termo de busca, aplica o filtro
    if query:
        produtos = produtos.filter(
            Q(nome__icontains=query)
            | Q(descricao__icontains=query)
            | Q(categoria__nome__icontains=query)
            | Q(marca__nome__icontains=query)
        ).distinct()

    # Anota o menor preço e otimiza a consulta DEPOIS de filtrar
    # CORREÇÃO APLICADA AQUI: 'ofertas__preco' (plural)
    produtos_anotados = (
        produtos.annotate(menor_preco=Min("ofertas__preco"))
        .select_related("categoria", "marca")
        .order_by("nome")
    )

    # Monta a lista de resultados
    results = []
    for produto in produtos_anotados:
        results.append(
            {
                "id": produto.id,
                "nome": produto.nome,
                "imagem_url": produto.imagem_url,
                "descricao": produto.descricao,
                "categoria": produto.categoria.nome if produto.categoria else None,
                "marca": produto.marca.nome if produto.marca else None,
                "menor_preco": (
                    float(produto.menor_preco)
                    if produto.menor_preco is not None
                    else None
                ),
            }
        )
    return results


## @brief Gera o HTML para exibir uma lista de lojas, com botões de editar e excluir.
#
# Esta função é utilizada em views de gerenciamento para renderizar dinamicamente
# a lista de lojas existentes.
#
# @param request O objeto HttpRequest do Django, necessário para obter o token CSRF.
# @param lojas_queryset Um QuerySet de objetos Loja a serem renderizados.
# @return Uma string HTML representando a lista de lojas.
def render_lojas_html(request, lojas_queryset):
    if not lojas_queryset.exists():
        return "<p>Nenhuma loja cadastrada ainda.</p>"

    html = ""
    for loja in lojas_queryset:
        html += f"""
        <div class="d-flex justify-content-between align-items-center mb-2 p-2 border-bottom">
            <span>{loja.nome} (<a href="{loja.url}" target="_blank">{loja.url}</a>)</span>
            <div>
                <form method="post" action="{reverse('core:manage_stores')}" style="display:inline;">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                    <input type="hidden" name="action" value="edit_store"> 
                    <input type="hidden" name="store_id" value="{loja.id}">
                    <button type="submit" class="btn btn-warning btn-sm me-2">Editar</button>
                </form>
                <form method="post" action="{reverse('core:manage_stores')}" style="display:inline;">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                    <input type="hidden" name="action" value="delete_store">
                    <input type="hidden" name="store_id" value="{loja.id}">
                    <button type="submit" class="btn btn-danger btn-sm">Excluir</button>
                </form>
            </div>
        </div>
        """
    return html


## @brief Processa o envio de um formulário de Loja (adição ou edição).
#
# Esta função encapsula a lógica de validação e salvamento de formulários de loja,
# retornando o formulário, um indicador de redirecionamento e mensagens adicionais.
#
# @param request O objeto HttpRequest do Django, contendo os dados POST.
# @return Uma tupla contendo:
#         - form (LojaForm): A instância do formulário processado.
#         - redirect_needed (bool): True se o formulário foi salvo com sucesso e um redirecionamento é necessário.
#         - additional_info (str): Uma string HTML com informações adicionais ou mensagens de erro.
def process_loja_form(request):
    store_id = request.POST.get("store_id_hidden")
    instance = get_object_or_404(Loja, id=store_id) if store_id else None
    form = LojaForm(request.POST, instance=instance)

    if form.is_valid():
        loja = form.save()
        messages.success(request, f"Loja '{loja.nome}' salva com sucesso!")
        return form, True, ""
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"Erro no campo '{field}': {error}")
        info = (
            f"<p>Editando loja: <strong>{instance.nome}</strong></p>"
            if instance
            else ""
        )
        return form, False, info


## @brief Gera o HTML formatado para exibir as mensagens do Django.
#
# Converte as mensagens de `django.contrib.messages` em uma string HTML com estilos básicos.
#
# @param request O objeto HttpRequest do Django, de onde as mensagens são obtidas.
# @return Uma string HTML contendo todas as mensagens formatadas.
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


## @brief Retorna o valor correto para o campo 'action' de um formulário principal de gerenciamento.
#
# Baseia-se no título da página para determinar a ação (adicionar ou editar)
# para diferentes tipos de entidades (Loja, Produto, Oferta).
#
# @param title O título da página de gerenciamento (ex: "Gerenciar Lojas", "Gerenciar Produtos").
# @return Uma string representando o valor da ação do formulário.
def _get_action_value_for_form(title):
    """Retorna o valor correto para o campo 'action' do formulário principal."""
    if "Loja" in title:
        return "add_or_update_store"
    elif "Produto" in title:
        return "add_or_update_product"
    elif "Oferta" in title:
        return "add_or_update"
    return ""  # Fallback caso o título não corresponda a nenhum


## @brief Retorna um dicionário de contexto para renderizar templates HTML base de gerenciamento.
#
# Esta função auxilia na construção de páginas de gerenciamento que incluem um formulário
# (para adicionar/editar), uma lista de itens existentes e mensagens.
#
# @param request O objeto HttpRequest do Django.
# @param title O título da página (ex: "Gerenciar Lojas").
# @param form_obj Uma instância de Django Form (opcional), usada para renderizar o formulário.
# @param existing_items_html Uma string HTML com a lista de itens existentes.
# @param additional_info_html Uma string HTML com informações adicionais a serem exibidas.
# @return Um dicionário contendo o contexto necessário para o template.
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
