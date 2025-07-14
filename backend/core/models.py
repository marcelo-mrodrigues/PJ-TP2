# core/models.py (Versão Refinada)

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Importar settings para referenciar o User model

# --- Modelos Principais ---


class Categoria(models.Model):
    # Nenhuma mudança necessária. Está perfeito.
    nome = models.CharField(
        max_length=100, unique=True, verbose_name="Nome da Categoria"
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Marca(models.Model):
    # Nenhuma mudança necessária. Está perfeito.
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Marca")

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Usuario(AbstractUser):
    """
    Modelo de usuário customizado. Herda todos os campos padrão do Django.
    """

    # Tornar o email obrigatório e único é uma ótima prática.
    email = models.EmailField(
        unique=True, blank=False, verbose_name="Endereço de e-mail"
    )

    # MUDANÇA 1: Simplificação dos related_name
    # Não é mais necessário sobrescrever 'groups' e 'user_permissions'
    # O Django já lida com isso automaticamente ao usar um AbstractUser.
    # Remover esses campos simplifica o modelo.

    # O USERNAME_FIELD e REQUIRED_FIELDS estão corretos.
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username


class Produto(models.Model):
    # Nenhuma mudança necessária. Está ótimo.
    nome = models.CharField(max_length=255, verbose_name="Nome do Produto")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    imagem_url = models.URLField(
        max_length=500, blank=True, verbose_name="URL da Imagem"
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoria",
    )
    marca = models.ForeignKey(
        Marca, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Marca"
    )

    # MUDANÇA 2: Usar settings.AUTH_USER_MODEL
    # É a forma mais robusta de referenciar seu modelo de usuário.
    adicionado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Adicionado Por",
    )
    data_adicao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Adição")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Loja(models.Model):
    # Nenhuma mudança necessária. Está ótimo.
    nome = models.CharField(max_length=255, unique=True, verbose_name="Nome da Loja")
    url = models.URLField(max_length=500, blank=True, verbose_name="URL da Loja")
    logo_url = models.URLField(max_length=500, blank=True, verbose_name="URL do Logo")

    class Meta:
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Oferta(models.Model):
    # Nenhuma mudança necessária. Perfeito.
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        verbose_name="Produto",
        related_name="ofertas",
    )
    loja = models.ForeignKey(
        Loja, on_delete=models.CASCADE, verbose_name="Loja", related_name="ofertas"
    )
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    data_captura = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Captura"
    )

    class Meta:
        verbose_name = "Oferta"
        verbose_name_plural = "Ofertas"
        unique_together = ("produto", "loja", "data_captura")
        ordering = ["-data_captura"]

    def __str__(self):
        return f"Oferta de {self.produto.nome} na {self.loja.nome} por R${self.preco}"


class ItemComprado(models.Model):
    # Usar settings.AUTH_USER_MODEL aqui também.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuário"
    )
    loja = models.ForeignKey(
        Loja, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Loja"
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Produto",
    )

    # MUDANÇA 3: Mudar preco_pago para DecimalField
    # É mais seguro e consistente com o modelo Oferta.
    preco_pago = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Preço Pago"
    )
    data_compra = models.DateField(verbose_name="Data da Compra")

    class Meta:
        verbose_name = "Item Comprado"
        verbose_name_plural = "Itens Comprados"
        ordering = ["-data_compra"]

    def __str__(self):
        produto_nome = self.produto.nome if self.produto else "Produto Removido"
        return f"Compra de {produto_nome} por {self.usuario}"


class ListaCompra(models.Model):
    # Usar settings.AUTH_USER_MODEL
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário",
        related_name="listas_de_compra",
    )
    nome = models.CharField(max_length=255, verbose_name="Nome da Lista")
    criada_em = models.DateTimeField(auto_now_add=True, verbose_name="Criada Em")
    finalizada = models.BooleanField(default=False, verbose_name="Finalizada")

    class Meta:
        verbose_name = "Lista de Compra"
        verbose_name_plural = "Listas de Compras"
        ordering = ["finalizada", "-criada_em"]

    def __str__(self):
        return f"Lista '{self.nome}' de {self.usuario}"


class ItemLista(models.Model):
    # Apenas um pequeno ajuste no related_name para clareza
    lista = models.ForeignKey(
        ListaCompra,
        on_delete=models.CASCADE,
        verbose_name="Lista de Compra",
        related_name="itens",
    )
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, verbose_name="Produto"
    )
    item_comprado = models.OneToOneField(
        ItemComprado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Item Comprado Associado",
    )
    observacoes = models.TextField(blank=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Item da Lista"
        verbose_name_plural = "Itens da Lista"
        unique_together = ("lista", "produto")
        ordering = ["lista", "produto__nome"]

    def __str__(self):
        return f"{self.produto.nome} na lista '{self.lista.nome}'"


class Comentario(models.Model):
    # Usar settings.AUTH_USER_MODEL
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuário"
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Produto",
        related_name="comentarios",
    )
    loja = models.ForeignKey(
        Loja,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Loja",
        related_name="comentarios",
    )
    texto = models.TextField(verbose_name="Texto do Comentário")
    nota = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Nota (1 a 5)",
    )
    data = models.DateTimeField(auto_now_add=True, verbose_name="Data do Comentário")

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ["-data"]

    def __str__(self):
        target = (
            f"Produto: {self.produto.nome}"
            if self.produto
            else f"Loja: {self.loja.nome}"
        )
        return f"Comentário de {self.usuario} sobre {target}"


class ProdutoIndicado(models.Model):
    # Usar settings.AUTH_USER_MODEL
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário Indicador",
    )
    nome_produto = models.CharField(
        max_length=255, verbose_name="Nome do Produto Indicado"
    )
    descricao_produto = models.TextField(
        blank=True, verbose_name="Descrição do Produto"
    )
    url_imagem = models.URLField(
        max_length=500, blank=True, verbose_name="URL da Imagem"
    )
    motivacao = models.TextField(blank=True, verbose_name="Motivação da Indicação")
    data_indicacao = models.DateTimeField(
        auto_now_add=True, verbose_name="Data da Indicação"
    )
    status = models.CharField(
        max_length=50,
        default="pendente",
        choices=[
            ("pendente", "Pendente"),
            ("aprovado", "Aprovado"),
            ("rejeitado", "Rejeitado"),
        ],
        verbose_name="Status da Indicação",
    )
    # Nenhuma mudança aqui
    produto_existente = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Produto Existente Relacionado",
    )

    class Meta:
        verbose_name = "Produto Indicado"
        verbose_name_plural = "Produtos Indicados"
        ordering = ["status", "-data_indicacao"]

    def __str__(self):
        return f"Indicação de '{self.nome_produto}' por {self.usuario} ({self.status})"
