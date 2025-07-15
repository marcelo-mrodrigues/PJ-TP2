# core/utils.py (Versão Corrigida e Otimizada)

from .models import Produto, Oferta
from django.db.models import Q, Min


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
