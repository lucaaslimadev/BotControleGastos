#!/usr/bin/env python3
"""
App Principal - Bot + Dashboard para Railway
"""
import os
import threading
import subprocess
import sys
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
PORT = int(os.getenv('PORT', 8000))

# Rota principal redireciona para o dashboard
@app.route('/')
def home():
    from dashboard_completo import dashboard
    return dashboard()

@app.route('/health')
def health():
    return {"status": "ok", "bot": "running"}

# Importar todas as rotas do dashboard
from dashboard_completo import app as dashboard_app

# Registrar todas as rotas do dashboard no app principal
for rule in dashboard_app.url_map.iter_rules():
    if rule.endpoint != 'static':
        app.add_url_rule(
            rule.rule,
            rule.endpoint + '_dashboard',
            dashboard_app.view_functions[rule.endpoint],
            methods=rule.methods
        )

def start_bot():
    """Inicia o bot em processo separado"""
    try:
        subprocess.run([sys.executable, 'bot_completo.py'])
    except Exception as e:
        print(f"Erro ao iniciar bot: {e}")

if __name__ == "__main__":
    print(f"🚀 Iniciando sistema completo na porta {PORT}")
    
    # Iniciar bot em thread separada
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Iniciar Flask app
    app.run(host='0.0.0.0', port=PORT, debug=False)