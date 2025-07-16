"""
Mapeamento de URLs da aplicação 'core'.

Organiza as rotas públicas, autenticadas, de API e de gerenciamento do sistema.
"""

from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # --- Views Públicas e de Autenticação ---
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("produto/<int:product_id>/", views.produto_view, name="produto"),
    path("produto/<int:product_id>/comentar/", views.adicionar_comentario_view, name="comentar_produto"),
    path("buscar/", views.buscar_produtos_view, name="buscar_produtos"),
    path("solicitar-produto/", views.solicitar_produto_view, name="solicitar_produto"),
    path("comentario/<int:comentario_id>/excluir/", views.excluir_comentario_view, name="excluir_comentario"),
    # --- Páginas e APIs do Catálogo ---
    path("catalogo/", views.product_catalog_page_view, name="product_catalog_page"),
    path("api/products/", views.product_catalog_view, name="product_catalog"),
    path("api/produto-dados/<int:product_id>/", views.get_product_data_api, name="get_product_data_api"),

    # --- APIs do Carrinho ---
    path("api/cart/add/", views.add_to_cart_view, name="add_to_cart"),
    path("api/cart/remove/", views.remove_from_cart_view, name="remove_from_cart"),
    path("api/cart/", views.get_cart_view, name="get_cart"),
    path("finalizar-compra/", views.finalizar_compra_view, name="finalizar_compra"),

    # --- URLs da Conta do Usuário Logado ---
    path("conta/perfil/", views.perfil_view, name="perfil"),
    path("conta/lista-compras/", views.lista_de_compras_view, name="lista_de_compras"),
    path("conta/historico-compras/", views.historico_view, name="historico"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("listas/", views.manage_shopping_lists_view, name="manage_shopping_lists"),
    path("lista/<int:item_id>/remover_item/", views.deletar_item_lista, name="deletar_item_lista"),
    path("lista/<int:lista_id>/usar/", views.usar_lista_como_carrinho, name="usar_lista_como_carrinho"),
    path("lista/<int:lista_id>/finalizar/", views.finalizar_lista, name="finalizar_lista"),


    # --- URLs do Painel de Gerenciamento (Apenas Staff) ---
    path("manage/stores/", views.manage_stores_view, name="manage_stores"),
    path("manage/products/", views.manage_products_view, name="manage_products"),
    path("manage/offers/", views.manage_offers_view, name="manage_offers"),
    path("manage/categories/", views.manage_categories_view, name="manage_categories"),
    path("manage/brands/", views.manage_brands_view, name="manage_brands"),
    path("manage/approve-products/", views.aprovar_produto_view, name="ver_aprovar_produtos"),
    path("manage/product-requests/", views.solicitar_produto_view, name="ver_solicitacao_produtos"),
]
