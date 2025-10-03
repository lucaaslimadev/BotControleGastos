#!/usr/bin/env python3
"""
Teste rápido da API do Telegram
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')

def testar_bot():
    """Testa se o bot está funcionando"""
    if not TOKEN:
        print("❌ TELEGRAM_TOKEN não encontrado no .env")
        return False
    
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('ok'):
            bot_info = data['result']
            print(f"✅ Bot conectado com sucesso!")
            print(f"📛 Nome: {bot_info['first_name']}")
            print(f"🔗 Username: @{bot_info['username']}")
            print(f"🆔 ID: {bot_info['id']}")
            return True
        else:
            print(f"❌ Erro: {data.get('description', 'Token inválido')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    testar_bot()