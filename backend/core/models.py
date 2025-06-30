from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import (
    Group,
    Permission,
)  # Importar Group e Permission para related_name


# --- Modelos Baseados nas Suas Tabelas do Banco de Dados ---


class Categoria(models.Model):
    """
    Representa as categorias de produtos.
    Ex: Eletrônicos, Roupas, Alimentos.
    """

    id = models.AutoField(primary_key=True)
    nome = models.CharField(
        max_length=100, unique=True, verbose_name="Nome da Categoria"
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]  # Ordena por nome por padrão

    def __str__(self):
        return self.nome


class Marca(models.Model):
    """
    Representa as marcas dos produtos.
    Ex: Apple, Samsung, Nike.
    """

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Marca")

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Usuario(AbstractUser):
    """
    Representa um usuário do sistema, integrado ao sistema de autenticação do Django.
    Herda campos como username, password, email, is_staff, is_active, etc.
    """

    email = models.EmailField(
        unique=True, blank=False, null=False, verbose_name="Email"
    )

    role = models.BooleanField(default=False, verbose_name="É Administrador/Gerente")

    # MUDANÇA AQUI: Define o campo usado para login como 'username'
    USERNAME_FIELD = 'username'

    # Campos que serão solicitados ao criar um usuário via createsuperuser
    # 'username' é o USERNAME_FIELD, então ele já é incluído.
    # 'email' é adicionado aqui para ser obrigatório no createsuperuser.
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    # Adiciona related_name para evitar conflitos com auth.User
    groups = models.ManyToManyField(
        Group,
        verbose_name="Grupos",
        blank=True,
        help_text=(
            "Os grupos aos quais este usuário pertence. Um usuário obterá "
            "todas as permissões concedidas a cada um de seus grupos."
        ),
        related_name="core_usuario_set",  # Nome relacionado único para Usuario.groups
        related_query_name="usuario",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="Permissões de Usuário",
        blank=True,
        help_text="Permissões específicas para este usuário.",
        related_name="core_usuario_permissions",  # Nome relacionado único
        related_query_name="usuario_permission",
    )

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username # USAR username se first_name/last_name vazios


class Produto(models.Model):
    """
    Representa um produto disponível no site.
    Possui informações detalhadas e links para categoria, marca e o usuário
    administrador que o adicionou.
    """

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255, verbose_name="Nome do Produto")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    imagem_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="URL da Imagem"
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
    # Referencia o novo modelo Usuario que é o AUTH_USER_MODEL
    adicionado_por = models.ForeignKey(
        "core.Usuario",  # Referencia o modelo 'Usuario' customizado
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
    """
    Representa uma loja onde os produtos são vendidos ou ofertados.
    """

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255, verbose_name="Nome da Loja")
    url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="URL da Loja"
    )
    logo_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="URL do Logo"
    )

    class Meta:
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Oferta(models.Model):
    """
    Registra uma oferta de um produto em uma loja específica, com seu preço e
    data de captura.
    """

    id = models.AutoField(primary_key=True)
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, verbose_name="Produto"
    )
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, verbose_name="Loja")
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

        return (
            f"Oferta de {self.produto.nome} na {self.loja.nome} " f"por R${self.preco}"
        )


class ItemComprado(models.Model):
    """
    Registra um item que foi efetivamente comprado por um usuário.
    """

    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "core.Usuario", on_delete=models.CASCADE, verbose_name="Usuário"
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
    preco_pago = models.IntegerField(verbose_name="Preço Pago (em centavos ou similar)")
    data_compra = models.DateField(verbose_name="Data da Compra")

    class Meta:
        verbose_name = "Item Comprado"
        verbose_name_plural = "Itens Comprados"
        ordering = ["-data_compra"]

    def __str__(self):

        return (
            f"Compra de {self.produto.nome if self.produto else 'Produto Desconhecido'} "
            f"por {self.usuario.first_name if self.usuario.first_name else self.usuario.email}"
        )


class ListaCompra(models.Model):
    """
    Representa uma lista de compras criada por um usuário.
    """

    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "core.Usuario", on_delete=models.CASCADE, verbose_name="Usuário"
    )
    nome = models.CharField(max_length=255, verbose_name="Nome da Lista")
    criada_em = models.DateTimeField(auto_now_add=True, verbose_name="Criada Em")
    finalizada = models.BooleanField(default=False, verbose_name="Finalizada")

    class Meta:
        verbose_name = "Lista de Compra"
        verbose_name_plural = "Listas de Compras"
        ordering = ["finalizada", "-criada_em"]

    def __str__(self):

        return f"Lista '{self.nome}' de {self.usuario.first_name if self.usuario.first_name else self.usuario.email}"


class ItemLista(models.Model):
    """
    Representa um item dentro de uma lista de compras.
    Pode estar associado a um item comprado após a realização da compra.
    """

    id = models.AutoField(primary_key=True)
    lista = models.ForeignKey(
        ListaCompra, on_delete=models.CASCADE, verbose_name="Lista de Compra"
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
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Item da Lista"
        verbose_name_plural = "Itens da Lista"
        unique_together = ("lista", "produto")
        ordering = ["lista", "produto__nome"]

    def __str__(self):
        return f"{self.produto.nome} na lista '{self.lista.nome}'"


class Comentario(models.Model):
    """
    Representa um comentário ou avaliação feito por um usuário sobre um produto ou loja.
    """

    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "core.Usuario", on_delete=models.CASCADE, verbose_name="Usuário"
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Produto",
    )
    loja = models.ForeignKey(
        Loja, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Loja"
    )
    texto = models.TextField(verbose_name="Texto do Comentário")
    nota = models.IntegerField(
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
        target = "Produto: " + self.produto.nome if self.produto else ""
        if self.loja:
            target += " Loja: " + self.loja.nome
        if not target:
            target = "N/A"

        return (
            f"Comentário de {self.usuario.first_name if self.usuario.first_name else self.usuario.email} "
            f"sobre {target} (Nota: {self.nota if self.nota else 'N/A'})"
        )


class ProdutoIndicado(models.Model):
    """
    Tabela para usuários indicarem produtos a serem adicionados ao site.
    """

    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "core.Usuario", on_delete=models.CASCADE, verbose_name="Usuário Indicador"
    )
    nome_produto = models.CharField(
        max_length=255, verbose_name="Nome do Produto Indicado"
    )
    descricao_produto = models.TextField(
        blank=True, null=True, verbose_name="Descrição do Produto"
    )
    url_imagem = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="URL da Imagem"
    )
    motivacao = models.TextField(verbose_name="Motivação da Indicação")
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

        return (
            f"Indicação de '{self.nome_produto}' por "
            f"{self.usuario.first_name if self.usuario.first_name else self.usuario.email} "
            f"(Status: {self.status})"
        )
