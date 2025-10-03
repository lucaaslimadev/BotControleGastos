#!/usr/bin/env python3
"""
Bot Telegram - Controle de Gastos
Versão limpa e funcional
"""
import requests
import time
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Imports locais
from src.sheets_service import SheetsService
from src.categories import categorizar_gasto
from src.utils import extrair_valor_melhorado, limpar_descricao

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações
TOKEN = os.getenv('TELEGRAM_TOKEN')
SHEET_ID = os.getenv('SHEET_ID')

if not TOKEN:
    logger.error("TELEGRAM_TOKEN não encontrado no .env")
    exit(1)

if not SHEET_ID:
    logger.error("SHEET_ID não encontrado no .env")
    exit(1)

# Inicializar serviços
sheets_service = SheetsService()

def enviar_mensagem(chat_id, texto):
    """Envia mensagem para o Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": texto,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            logger.info(f"✅ Mensagem enviada para {chat_id}")
            return True
        else:
            logger.error(f"❌ Erro ao enviar mensagem: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        return False

def processar_comando(comando, chat_id):
    """Processa comandos do bot"""
    logger.info(f"Processando comando: /{comando}")
    
    if comando == "start":
        texto = """🤖 *Bot Controle de Gastos*

✅ Bot funcionando!

*Como usar:*
• Digite: `mercado 50`
• Digite: `uber 25.50`
• Digite: `R$ 100 farmácia`

*Comandos:*
/saldo - Total do mês
/ajuda - Esta mensagem"""
        
        enviar_mensagem(chat_id, texto)
    
    elif comando == "saldo":
        total = sheets_service.calcular_saldo_mes()
        mes_atual = datetime.now().strftime("%m/%Y")
        texto = f"💰 *Saldo do mês {mes_atual}*\n\nTotal gasto: R$ {total:.2f}"
        enviar_mensagem(chat_id, texto)
    
    elif comando == "ajuda":
        texto = """🤖 *Comandos Disponíveis*

💰 *Para registrar gastos:*
• mercado 50
• uber 25.50
• R$ 100 farmácia

📊 *Consultas:*
• /saldo - Total do mês
• /ajuda - Esta mensagem

Digite qualquer gasto para começar!"""
        
        enviar_mensagem(chat_id, texto)

def processar_gasto(texto, chat_id):
    """Processa registro de gasto"""
    logger.info(f"Processando gasto: '{texto}'")
    
    valor = extrair_valor_melhorado(texto)
    
    if valor:
        descricao = limpar_descricao(texto)
        categoria = categorizar_gasto(descricao)
        
        logger.info(f"Valor: {valor}, Descrição: '{descricao}', Categoria: {categoria}")
        
        # Salvar na planilha
        if sheets_service.adicionar_gasto(descricao, valor, categoria):
            # Sucesso
            resposta = f"""✅ *Gasto Registrado*

{descricao} - R$ {valor:.2f}
📂 Categoria: {categoria.title()}"""
            
            enviar_mensagem(chat_id, resposta)
            logger.info(f"💰 GASTO SALVO: {descricao} - R$ {valor:.2f} ({categoria})")
        else:
            # Erro ao salvar
            enviar_mensagem(chat_id, "❌ Erro ao salvar gasto. Tente novamente.")
            logger.error("Erro ao salvar gasto na planilha")
    else:
        # Valor não identificado
        texto_erro = """❌ *Valor não identificado*

*Exemplos válidos:*
• mercado 50
• R$ 25.50 uber
• cinquenta reais farmácia
• 100 gasolina"""
        
        enviar_mensagem(chat_id, texto_erro)

def processar_mensagem(message):
    """Processa uma mensagem recebida"""
    try:
        chat_id = message["chat"]["id"]
        texto = message.get("text", "").strip()
        
        if not texto:
            return
        
        logger.info(f"📱 Mensagem de {chat_id}: '{texto}'")
        
        # Comandos com /
        if texto.startswith('/'):
            comando = texto[1:].lower()
            processar_comando(comando, chat_id)
        else:
            # É um gasto
            processar_gasto(texto, chat_id)
            
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")

def obter_updates(offset=None):
    """Obtém atualizações do Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        params = {"timeout": 10}
        if offset:
            params["offset"] = offset
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao obter updates: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao obter updates: {e}")
        return None

def main():
    """Função principal do bot"""
    logger.info("🚀 Iniciando Bot Telegram - Controle de Gastos")
    logger.info(f"📊 Google Sheets: {'✅ Conectado' if sheets_service.is_connected() else '❌ Desconectado'}")
    logger.info(f"🤖 Token Telegram: {'✅ Configurado' if TOKEN else '❌ Não configurado'}")
    
    if not sheets_service.is_connected():
        logger.error("❌ Google Sheets não conectado. Verifique as credenciais.")
        return
    
    offset = None
    logger.info("✅ Bot iniciado e aguardando mensagens...")
    
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
            logger.info("🛑 Bot interrompido pelo usuário")
            break
        except Exception as e:
            logger.error(f"❌ Erro no loop principal: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()