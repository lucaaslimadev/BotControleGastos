#!/usr/bin/env python3
"""
Servidor Principal - Mantém TODAS as funcionalidades
"""
import os
import threading
import time
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
PORT = int(os.getenv('PORT', 8000))

@app.route('/health')
def health():
    return {"status": "ok"}

@app.route('/')
def home():
    # Importar e executar dashboard completo
    from dashboard_completo import dashboard
    return dashboard()

# Importar TODAS as rotas do dashboard
from dashboard_completo import app as dashboard_app
for rule in dashboard_app.url_map.iter_rules():
    if rule.endpoint not in ['static', 'health']:
        try:
            app.add_url_rule(
                rule.rule, 
                rule.endpoint,
                dashboard_app.view_functions[rule.endpoint],
                methods=list(rule.methods)
            )
        except:
            pass

def start_bot():
    """Inicia bot completo em background"""
    time.sleep(3)  # Aguarda servidor iniciar
    os.system('python bot_completo.py &')

if __name__ == "__main__":
    print(f"🚀 Iniciando sistema completo na porta {PORT}")
    
    # Bot em background
    threading.Thread(target=start_bot, daemon=True).start()
    
    # Servidor principal
    app.run(host='0.0.0.0', port=PORT, debug=False)