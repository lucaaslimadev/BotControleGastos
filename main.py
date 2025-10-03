#!/usr/bin/env python3
"""
Main - Sistema Completo para Railway
"""
import os
import threading
import time
from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
PORT = int(os.getenv('PORT', 8000))

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/')
def home():
    # Importar e retornar o dashboard completo
    from dashboard_completo import dashboard
    return dashboard()

# Importar todas as rotas do dashboard
from dashboard_completo import app as dashboard_app
for rule in dashboard_app.url_map.iter_rules():
    if rule.endpoint not in ['static', 'health']:
        try:
            app.add_url_rule(
                rule.rule, 
                f"dashboard_{rule.endpoint}",
                dashboard_app.view_functions[rule.endpoint],
                methods=list(rule.methods)
            )
        except:
            pass

def run_bot():
    """Executa o bot completo"""
    time.sleep(5)  # Aguarda Flask iniciar
    exec(open('bot_completo.py').read())

if __name__ == "__main__":
    print(f"🚀 Iniciando na porta {PORT}")
    
    # Bot em thread
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Flask
    app.run(host='0.0.0.0', port=PORT, debug=False)