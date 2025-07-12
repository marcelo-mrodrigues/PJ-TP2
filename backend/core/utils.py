from .models import Produto, Oferta, Loja, Categoria, Marca # Importar os modelos

def get_product_info(product_id):
    """
    Busca informações detalhadas de um produto por ID do banco de dados,
    incluindo o menor preço e as ofertas.
    """
    try:
        product = Produto.objects.select_related('categoria', 'marca').get(id=product_id)
    except Produto.DoesNotExist:
        return None

    offers = Oferta.objects.filter(produto=product).order_by('preco')

    min_price = offers.first().preco if offers.exists() else None # Pega o preço da primeira oferta (já ordenada)

    product_info = {
        "id": product.id,
        "name": product.nome,
        "imageUrl": product.imagem_url,
        "description": product.descricao,
        "category": product.categoria.nome if product.categoria else None,
        "brand": product.marca.nome if product.marca else None,
        "min_price": float(min_price) if min_price is not None else None, # Converter Decimal para float para JS
        "offers": [
            {"store": offer.loja.nome, "price": float(offer.preco), "date": offer.data_captura.isoformat()}
            for offer in offers
        ]
    }
    return product_info

def search_products(query):
    """
    Busca produtos com base em um termo de consulta, usando o ORM do Django.
    Também calcula o menor preço para cada produto encontrado.
    """
    from django.db.models import Min # Importe Min para agregação

    if not query:
        # Retorna todos os produtos com seu menor preço
        products = Produto.objects.annotate(
            min_price=Min('oferta__preco') # Encontra o menor preço de todas as ofertas para cada produto
        ).select_related('categoria', 'marca').order_by('nome')
    else:
        query = query.lower()
        products = Produto.objects.filter(
            Q(nome__icontains=query) |
            Q(descricao__icontains=query) |
            Q(categoria__nome__icontains=query) |
            Q(marca__nome__icontains=query)
        ).annotate(
            min_price=Min('oferta__preco')
        ).select_related('categoria', 'marca').order_by('nome')

    results = []
    for product in products:
        results.append({
            "id": product.id,
            "name": product.nome,
            "imageUrl": product.imagem_url,
            "description": product.descricao,
            "category": product.categoria.nome if product.categoria else None,
            "brand": product.marca.nome if product.marca else None,
            "min_price": float(product.min_price) if product.min_price is not None else None # Converte Decimal para float
        })
    return results