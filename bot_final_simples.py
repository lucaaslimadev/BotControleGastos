#!/usr/bin/env python3
import requests
import time
import sys
sys.path.append('.')
from src.sheets_service import SheetsService
from src.utils import extrair_valor_melhorado, limpar_descricao
from src.categories import categorizar_gasto

TOKEN = "7907909261:AAFTVrpSpIDNL8CiB5dKnqrlJvB81x-4oDs"
sheets = SheetsService()

print("🤖 Bot iniciado!")
print(f"📊 Planilha: {'✅' if sheets.is_connected() else '❌'}")

# Limpar mensagens antigas
r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
if r.json().get("result"):
    last_id = r.json()["result"][-1]["update_id"]
    requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}")
    print(f"🧹 Limpas {len(r.json()['result'])} mensagens antigas")

print("✅ Aguardando mensagens NOVAS...")

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
                    
                    print(f"📱 NOVA MENSAGEM: '{texto}' de {chat_id}")
                    
                    if texto == "/start":
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                    json={"chat_id": chat_id, "text": "🤖 Bot funcionando! Digite: mercado 50"})
                    else:
                        valor = extrair_valor_melhorado(texto)
                        if valor:
                            descricao = limpar_descricao(texto)
                            categoria = categorizar_gasto(descricao)
                            
                            if sheets.adicionar_gasto(descricao, valor, categoria):
                                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                            json={"chat_id": chat_id, "text": f"✅ {descricao} - R$ {valor:.2f}"})
                                print(f"💰 SALVO: {descricao} - R$ {valor:.2f}")
                            else:
                                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                            json={"chat_id": chat_id, "text": "❌ Erro ao salvar"})
                
                offset = update["update_id"] + 1
        
        time.sleep(1)
    
    except KeyboardInterrupt:
        print("🛑 Bot parado")
        break
    except Exception as e:
        print(f"❌ Erro: {e}")
        time.sleep(3)