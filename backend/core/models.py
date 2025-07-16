## @file core/models.py
#
# @brief Define os modelos de dados para o aplicativo 'core' do FoodMart.
#
# Este arquivo contém as definições de todos os modelos Django que representam
# as entidades do sistema, como Categorias, Marcas, Produtos, Usuários, Lojas,
# Ofertas, Itens Comprados, Listas de Compras, Itens de Lista e Comentários.
# Também inclui um modelo para Produtos Indicados por usuários.
#
# Cada modelo herda de `django.db.models.Model` e define campos com tipos de dados
# apropriados, validações, relacionamentos e metadados para administração.

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Importar settings para referenciar o User model

# --- Modelos Principais ---

## @brief Modelo que representa uma Categoria de produto.
#
# Cada categoria possui um nome único.
class Categoria(models.Model):
    ## @var nome
    # @brief Nome da categoria (ex: "Alimentos", "Eletrônicos").
    # @type models.CharField
    # @details Único e obrigatório.
    nome = models.CharField(
        max_length=100, unique=True, verbose_name="Nome da Categoria"
    )

    ## @brief Opções de metadados para o modelo Categoria.
    #
    # @param verbose_name Nome singular legível para humanos.
    # @param verbose_name_plural Nome plural legível para humanos.
    # @param ordering Ordem padrão para consulta, por nome ascendente.
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    ## @brief Representação em string do objeto Categoria.
    # @return O nome da categoria.
    def __str__(self):
        return self.nome

## @brief Modelo que representa uma Marca de produto.
#
# Cada marca possui um nome único.
class Marca(models.Model):
    ## @var nome
    # @brief Nome da marca (ex: "Nestlé", "Sony").
    # @type models.CharField
    # @details Único e obrigatório.
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Marca")


    class Meta:
        ## @brief Opções de metadados para o modelo Marca.
        #
        # @param verbose_name Nome singular legível para humanos.
        # @param verbose_name_plural Nome plural legível para humanos.
        # @param ordering Ordem padrão para consulta, por nome ascendente.
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["nome"]

    ## @brief Representação em string do objeto Marca.
    # @return O nome da marca.
    def __str__(self):
        return self.nome

## @brief Modelo de usuário customizado para o sistema FoodMart.
#
# Herda todos os campos padrão do Django's `AbstractUser` e adiciona validações customizadas.
class Usuario(AbstractUser):
    ## @var email
    # @brief Endereço de e-mail do usuário.
    # @type models.EmailField
    # @details Obrigatório e único, usado para contato e identificação.
    email = models.EmailField(
        unique=True, blank=False, verbose_name="Endereço de e-mail"
    )

    ## @brief Campo usado para login.
    # @details Define 'username' como o campo a ser usado para autenticação.
    USERNAME_FIELD = "username"
    ## @brief Campos obrigatórios ao criar um superusuário ou usuário via `createsuperuser`.
    # @details Define 'email', 'first_name', 'last_name' como campos obrigatórios.
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    ## @brief Representação em string do objeto Usuario.
    # @return O nome completo do usuário, se disponível, caso contrário o nome de usuário.
    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username

## @brief Modelo que representa um Produto no catálogo.
#
# Inclui informações detalhadas sobre o produto, sua categoria, marca, e status de aprovação.
class Produto(models.Model):
    ## @var nome
    # @brief Nome do produto (ex: "Arroz Parboilizado").
    # @type models.CharField
    # @details Obrigatório.
    nome = models.CharField(max_length=255, verbose_name="Nome do Produto")
    ## @var descricao
    # @brief Descrição detalhada do produto.
    # @type models.TextField
    # @details Opcional.
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    ## @var imagem_url
    # @brief URL da imagem do produto.
    # @type models.URLField
    # @details Opcional.
    imagem_url = models.URLField(
        max_length=500, blank=True, verbose_name="URL da Imagem"
    )
    ## @var categoria
    # @brief Categoria à qual o produto pertence.
    # @type models.ForeignKey
    # @details Relacionamento com `Categoria`. Pode ser nulo se a categoria for removida.
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoria",
    )
    ## @var marca
    # @brief Marca do produto.
    # @type models.ForeignKey
    # @details Relacionamento com `Marca`. Pode ser nulo se a marca for removida.
    marca = models.ForeignKey(
        Marca, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Marca"
    )

    ## @var adicionado_por
    # @brief Usuário que adicionou ou solicitou o produto.
    # @type models.ForeignKey
    # @details Relacionamento com o modelo de usuário definido em `settings.AUTH_USER_MODEL`.
    # Pode ser nulo se o usuário for removido.
    adicionado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Adicionado Por",
    )
    ## @var data_adicao
    # @brief Data e hora em que o produto foi adicionado.
    # @type models.DateTimeField
    # @details Gerado automaticamente na criação.
    data_adicao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Adição")
    ## @var aprovado
    # @brief Indica se o produto foi aprovado para aparecer no catálogo.
    # @type models.BooleanField
    # @details Padrão é `False`.
    aprovado = models.BooleanField(default=False)

    class Meta:
        ## @brief Opções de metadados para o modelo Produto.
        #
        # @param verbose_name Nome singular legível para humanos.
        # @param verbose_name_plural Nome plural legível para humanos.
        # @param ordering Ordem padrão para consulta, por nome ascendente.
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    ## @brief Representação em string do objeto Produto.
    # @return O nome do produto.
    def __str__(self):
        return self.nome


