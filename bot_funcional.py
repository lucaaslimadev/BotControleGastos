#!/usr/bin/env python3
"""
Bot Telegram Funcional - Controle de Gastos
"""
import requests
import time
import logging
from datetime import datetime

# Imports locais
from src.sheets_service import SheetsService
from src.categories import categorizar_gasto
from src.utils import extrair_valor_melhorado, limpar_descricao, extrair_comando

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token do bot
TOKEN = "7907909261:AAFTVrpSpIDNL8CiB5dKnqrlJvB81x-4oDs"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Inicializar serviços
sheets_service = SheetsService()

def enviar_mensagem(chat_id, texto):
    """Envia mensagem para o Telegram"""
    try:
        url = f"{BASE_URL}/sendMessage"
        data = {"chat_id": chat_id, "text": texto}
        response = requests.post(url, json=data)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        return False

def processar_comando(comando, chat_id):
    """Processa comandos específicos"""
    
    if comando == "start":
        enviar_mensagem(chat_id, "🤖 Bot funcionando!\n\nDigite: mercado 50")
    
    elif comando == "saldo":
        total = sheets_service.calcular_saldo_mes()
        mes_atual = datetime.now().strftime("%m/%Y")
        enviar_mensagem(chat_id, f"💰 Saldo do mês {mes_atual}\nTotal: R$ {total:.2f}")
    
    elif comando == "ajuda":
        texto = """🤖 Comandos:
/start - Iniciar
/saldo - Total do mês
/ajuda - Esta mensagem

Para registrar gastos:
mercado 50
uber 25.50
R$ 100 farmácia"""
        enviar_mensagem(chat_id, texto)

def processar_gasto(texto, chat_id):
    """Processa registro de gasto"""
    valor = extrair_valor_melhorado(texto)
    
    if valor:
        descricao = limpar_descricao(texto)
        categoria = categorizar_gasto(descricao)
        
        logger.info(f"Processando: {descricao} - R$ {valor:.2f} ({categoria})")
        
        if sheets_service.adicionar_gasto(descricao, valor, categoria):
            enviar_mensagem(chat_id, f"✅ {descricao} - R$ {valor:.2f}\n📂 {categoria.title()}")
            logger.info(f"💰 SALVO: {descricao} - R$ {valor:.2f}")
        else:
            enviar_mensagem(chat_id, "❌ Erro ao salvar gasto")
    else:
        enviar_mensagem(chat_id, "❌ Valor não identificado\nExemplo: mercado 50")

def processar_mensagem(message):
    """Processa uma mensagem recebida"""
    chat_id = message["chat"]["id"]
    texto = message.get("text", "").strip()
    
    if not texto:
        return
    
    logger.info(f"📱 Recebido de {chat_id}: '{texto}'")
    
    # Comandos com /
    if texto.startswith('/'):
        comando = texto[1:].lower()
        processar_comando(comando, chat_id)
    else:
        # Verificar se é comando sem /
        comando = extrair_comando(texto)
        if comando:
            processar_comando(comando, chat_id)
        else:
            # É um gasto
            processar_gasto(texto, chat_id)

def obter_updates(offset=None):
    """Obtém atualizações do Telegram"""
    try:
        url = f"{BASE_URL}/getUpdates"
        params = {"timeout": 10}
        if offset:
            params["offset"] = offset
        
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        logger.error(f"Erro ao obter updates: {e}")
        return None

def main():
    """Função principal"""
    logger.info("🚀 Iniciando Bot Telegram - Controle de Gastos")
    logger.info(f"📊 Google Sheets: {'✅ Conectado' if sheets_service.is_connected() else '❌ Desconectado'}")
    
    offset = None
    
    while True:
        try:
            updates = obter_updates(offset)
            
            if updates and updates.get("ok"):
                for update in updates["result"]:
                    if "message" in update:
                        processar_mensagem(update["message"])
                    
                    offset = update["update_id"] + 1
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("Bot interrompido pelo usuário")
            break
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()