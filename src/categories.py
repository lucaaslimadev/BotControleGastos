"""
Sistema de categorização automática de gastos
"""

# Definição das categorias e palavras-chave
CATEGORIAS = {
    'alimentação': [
        'mercado', 'supermercado', 'padaria', 'restaurante', 'lanche', 
        'pizza', 'hamburguer', 'comida', 'ifood', 'delivery', 'açougue',
        'feira', 'verdura', 'fruta', 'pão', 'café', 'bar', 'lanchonete'
    ],
    'transporte': [
        'uber', 'taxi', '99', 'gasolina', 'combustível', 'ônibus', 
        'metro', 'estacionamento', 'pedágio', 'mecânico', 'oficina',
        'pneu', 'óleo', 'revisão', 'ipva', 'seguro', 'multa'
    ],
    'saúde': [
        'farmácia', 'médico', 'hospital', 'remédio', 'consulta', 
        'exame', 'dentista', 'laboratório', 'plano', 'saúde',
        'medicamento', 'vitamina', 'suplemento'
    ],
    'lazer': [
        'cinema', 'teatro', 'show', 'bar', 'balada', 'festa', 
        'viagem', 'hotel', 'passeio', 'parque', 'shopping',
        'jogo', 'streaming', 'netflix', 'spotify'
    ],
    'casa': [
        'luz', 'água', 'internet', 'aluguel', 'condomínio', 'limpeza',
        'móvel', 'decoração', 'reforma', 'manutenção', 'gás',
        'telefone', 'tv', 'segurança'
    ],
    'educação': [
        'curso', 'livro', 'escola', 'faculdade', 'material', 
        'mensalidade', 'apostila', 'caneta', 'caderno',
        'formação', 'certificação'
    ],
    'vestuário': [
        'roupa', 'sapato', 'tênis', 'camisa', 'calça', 'vestido',
        'blusa', 'casaco', 'bermuda', 'moda', 'loja'
    ],
    'outros': []
}

def categorizar_gasto(descricao):
    """
    Categoriza um gasto baseado na descrição
    
    Args:
        descricao (str): Descrição do gasto
        
    Returns:
        str: Categoria identificada
    """
    if not descricao:
        return 'outros'
    
    descricao_lower = descricao.lower().strip()
    
    # Procura por palavras-chave em cada categoria
    for categoria, palavras in CATEGORIAS.items():
        if any(palavra in descricao_lower for palavra in palavras):
            return categoria
    
    return 'outros'

def obter_categorias():
    """
    Retorna lista de todas as categorias disponíveis
    
    Returns:
        list: Lista de categorias
    """
    return list(CATEGORIAS.keys())

def adicionar_palavra_categoria(categoria, palavra):
    """
    Adiciona uma nova palavra-chave a uma categoria
    
    Args:
        categoria (str): Nome da categoria
        palavra (str): Palavra-chave a ser adicionada
    """
    if categoria in CATEGORIAS:
        if palavra.lower() not in CATEGORIAS[categoria]:
            CATEGORIAS[categoria].append(palavra.lower())
            return True
    return False