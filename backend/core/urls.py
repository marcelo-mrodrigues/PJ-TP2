from django.urls import path
from . import views
from core.api import api_views

urlpatterns = [
    path("", views.home_view, name="home"),  # URL para a página inicial
    path(
        "register/", views.register_view, name="register"
    ),  # URL para o formulário de registro
    path("login/", views.login_view, name="login"),  # URL para o formulário de login
    path(
        "product_catalog/", views.product_catalog_view, name="product_catalog"
    ),  # URL para a página one será exibido os produtos
    path("solicitar-produto/", views.solicitar_produto_view, name="solicitar_produto"),
    path("aprovar-produto/", views.aprovar_produto_view, name="aprovar_produto"),
    path("buscar/", views.buscar_produtos_view, name="buscar_produtos"),
    path(
        "solicitacoes-produto/",
        views.solicitacao_produto_view,
        name="ver_solicitacao_produtos",
    ),
    path("produto/<int:product_id>/", views.produto_view, name="produto"),
    path("perfil/", views.perfil_view, name="perfil"),
    path("lista-compras/", views.lista_de_compras_view, name="lista_de_compras"),
    path("historico-compras/", views.historico_view, name="historico"),
    path(
        "catalago_produtos/", views.product_catalog_view2, name="catalogo"
    ),  # pra teste
    # URLs de Gerenciamento (Create/Edit/Delete em uma única view)
    path("gerenciar-lojas/", views.manage_stores_view, name="manage_stores"),
    path("gerenciar-produtos/", views.manage_products_view, name="manage_products"),
    path("gerenciar-ofertas/", views.manage_offers_view, name="manage_offers"),
    path("api/v1/register", api_views.RegisterAPIView.as_view(), name="api-register"),
]
