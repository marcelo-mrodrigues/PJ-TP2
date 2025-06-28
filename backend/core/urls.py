from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),  # URL para a página inicial
    path(
        "register/", views.register_view, name="register"
    ),  # URL para o formulário de registro
    path("login/", views.login_view, name="login"),  # URL para o formulário de login
    path(
        "product_catalog/", views.product_catalog_view, name="product_catalog"
    ),  # URL para a página one será exibido os produtos
]
