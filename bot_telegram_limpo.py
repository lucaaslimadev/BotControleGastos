#!/usr/bin/env python3
"""
Bot Telegram - Controle de Gastos
Versão completamente limpa
"""
import requests
import time
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar src ao path
sys.path.append('src')

try:
    from src.sheets_service import SheetsService
    from src.categories import categorizar_gasto
    from src.utils import extrair_valor_melhorado, limpar_descricao
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações
TOKEN = os.getenv('TELEGRAM_TOKEN')
SHEET_ID = os.getenv('SHEET_ID')

print(f"TOKEN: {TOKEN[:10]}..." if TOKEN else "TOKEN: None")
print(f"SHEET_ID: {SHEET_ID}")

if not TOKEN:
    print("❌ TELEGRAM_TOKEN não encontrado no .env")
    sys.exit(1)

if not SHEET_ID:
    print("❌ SHEET_ID não encontrado no .env")
    sys.exit(1)

# Inicializar serviços
try:
    sheets_service = SheetsService()
    print(f"📊 Google Sheets: {'✅ Conectado' if sheets_service.is_connected() else '❌ Desconectado'}")
except Exception as e:
    print(f"❌ Erro ao conectar Google Sheets: {e}")
    sys.exit(1)

def enviar_mensagem(chat_id, texto):
    """Envia mensagem para o Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": texto}
        response = requests.post(url, json=data)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        return False

def processar_mensagem(chat_id, texto):
    """Processa uma mensagem"""
    print(f"📱 Processando: '{texto}' de {chat_id}")
    
    # Comandos
    if texto.startswith('/'):
        comando = texto[1:].lower()
        
        if comando == "start":
            enviar_mensagem(chat_id, "🤖 Bot funcionando!\n\nDigite: mercado 50")
            return
        
        elif comando == "saldo":
            total = sheets_service.calcular_saldo_mes()
            mes = datetime.now().strftime("%m/%Y")
            enviar_mensagem(chat_id, f"💰 Saldo {mes}: R$ {total:.2f}")
            return
    
    # Processar gasto
    valor = extrair_valor_melhorado(texto)
    if valor:
        descricao = limpar_descricao(texto)
        categoria = categorizar_gasto(descricao)
        
        print(f"  Valor: {valor}")
        print(f"  Descrição: '{descricao}'")
        print(f"  Categoria: {categoria}")
        
        if sheets_service.adicionar_gasto(descricao, valor, categoria):
            enviar_mensagem(chat_id, f"✅ {descricao} - R$ {valor:.2f}")
            print(f"💰 SALVO: {descricao} - R$ {valor:.2f}")
        else:
            enviar_mensagem(chat_id, "❌ Erro ao salvar")
            print("❌ Erro ao salvar na planilha")
    else:
        enviar_mensagem(chat_id, "❌ Valor não identificado\nExemplo: mercado 50")

def main():
    """Função principal"""
    print("🚀 Iniciando Bot Telegram - Controle de Gastos")
    
    # Limpar mensagens antigas
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
        data = response.json()
        if data.get("ok") and data["result"]:
            last_update_id = data["result"][-1]["update_id"]
            offset = last_update_id + 1
            print(f"Ignorando {len(data['result'])} mensagens antigas")
        else:
            offset = None
    except:
        offset = None
    
    print("✅ Bot aguardando mensagens novas...")
    
    while True:
        try:
            # Buscar mensagens
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"timeout": 5}
            if offset:
                params["offset"] = offset
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("ok") and data["result"]:
                for update in data["result"]:
                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        texto = message.get("text", "").strip()
                        
                        if texto:
                            processar_mensagem(chat_id, texto)
                    
                    offset = update["update_id"] + 1
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot interrompido")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()