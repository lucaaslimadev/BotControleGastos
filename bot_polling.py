#!/usr/bin/env python3
"""
Bot Telegram com Polling (sem webhook)
"""
import time
import requests
import logging
from src.config import Config
from src.sheets_service import SheetsService
from src.telegram_service import TelegramService
from src.categories import categorizar_gasto
from src.utils import extrair_valor_melhorado, limpar_descricao, extrair_comando
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar serviços
sheets_service = SheetsService()
telegram_service = TelegramService()

def get_updates(offset=None):
    """Obtém atualizações do Telegram"""
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 10}
    if offset:
        params["offset"] = offset
    
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        logger.error(f"Erro ao obter updates: {e}")
        return None

def processar_mensagem(message):
    """Processa uma mensagem"""
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    
    if not text:
        return
    
    logger.info(f"📱 Mensagem de {chat_id}: '{text}'")
    
    # Comandos com /
    if text.startswith('/'):
        comando = text[1:].lower()
        processar_comando(comando, text, chat_id)
    else:
        # Verificar comandos sem /
        comando = extrair_comando(text)
        if comando:
            processar_comando(comando, text, chat_id)
        else:
            processar_gasto(text, chat_id)

def processar_comando(comando, text, chat_id):
    """Processa comandos específicos"""
    
    if comando == "saldo":
        total = sheets_service.calcular_saldo_mes()
        mes_atual = datetime.now().strftime("%m/%Y")
        telegram_service.enviar_saldo_mensal(chat_id, total, mes_atual)
    
    elif comando == "hoje":
        gastos_hoje, total = sheets_service.obter_gastos_hoje()
        telegram_service.enviar_lista_gastos(chat_id, gastos_hoje, "📅 Gastos de Hoje")
    
    elif comando == "exportar":
        link_planilha = f"https://docs.google.com/spreadsheets/d/{Config.SHEET_ID}/edit"
        telegram_service.enviar_mensagem_formatada(
            chat_id,
            "📊 Planilha de Gastos",
            f"Acesse sua planilha completa:\n{link_planilha}",
            "Mantenha seus gastos sempre organizados!"
        )
    
    elif comando in ["deletar", "apagar"]:
        if sheets_service.deletar_ultimo_gasto():
            telegram_service.enviar_mensagem(chat_id, "✅ Último gasto deletado com sucesso!")
        else:
            telegram_service.enviar_mensagem(chat_id, "❌ Erro ao deletar gasto")
    
    elif comando in ["ajuda", "help", "comandos", "start"]:
        telegram_service.enviar_ajuda(chat_id)

def processar_gasto(text, chat_id):
    """Processa registro de gasto"""
    valor = extrair_valor_melhorado(text)
    
    if valor:
        descricao = limpar_descricao(text)
        categoria = categorizar_gasto(descricao)
        
        if sheets_service.adicionar_gasto(descricao, valor, categoria):
            telegram_service.enviar_mensagem_formatada(
                chat_id,
                "✅ Gasto Registrado",
                f"{descricao} - R$ {valor:.2f}",
                f"📂 Categoria: {categoria.title()}"
            )
            
            logger.info(f"💰 GASTO REGISTRADO: {descricao} - R$ {valor:.2f} ({categoria})")
        else:
            telegram_service.enviar_mensagem(chat_id, "❌ Erro ao salvar gasto. Tente novamente.")
    else:
        telegram_service.enviar_erro_valor(chat_id)

def main():
    """Função principal"""
    logger.info("🚀 Iniciando Bot Telegram (Polling)")
    
    # Remover webhook
    requests.post(f"https://api.telegram.org/bot{Config.TELEGRAM_TOKEN}/deleteWebhook")
    
    offset = None
    
    while True:
        try:
            updates = get_updates(offset)
            
            if updates and updates.get("ok"):
                for update in updates["result"]:
                    if "message" in update:
                        processar_mensagem(update["message"])
                    
                    offset = update["update_id"] + 1
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("Bot interrompido")
            break
        except Exception as e:
            logger.error(f"Erro: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()