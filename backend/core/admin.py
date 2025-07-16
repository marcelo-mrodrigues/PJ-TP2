##
# @file admin.py
# @brief Registro dos modelos no Django Admin.
# 
# Este arquivo configura os modelos que estarão disponíveis no painel administrativo do Django.
# Permite que administradores visualizem, editem e gerenciem instâncias dos modelos via interface web.
#
# @date 2025-07-15
##

from django.contrib import admin

# Importe seus modelos para registrá-los no Django Admin
from .models import (
    Categoria, 
    Marca,
    Produto,
    Usuario,
    Loja,
    Oferta,
    ItemComprado,
    ListaCompra,
    ItemLista,
    Comentario,
    ProdutoIndicado,
)

# Registre seus modelos aqui para que apareçam no painel de administração do Django.
# Exemplo básico de registro:
admin.site.register(Categoria)
admin.site.register(Marca)
admin.site.register(Produto)
admin.site.register(Usuario)
admin.site.register(Loja)
admin.site.register(Oferta)
admin.site.register(ItemComprado)
admin.site.register(ListaCompra)
admin.site.register(ItemLista)
admin.site.register(Comentario)
admin.site.register(ProdutoIndicado)

# Para um controle mais granular no Admin, você pode usar ModelAdmin
# Exemplo:
# @admin.register(Produto)
# class ProdutoAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'categoria', 'marca', 'adicionado_por', 'data_adicao')
#     list_filter = ('categoria', 'marca')
#     search_fields = ('nome', 'descricao')
