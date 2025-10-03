#!/usr/bin/env python3
"""
Bot Ultra Rápido - Resposta em milissegundos
"""
import requests
import time
import re
import threading
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
SHEET_ID = os.getenv('SHEET_ID')

# Sessão HTTP persistente para velocidade máxima
session = requests.Session()
session.timeout = 2

# Conectar Google Sheets uma vez
creds = Credentials.from_service_account_file('config/credentials.json', 
    scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).sheet1

print("🚀 Bot Ultra Rápido iniciado!")

def enviar_instantaneo(chat_id, texto):
    """Envio instantâneo sem esperar resposta"""
    def enviar():
        try:
            session.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                        json={"chat_id": chat_id, "text": texto})
        except:
            pass
    threading.Thread(target=enviar, daemon=True).start()

def salvar_background(descricao, valor, categoria):
    """Salva em background sem bloquear"""
    def salvar():
        try:
            hoje = datetime.now().strftime("%d/%m/%Y")
            sheet.append_row([hoje, descricao, f"{valor:.2f}", categoria])
            print(f"💾 Salvo: {descricao} - R$ {valor:.2f}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    threading.Thread(target=salvar, daemon=True).start()

def processar_rapido(chat_id, texto, nome):
    """Processamento ultra rápido"""
    print(f"⚡ {nome}: {texto}")
    
    if texto.startswith('/'):
        if texto == "/start":
            enviar_instantaneo(chat_id, f"🤖 {nome}! Digite: mercado 50")
        elif texto == "/saldo":
            enviar_instantaneo(chat_id, "💰 Calculando...")
    else:
        # Extrair valor instantaneamente
        match = re.search(r'(\d+(?:[.,]\d{1,2})?)', texto)
        if match:
            valor = float(match.group().replace(',', '.'))
            descricao = re.sub(r'\d+(?:[.,]\d{1,2})?|r\$|reais?', '', texto, flags=re.IGNORECASE).strip()
            
            # Categorização rápida
            categoria = 'outros'
            if any(x in descricao.lower() for x in ['mercado', 'supermercado', 'comida']):
                categoria = 'alimentação'
            elif any(x in descricao.lower() for x in ['uber', 'taxi', 'gasolina']):
                categoria = 'transporte'
            elif any(x in descricao.lower() for x in ['farmácia', 'médico']):
                categoria = 'saúde'
            
            # RESPOSTA INSTANTÂNEA
            enviar_instantaneo(chat_id, f"✅ {descricao} - R$ {valor:.2f}")
            
            # Salvar em background
            salvar_background(descricao, valor, categoria)
        else:
            enviar_instantaneo(chat_id, "❌ Valor não identificado")

# Limpar cache
try:
    r = session.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
    if r.json().get("result"):
        last_id = r.json()["result"][-1]["update_id"]
        session.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}")
        print("🧹 Cache limpo")
except:
    pass

print("⚡ Modo ultra rápido ativo!")

offset = None
while True:
    try:
        # Polling ultra rápido
        r = session.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", 
                       params={"timeout": 1, "offset": offset})
        data = r.json()
        
        if data.get("ok") and data["result"]:
            for update in data["result"]:
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    texto = msg.get("text", "").strip()
                    nome = msg["from"].get("first_name", "User")
                    
                    if texto:
                        processar_rapido(chat_id, texto, nome)
                
                offset = update["update_id"] + 1
        
        # Sem delay - máxima velocidade
        
    except KeyboardInterrupt:
        break
    except:
        time.sleep(1)