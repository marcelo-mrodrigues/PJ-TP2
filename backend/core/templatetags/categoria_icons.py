from django import template

register = template.Library()

# Dicionário de emojis para cada categoria
ICONS = {
    "Açougue & Peixaria": "🥩",
    "Alimentos": "🍞",
    "Bebê & Infantil": "🍼",
    "Bebida": "🥤",
    "Casa": "🏠",
    "Comemorações": "🎉",
    "Congelados & Sobremesas": "🍦",
    "Conservas e Enlatados": "🥫",
    "Cozinha": "🍳",
    "Cuidados Pessoais": "🧼",
    "Diet, Saudáveis & Veganos": "🥗",
    "eletronico": "🔌",
    "Eletrônicos": "💻",
    "Frios & Laticínios": "🧀",
    "fruta": "🍎",
    "Fruta": "🍎",
    "Guloseimas": "🍬",
    "Higiene & Perfumaria": "🧴",
    "Hortifruti": "🥦",
    "Legumes e Vegetais": "🥕",
    "Limpeza": "🧹",
    "Livros": "📚",
    "Mercearia": "🥫",
    "Padarias & Matinais": "🥐",
    "Papelaria": "✏️",
    "Pet Care": "🐶",
    "Roupas": "👕",
    "Verduras": "🥬",
    "VideoGame": "🎮",
    "Vinhos": "🍷",
}


@register.simple_tag
def icon_categoria(nome_categoria):
    """
    Retorna um emoji para a categoria.
    Usa um carrinho de compras como ícone padrão se a categoria não for encontrada.
    """
    # A comparação de categoria deve ser insensível a maiúsculas/minúsculas
    # e trata o & se necessário
    return ICONS.get(nome_categoria, "🛒")  # Ícone padrão (carrinho de compras)
