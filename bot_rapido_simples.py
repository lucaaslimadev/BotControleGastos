#!/usr/bin/env python3
"""
Bot Rápido e Simples - Baseado no que funcionava
"""
import requests
import time
import re
import threading
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
SHEET_ID = os.getenv('SHEET_ID')

print(f"🔧 Iniciando bot...")
print(f"🔧 TOKEN: {TOKEN[:10]}...")
print(f"🔧 SHEET_ID: {SHEET_ID}")

# Conectar Google Sheets
try:
    creds = Credentials.from_service_account_file('config/credentials.json', 
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_ID).sheet1
    print("✅ Google Sheets conectado")
except Exception as e:
    print(f"❌ Erro Google Sheets: {e}")
    exit(1)

def enviar_mensagem(chat_id, texto):
    """Envia mensagem"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": texto}, timeout=5)
        return True
    except:
        return False

def salvar_gasto_async(descricao, valor, categoria):
    """Salva gasto em background"""
    def salvar():
        try:
            hoje = datetime.now().strftime("%d/%m/%Y")
            sheet.append_row([hoje, descricao, f"{valor:.2f}", categoria])
            print(f"💰 SALVO: {descricao} - R$ {valor:.2f}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    
    threading.Thread(target=salvar, daemon=True).start()

def processar_mensagem(chat_id, texto, nome):
    """Processa mensagem"""
    print(f"📱 {nome} ({chat_id}): {texto}")
    
    if texto.startswith('/'):
        if texto == "/start":
            enviar_mensagem(chat_id, f"🤖 Olá {nome}!\n\nBot funcionando! Digite: mercado 50")
        elif texto == "/saldo":
            enviar_mensagem(chat_id, "💰 Calculando saldo...")
    else:
        # Processar gasto
        match = re.search(r'(\d+(?:[.,]\d{1,2})?)', texto)
        if match:
            valor = float(match.group().replace(',', '.'))
            descricao = re.sub(r'\d+(?:[.,]\d{1,2})?|r\$|reais?', '', texto, flags=re.IGNORECASE).strip()
            
            # Categorizar
            categoria = 'outros'
            desc_lower = descricao.lower()
            if any(x in desc_lower for x in ['mercado', 'supermercado', 'comida', 'lanche']):
                categoria = 'alimentação'
            elif any(x in desc_lower for x in ['uber', 'taxi', 'gasolina', 'combustível']):
                categoria = 'transporte'
            elif any(x in desc_lower for x in ['farmácia', 'médico', 'remédio']):
                categoria = 'saúde'
            
            # RESPOSTA IMEDIATA
            enviar_mensagem(chat_id, f"✅ {descricao} - R$ {valor:.2f}\n📂 {categoria.title()}")
            
            # Salvar em background
            salvar_gasto_async(descricao, valor, categoria)
        else:
            enviar_mensagem(chat_id, "❌ Valor não identificado\nExemplo: mercado 50")

def main():
    """Função principal"""
    print("🚀 Bot Rápido iniciado!")
    
    # Limpar mensagens antigas
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=10)
        if r.json().get("result"):
            last_id = r.json()["result"][-1]["update_id"]
            requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}", timeout=10)
            print(f"🧹 Limpas {len(r.json()['result'])} mensagens antigas")
    except:
        pass
    
    print("✅ Aguardando mensagens...")
    
    offset = None
    while True:
        try:
            r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", 
                           params={"timeout": 5, "offset": offset}, timeout=10)
            data = r.json()
            
            if data.get("ok") and data["result"]:
                for update in data["result"]:
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        texto = msg.get("text", "").strip()
                        nome = msg["from"].get("first_name", f"User{chat_id}")
                        
                        if texto:
                            processar_mensagem(chat_id, texto, nome)
                    
                    offset = update["update_id"] + 1
            
            # Sem delay para máxima velocidade
            
        except KeyboardInterrupt:
            print("\n🛑 Bot parado")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()