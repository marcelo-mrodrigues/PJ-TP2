from .models import Categoria

def categorias_disponiveis(request):
    """
    Processador de contexto que disponibiliza todas as categorias do banco
    para serem acessadas em qualquer template renderizado.

    @param request: objeto HttpRequest
    @return: dicionário com a lista de categorias
    """
    return {'categorias': Categoria.objects.all()}