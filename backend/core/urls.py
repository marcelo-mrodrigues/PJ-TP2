# core/urls.py (Versão Recomendada e Organizada)

from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # --- Views Públicas e de Autenticação ---
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("produto/<int:product_id>/", views.produto_view, name="produto"),
    path("buscar/", views.buscar_produtos_view, name="buscar_produtos"),
    path("solicitar-produto/", views.solicitar_produto_view, name="solicitar_produto"),
    path("logout/", views.logout_view, name="logout"),
    # --- API Endpoints (para o Frontend consumir) ---
    path("catalogo/", views.product_catalog_page_view, name="product_catalog_page"),
    path(
        "api/produto-dados/<int:product_id>/",
        views.get_product_data_api,
        name="get_product_data_api",
    ),
    path("api/products/", views.product_catalog_view, name="api_product_list"),
    # core/product_catalog.html
    # --- URLs da Conta do Usuário Logado ---
    path("conta/perfil/", views.perfil_view, name="perfil"),
    path("conta/lista-compras/", views.lista_de_compras_view, name="lista_de_compras"),
    path("conta/historico-compras/", views.historico_view, name="historico"),
    # --- URLs do Painel de Gerenciamento (Apenas Staff) ---
    path("manage/stores/", views.manage_stores_view, name="manage_stores"),
    path("manage/products/", views.manage_products_view, name="manage_products"),
    path("manage/offers/", views.manage_offers_view, name="manage_offers"),
    path("manage/categories/", views.manage_categories_view, name="manage_categories"),
    path("manage/brands/", views.manage_brands_view, name="manage_brands"),
    path(
        "manage/approve-products/",
        views.aprovar_produto_view,
        name="ver_aprovar_produtos",
    ),
    path(
        "manage/product-requests/",
        views.solicitar_produto_view,
        name="ver_solicitacao_produtos",
    ),
]
