"""
Utilitários e funções auxiliares
"""
import re
from datetime import datetime

def extrair_valor_melhorado(text):
    """
    Extrai valor monetário de um texto com múltiplos formatos
    
    Args:
        text (str): Texto contendo o valor
        
    Returns:
        float: Valor extraído ou None se não encontrado
    """
    if not text:
        return None
    
    # Remove R$, reais, etc.
    text_clean = re.sub(r'(r\$|reais?|real)', '', text, flags=re.IGNORECASE)
    
    # Procura por números com vírgula ou ponto
    valor_match = re.search(r'\d+(?:[.,]\d{1,2})?', text_clean)
    if valor_match:
        valor = valor_match.group().replace(',', '.')
        try:
            return float(valor)
        except ValueError:
            pass
    
    # Números por extenso básicos
    numeros_extenso = {
        'um': 1, 'dois': 2, 'três': 3, 'quatro': 4, 'cinco': 5,
        'seis': 6, 'sete': 7, 'oito': 8, 'nove': 9, 'dez': 10,
        'onze': 11, 'doze': 12, 'treze': 13, 'quatorze': 14, 'quinze': 15,
        'dezesseis': 16, 'dezessete': 17, 'dezoito': 18, 'dezenove': 19,
        'vinte': 20, 'trinta': 30, 'quarenta': 40, 'cinquenta': 50,
        'sessenta': 60, 'setenta': 70, 'oitenta': 80, 'noventa': 90,
        'cem': 100, 'duzentos': 200, 'trezentos': 300, 'quatrocentos': 400,
        'quinhentos': 500, 'seiscentos': 600, 'setecentos': 700,
        'oitocentos': 800, 'novecentos': 900, 'mil': 1000
    }
    
    text_lower = text.lower()
    for palavra, valor in numeros_extenso.items():
        if palavra in text_lower:
            return float(valor)
    
    return None

def limpar_descricao(text, valor_str=None):
    """
    Remove valores e símbolos da descrição, mantendo apenas o texto relevante
    
    Args:
        text (str): Texto original
        valor_str (str): String do valor a ser removida (opcional)
        
    Returns:
        str: Descrição limpa
    """
    if not text:
        return ""
    
    # Remove números, símbolos monetários e palavras relacionadas a dinheiro
    descricao = re.sub(
        r'\d+(?:[.,]\d{1,2})?|r\$|reais?|real', 
        '', 
        text, 
        flags=re.IGNORECASE
    )
    
    # Remove espaços extras e caracteres especiais desnecessários
    descricao = re.sub(r'\s+', ' ', descricao).strip()
    
    return descricao

def formatar_data_brasileira(data=None):
    """
    Formata data no padrão brasileiro (DD/MM/YYYY)
    
    Args:
        data (datetime): Data a ser formatada (padrão: hoje)
        
    Returns:
        str: Data formatada
    """
    if data is None:
        data = datetime.now()
    
    return data.strftime("%d/%m/%Y")

def formatar_valor_monetario(valor):
    """
    Formata valor monetário no padrão brasileiro
    
    Args:
        valor (float): Valor a ser formatado
        
    Returns:
        str: Valor formatado (ex: "R$ 123,45")
    """
    if valor is None:
        return "R$ 0,00"
    
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def validar_numero_telefone(numero):
    """
    Valida formato de número de telefone
    
    Args:
        numero (str): Número de telefone
        
    Returns:
        bool: True se válido
    """
    if not numero:
        return False
    
    # Remove caracteres não numéricos
    numero_limpo = re.sub(r'\D', '', numero)
    
    # Verifica se tem entre 10 e 15 dígitos (padrões internacionais)
    return 10 <= len(numero_limpo) <= 15

def extrair_comando(text):
    """
    Extrai comando de um texto
    
    Args:
        text (str): Texto da mensagem
        
    Returns:
        str: Comando identificado ou None
    """
    if not text:
        return None
    
    text_lower = text.lower().strip()
    
    comandos = [
        'saldo', 'hoje', 'exportar', 'deletar', 'apagar', 
        'ajuda', 'help', 'comandos'
    ]
    
    for comando in comandos:
        if comando in text_lower:
            return comando
    
    return None