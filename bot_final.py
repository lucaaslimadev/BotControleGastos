#!/usr/bin/env python3
import requests
import time
from src.sheets_service import SheetsService
from src.utils import extrair_valor_melhorado, limpar_descricao
from src.categories import categorizar_gasto

TOKEN = "7907909261:AAFTVrpSpIDNL8CiB5dKnqrlJvB81x-4oDs"
sheets = SheetsService()

print("🚀 Bot Telegram iniciado!")
print("📊 Planilha conectada!")

def enviar_mensagem(chat_id, texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": texto})

offset = None
while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        params = {"timeout": 5}
        if offset:
            params["offset"] = offset
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("ok"):
            for update in data["result"]:
                if "message" in update:
                    message = update["message"]
                    texto = message.get("text", "")
                    chat_id = message["chat"]["id"]
                    
                    if texto:
                        print(f"📱 Recebido: '{texto}' de {chat_id}")
                        
                        if texto == "/start":
                            enviar_mensagem(chat_id, "✅ Bot funcionando! Digite: mercado 50")
                        else:
                            valor = extrair_valor_melhorado(texto)
                            if valor:
                                descricao = limpar_descricao(texto)
                                categoria = categorizar_gasto(descricao)
                                
                                if sheets.adicionar_gasto(descricao, valor, categoria):
                                    enviar_mensagem(chat_id, f"✅ {descricao} - R$ {valor:.2f}")
                                    print(f"💰 SALVO: {descricao} - R$ {valor:.2f}")
                                else:
                                    enviar_mensagem(chat_id, "❌ Erro ao salvar")
                            else:
                                enviar_mensagem(chat_id, "❌ Valor não identificado")
                
                offset = update["update_id"] + 1
    
    except KeyboardInterrupt:
        print("Bot parado!")
        break
    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(2)