## @brief Modelo que representa uma Loja onde os produtos podem ser comprados.
#
# Cada loja possui um nome único e pode ter uma URL e URL de logo.
class Loja(models.Model):
    ## @var nome
    # @brief Nome da loja (ex: "Amazon Brasil", "Mercado Livre").
    # @type models.CharField
    # @details Único e obrigatório.
    nome = models.CharField(max_length=255, unique=True, verbose_name="Nome da Loja")

    ## @var url
    # @brief URL do website da loja.
    # @type models.URLField
    # @details Opcional.
    url = models.URLField(max_length=500, blank=True, verbose_name="URL da Loja")

    ## @var logo_url
    # @brief URL do logo da loja.
    # @type models.URLField
    # @details Opcional.
    logo_url = models.URLField(max_length=500, blank=True, verbose_name="URL do Logo")

    class Meta:
        ## @brief Opções de metadados para o modelo Loja.
        #
        # @param verbose_name Nome singular legível para humanos.
        # @param verbose_name_plural Nome plural legível para humanos.
        # @param ordering Ordem padrão para consulta, por nome ascendente.
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"
        ordering = ["nome"]
    
    ## @brief Representação em string do objeto Loja.
    # @return O nome da loja.
    def __str__(self):
        return self.nome

## @brief Modelo que representa uma Oferta específica de um produto em uma loja.
#
# Uma oferta registra o preço de um produto em uma determinada loja em um momento específico.
class Oferta(models.Model):
    ## @var produto
    # @brief Produto ao qual esta oferta se refere.
    # @type models.ForeignKey
    # @details Relacionamento com `Produto`. Se o produto for excluído, a oferta também será.
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        verbose_name="Produto",
        related_name="ofertas",
    )
    ## @var loja
    # @brief Loja que está fazendo esta oferta.
    # @type models.ForeignKey
    # @details Relacionamento com `Loja`. Se a loja for excluída, a oferta também será.
    loja = models.ForeignKey(
        Loja, on_delete=models.CASCADE, verbose_name="Loja", related_name="ofertas"
    )
    ## @var preco
    # @brief Preço da oferta.
    # @type models.DecimalField
    # @details Obrigatório, com precisão de 10 dígitos e 2 casas decimais.
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    ## @var data_captura
    # @brief Data e hora em que a oferta foi capturada.
    # @type models.DateTimeField
    # @details Gerado automaticamente na criação.
    data_captura = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Captura"
    )

    class Meta:
        ## @brief Opções de metadados para o modelo Oferta.
        #
        # @param verbose_name Nome singular legível para humanos.
        # @param verbose_name_plural Nome plural legível para humanos.
        # @param unique_together Garante que a combinação de produto, loja e data_captura seja única.
        # @param ordering Ordem padrão para consulta, pela data de captura descendente.
        verbose_name = "Oferta"
        verbose_name_plural = "Ofertas"
        unique_together = ("produto", "loja", "data_captura")
        ordering = ["-data_captura"]

    ## @brief Representação em string do objeto Oferta.
    # @return Uma string descrevendo a oferta (produto, loja, preço).
    def __str__(self):
        return f"Oferta de {self.produto.nome} na {self.loja.nome} por R${self.preco}"

