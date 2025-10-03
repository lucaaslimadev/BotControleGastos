#!/usr/bin/env python3
import requests
import time
import re
from sheets_abas_separadas import SheetsAbasSeparadas

TOKEN = "7907909261:AAFTVrpSpIDNL8CiB5dKnqrlJvB81x-4oDs"
sheets = SheetsAbasSeparadas()

print("🤖 Bot Simples iniciado!")

def processar_gasto(chat_id, texto, nome):
    valor_match = re.search(r'(\d+(?:[.,]\d{1,2})?)', texto)
    if valor_match:
        valor = float(valor_match.group().replace(',', '.'))
        descricao = re.sub(r'\d+(?:[.,]\d{1,2})?|r\$|reais?', '', texto, flags=re.IGNORECASE).strip()
        
        print(f"💰 Salvando: {descricao} - R$ {valor:.2f} para {nome}")
        
        if sheets.adicionar_gasto(chat_id, nome, descricao, valor, 'outros'):
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                         json={"chat_id": chat_id, "text": f"✅ {descricao} - R$ {valor:.2f}"})
            print("✅ Salvo com sucesso!")
        else:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                         json={"chat_id": chat_id, "text": "❌ Erro ao salvar"})
            print("❌ Erro ao salvar")

# Limpar mensagens antigas
r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
if r.json().get("result"):
    last_id = r.json()["result"][-1]["update_id"]
    requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}")
    print(f"🧹 Limpas {len(r.json()['result'])} mensagens antigas")

print("✅ Aguardando mensagens...")

offset = None
while True:
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", 
                        params={"timeout": 5, "offset": offset})
        data = r.json()
        
        if data.get("ok") and data["result"]:
            for update in data["result"]:
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    texto = msg.get("text", "").strip()
                    nome = msg["from"].get("first_name", f"User{chat_id}")
                    
                    print(f"📱 {nome} ({chat_id}): {texto}")
                    
                    if texto == "/start":
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                     json={"chat_id": chat_id, "text": f"🤖 Olá {nome}! Digite: mercado 50"})
                    elif texto.startswith('/'):
                        pass  # Ignorar outros comandos por agora
                    else:
                        processar_gasto(chat_id, texto, nome)
                
                offset = update["update_id"] + 1
        
        time.sleep(1)
    
    except KeyboardInterrupt:
        print("🛑 Bot parado")
        break
    except Exception as e:
        print(f"❌ Erro: {e}")
        time.sleep(3)