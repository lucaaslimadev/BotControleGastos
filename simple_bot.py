#!/usr/bin/env python3
"""
Bot Telegram Simples para Railway
"""
import requests
import time
import os
import threading
import re
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

# Configurações
TOKEN = os.getenv('TELEGRAM_TOKEN')
PORT = int(os.getenv('PORT', 8000))

# Flask para health check
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Telegram funcionando!"

@app.route('/health')
def health():
    return {"status": "ok", "bot": "running"}

def extrair_valor(texto):
    """Extrai valor do texto"""
    match = re.search(r'(\d+(?:[.,]\d{1,2})?)', texto)
    return float(match.group().replace(',', '.')) if match else None

def categorizar(descricao):
    """Categoriza gasto"""
    desc = descricao.lower()
    if any(p in desc for p in ['mercado', 'supermercado']):
        return 'alimentação'
    elif any(p in desc for p in ['uber', 'taxi']):
        return 'transporte'
    elif any(p in desc for p in ['farmácia', 'médico']):
        return 'saúde'
    return 'outros'

def enviar_mensagem(chat_id, texto):
    """Envia mensagem"""
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                     json={"chat_id": chat_id, "text": texto}, timeout=5)
        return True
    except:
        return False

def processar_mensagem(chat_id, texto, nome):
    """Processa mensagem"""
    print(f"📱 {nome}: {texto}")
    
    if texto.startswith('/'):
        comando = texto[1:].lower()
        
        if comando == 'start':
            enviar_mensagem(chat_id, f"🤖 Olá {nome}!\n\n✅ Bot funcionando!\n\nDigite: mercado 50")
        
        elif comando == 'saldo':
            enviar_mensagem(chat_id, "💰 Saldo do mês\n\nTotal: R$ 1.250,50")
        
        elif comando == 'ajuda':
            enviar_mensagem(chat_id, """🤖 Comandos:
/start - Iniciar
/saldo - Total do mês
/ajuda - Esta mensagem

Para registrar gastos:
mercado 50
uber 25.50""")
    else:
        # Processar gasto
        valor = extrair_valor(texto)
        if valor:
            categoria = categorizar(texto)
            enviar_mensagem(chat_id, f"✅ Gasto registrado!\n💰 R$ {valor:.2f}\n📂 {categoria.title()}")
            print(f"💰 GASTO: R$ {valor:.2f} - {categoria}")
        else:
            enviar_mensagem(chat_id, "❌ Valor não identificado\nExemplo: mercado 50")

def bot_loop():
    """Loop principal do bot"""
    print("🚀 Bot iniciado!")
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
                        nome = msg["from"].get("first_name", "User")
                        
                        if texto:
                            processar_mensagem(chat_id, texto, nome)
                    
                    offset = update["update_id"] + 1
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            time.sleep(2)

if __name__ == "__main__":
    # Iniciar bot em thread
    bot_thread = threading.Thread(target=bot_loop, daemon=True)
    bot_thread.start()
    
    # Iniciar Flask para health check
    print(f"🌐 Health check em http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)