## @brief Modelo que registra um item que foi efetivamente comprado por um usuário.
#
# Usado para histórico de compras.
class ItemComprado(models.Model):
    ## @var usuario
    # @brief Usuário que realizou a compra.
    # @type models.ForeignKey
    # @details Relacionamento com o modelo de usuário definido em `settings.AUTH_USER_MODEL`.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuário"
    )
    ## @var loja
    # @brief Loja onde o item foi comprado.
    # @type models.ForeignKey
    # @details Relacionamento com `Loja`. Pode ser nulo se a loja for removida.
    loja = models.ForeignKey(
        Loja, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Loja"
    )
    ## @var produto
    # @brief Produto que foi comprado.
    # @type models.ForeignKey
    # @details Relacionamento com `Produto`. Pode ser nulo se o produto for removido.
    produto = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Produto",
    )

    ## @var preco_pago
    # @brief Preço pago pelo item no momento da compra.
    # @type models.DecimalField
    # @details Obrigatório, com precisão de 10 dígitos e 2 casas decimais.
    preco_pago = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Preço Pago"
    )
    ## @var data_compra
    # @brief Data em que a compra foi realizada.
    # @type models.DateField
    # @details Obrigatório.
    data_compra = models.DateField(verbose_name="Data da Compra")

    class Meta:
        ## @brief Opções de metadados para o modelo ItemComprado.
        #
        # @param verbose_name Nome singular legível para humanos.
        # @param verbose_name_plural Nome plural legível para humanos.
        # @param ordering Ordem padrão para consulta, pela data de compra descendente.
        verbose_name = "Item Comprado"
        verbose_name_plural = "Itens Comprados"
        ordering = ["-data_compra"]
    
    ## @brief Representação em string do objeto ItemComprado.
    # @return Uma string descrevendo o item comprado (produto, usuário).
    def __str__(self):
        produto_nome = self.produto.nome if self.produto else "Produto Removido"
        return f"Compra de {produto_nome} por {self.usuario}"

## @brief Modelo que representa uma Lista de Compras criada por um usuário.
class ListaCompra(models.Model):
    ## @var usuario
    # @brief Usuário proprietário da lista de compras.
    # @type models.ForeignKey
    # @details Relacionamento com o modelo de usuário definido em `settings.AUTH_USER_MODEL`.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário",
        related_name="listas_de_compra",
    )

    ## @var nome
    # @brief Nome da lista de compras (ex: "Compras da Semana", "Churrasco").
    # @type models.CharField
    # @details Obrigatório.
    nome = models.CharField(max_length=255, verbose_name="Nome da Lista")

    ## @var criada_em
    # @brief Data e hora de criação da lista.
    # @type models.DateTimeField
    # @details Gerado automaticamente na criação.
    criada_em = models.DateTimeField(auto_now_add=True, verbose_name="Criada Em")

    ## @var finalizada
    # @brief Indica se a lista de compras foi finalizada.
    # @type models.BooleanField
    # @details Padrão é `False`.
    finalizada = models.BooleanField(default=False, verbose_name="Finalizada")

    class Meta:
        ## @brief Opções de metadados para o modelo ListaCompra.
        #
        # @param verbose_name Nome singular legível para humanos.
        # @param verbose_name_plural Nome plural legível para humanos.
        # @param ordering Ordem padrão para consulta (finalizadas por último, depois por data de criação descendente).
        verbose_name = "Lista de Compra"
        verbose_name_plural = "Listas de Compras"
        ordering = ["finalizada", "-criada_em"]

    ## @brief Representação em string do objeto ListaCompra.
    # @return Uma string descrevendo a lista de compras (nome, usuário).
    def __str__(self):
        return f"Lista '{self.nome}' de {self.usuario}"

## @brief Modelo que representa um item específico dentro de uma Lista de Compras.
class ItemLista(models.Model):
    ## @var lista
    # @brief Lista de compras à qual este item pertence.
    # @type models.ForeignKey
    # @details Relacionamento com `ListaCompra`. Se a lista for excluída, o item também será.
    lista = models.ForeignKey(
        ListaCompra,
        on_delete=models.CASCADE,
        verbose_name="Lista de Compra",
        related_name="itens", # related_name ajustado para clareza
    )

    ## @var produto
    # @brief Produto que é o item da lista.
    # @type models.ForeignKey
    # @details Relacionamento com `Produto`. Se o produto for excluído, o item da lista também será.
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, verbose_name="Produto"
    )

    ## @var item_comprado
    # @brief Referência ao ItemComprado, se este item da lista já foi efetivamente comprado.
    # @type models.OneToOneField
    # @details Opcional.
    item_comprado = models.OneToOneField(
        ItemComprado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Item Comprado Associado",
    )

    ## @var observacoes
    # @brief Observações adicionais sobre o item da lista (ex: "orgânico", "marca X").
    # @type models.TextField
    # @details Opcional.
    observacoes = models.TextField(blank=True, verbose_name="Observações")

    class Meta:
        ## @brief Opções de metadados para o modelo ItemLista.
        #
        # @param verbose_name Nome singular legível para humanos.
        # @param verbose_name_plural Nome plural legível para humanos.
        # @param unique_together Garante que um produto só possa estar uma vez em uma lista específica.
        # @param ordering Ordem padrão para consulta.
        verbose_name = "Item da Lista"
        verbose_name_plural = "Itens da Lista"
        unique_together = ("lista", "produto")
        ordering = ["lista", "produto__nome"]

    ## @brief Representação em string do objeto ItemLista.
    # @return Uma string descrevendo o item na lista.
    def __str__(self):
        return f"{self.produto.nome} na lista '{self.lista.nome}'"

