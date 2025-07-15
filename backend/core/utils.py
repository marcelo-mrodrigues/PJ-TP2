# core/utils.py (Versão Corrigida e Otimizada)

from .models import Produto, Oferta
from django.db.models import Q, Min
from django.urls import reverse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Loja
from .forms import LojaForm



def get_product_info(product_id):
    """
    Busca informações detalhadas de um produto por ID, incluindo todas as suas ofertas.
    """
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


def search_products(query=""):
    """
    Busca produtos com base em um termo de consulta e anota o menor preço para cada um.
    """
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


def render_lojas_html(request, lojas_queryset):
    """
    Gera o HTML da lista de lojas, com botões de editar e excluir.
    """
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


def process_loja_form(request):
    """
    Processa o formulário da loja (adicionar/editar) e retorna:
    - form: instância do formulário
    - redirect_needed: se precisa redirecionar
    - additional_info: mensagem opcional
    """
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
        info = f"<p>Editando loja: <strong>{instance.nome}</strong></p>" if instance else ""
        return form, False, info
    

def _get_messages_html(request):
    messages_html = ""
    if messages.get_messages(request):
        messages_html = "".join([
            f'<p style="color:{"green" if msg.tags == "success" else "red" if msg.tags == "error" else "blue"};">{msg}</p>'
            for msg in messages.get_messages(request)
        ])
    return messages_html

def _get_action_value_for_form(title):
    """Retorna o valor correto para o campo 'action' do formulário principal."""
    if "Loja" in title:
        return "add_or_update_store"
    elif "Produto" in title:
        return "add_or_update_product"
    elif "Oferta" in title:
        return "add_or_update"
    return "" # Fallback caso o título não corresponda a nenhum

def _get_base_html_context(request, title, form_obj=None, existing_items_html="", additional_info_html=""):
    # Inicializa form_header_text com um valor padrão.
    # Esta linha garante que a variável sempre terá um valor.
    item_type = title.split(' ')[-1].replace('s', '').replace('Oferta', 'Oferta')
    form_header_text = f"Adicionar Novo {item_type}" # Valor padrão (para caso form_obj seja None ou sem pk)

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

            f"""<h3>{form_header_text}</h3>""" # Usa a variável que agora está garantida
            f"""<form method="post" action="">"""
            f"""<input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">"""
            f"""<input type="hidden" name="action" value="{_get_action_value_for_form(title)}">""" # Chamada para função auxiliar de action_value
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