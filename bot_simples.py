#!/usr/bin/env python3
import requests
import time
from src.sheets_service import SheetsService
from src.utils import extrair_valor_melhorado, limpar_descricao
from src.categories import categorizar_gasto

TOKEN = "7907909261:AAFTVrpSpIDNL8CiB5dKnqrlJvB81x-4oDs"
sheets = SheetsService()

def enviar_mensagem(chat_id, texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": texto})

def processar_mensagem(texto, chat_id):
    print(f"Processando: {texto}")
    
    if texto == "/start":
        enviar_mensagem(chat_id, "Bot funcionando! Digite: mercado 50")
        return
    
    valor = extrair_valor_melhorado(texto)
    if valor:
        descricao = limpar_descricao(texto)
        categoria = categorizar_gasto(descricao)
        
        if sheets.adicionar_gasto(descricao, valor, categoria):
            enviar_mensagem(chat_id, f"✅ {descricao} - R$ {valor:.2f}")
            print(f"SALVO: {descricao} - R$ {valor:.2f}")
        else:
            enviar_mensagem(chat_id, "❌ Erro ao salvar")

offset = None
print("Bot iniciado...")

while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        params = {"timeout": 10}
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
                        processar_mensagem(texto, chat_id)
                
                offset = update["update_id"] + 1
    
    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(5)