## @brief Modelo que representa um Comentário ou avaliação de um usuário sobre um Produto ou Loja.
class Comentario(models.Model):
    ## @var usuario
    # @brief Usuário que fez o comentário.
    # @type models.ForeignKey
    # @details Relacionamento com o modelo de usuário definido em `settings.AUTH_USER_MODEL`.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuário"
    )

    ## @var produto
    # @brief Produto ao qual o comentário se refere.
    # @type models.ForeignKey
    # @details Relacionamento com `Produto`. Opcional.
    produto = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Produto",
        related_name="comentarios",
    )

    ## @var loja
    # @brief Loja à qual o comentário se refere.
    # @type models.ForeignKey
    # @details Relacionamento com `Loja`. Opcional.
    loja = models.ForeignKey(
        Loja,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Loja",
        related_name="comentarios",
    )

    ## @var texto
    # @brief Conteúdo do comentário.
    # @type models.TextField
    # @details Obrigatório.
    texto = models.TextField(verbose_name="Texto do Comentário")

    ## @var nota
    # @brief Nota atribuída (de 1 a 5).
    # @type models.PositiveSmallIntegerField
    # @details Opcional, com validação de mínimo e máximo.
    nota = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Nota (1 a 5)",
    )

    ## @var data
    # @brief Data e hora do comentário.
    # @type models.DateTimeField
    # @details Gerado automaticamente na criação.
    data = models.DateTimeField(auto_now_add=True, verbose_name="Data do Comentário")

    class Meta:
        ## @brief Opções de metadados para o modelo Comentario.
        #
        # @param verbose_name Nome singular legível para humanos.
        # @param verbose_name_plural Nome plural legível para humanos.
        # @param ordering Ordem padrão para consulta, pela data descendente.
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ["-data"]

    ## @brief Representação em string do objeto Comentario.
    # @return Uma string descrevendo o comentário (usuário, produto/loja).
    def __str__(self):
        target = (
            f"Produto: {self.produto.nome}"
            if self.produto
            else f"Loja: {self.loja.nome}"
        )
        return f"Comentário de {self.usuario} sobre {target}"

## @brief Modelo que representa um Produto Indicado por um usuário para inclusão no catálogo.
#
# Produtos indicados aguardam aprovação da equipe administrativa.
class ProdutoIndicado(models.Model):
    ## @var usuario
    # @brief Usuário que fez a indicação do produto.
    # @type models.ForeignKey
    # @details Relacionamento com o modelo de usuário definido em `settings.AUTH_USER_MODEL`.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário Indicador",
    )
    ## @var nome_produto
    # @brief Nome do produto sugerido.
    # @type models.CharField
    # @details Obrigatório.
    nome_produto = models.CharField(
        max_length=255, verbose_name="Nome do Produto Indicado"
    )
    ## @var descricao_produto
    # @brief Descrição fornecida para o produto sugerido.
    # @type models.TextField
    # @details Opcional.
    descricao_produto = models.TextField(
        blank=True, verbose_name="Descrição do Produto"
    )

    ## @var url_imagem
    # @brief URL da imagem sugerida para o produto.
    # @type models.URLField
    # @details Opcional.
    url_imagem = models.URLField(
        max_length=500, blank=True, verbose_name="URL da Imagem"
    )

    ## @var motivacao
    # @brief Razão pela qual o usuário está indicando o produto.
    # @type models.TextField
    # @details Opcional.
    motivacao = models.TextField(blank=True, verbose_name="Motivação da Indicação")

    ## @var data_indicacao
    # @brief Data e hora em que a indicação foi feita.
    # @type models.DateTimeField
    # @details Gerado automaticamente na criação.
    data_indicacao = models.DateTimeField(
        auto_now_add=True, verbose_name="Data da Indicação"
    )

    ## @var status
    # @brief Status atual da indicação (pendente, aprovado, rejeitado).
    # @type models.CharField
    # @details Campo de escolha com valores predefinidos. Padrão é 'pendente'.
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

    ## @var produto_existente
    # @brief Referência a um produto existente no catálogo, se a indicação for para um produto já existente.
    # @type models.ForeignKey
    # @details Opcional.
    produto_existente = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Produto Existente Relacionado",
    )

    class Meta:
        ## @brief Opções de metadados para o modelo ProdutoIndicado.
        #
        # @param verbose_name Nome singular legível para humanos.
        # @param verbose_name_plural Nome plural legível para humanos.
        # @param ordering Ordem padrão para consulta (primeiro pelo status, depois pela data de indicação descendente).
        verbose_name = "Produto Indicado"
        verbose_name_plural = "Produtos Indicados"
        ordering = ["status", "-data_indicacao"]

    ## @brief Representação em string do objeto ProdutoIndicado.
    # @return Uma string descrevendo a indicação do produto.
    def __str__(self):
        return f"Indicação de '{self.nome_produto}' por {self.usuario} ({self.status})"