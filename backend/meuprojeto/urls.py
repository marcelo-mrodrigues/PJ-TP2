from django.contrib import admin
from django.urls import path, include

# Configurações para servir arquivos estáticos e de mídia em desenvolvimento
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),  # URL para o painel de administração do Django
    path(
        "", include("core.urls")
    ),  # Inclui as URLs do seu app 'core' na raiz do projeto
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
