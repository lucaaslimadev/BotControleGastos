#!/usr/bin/env python3
import requests
import time

TOKEN = "7907909261:AAFTVrpSpIDNL8CiB5dKnqrlJvB81x-4oDs"

print("🤖 Bot ultra simples iniciado!")

offset = None
while True:
    try:
        # Buscar mensagens
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
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    
                    print(f"📱 Recebido: '{text}' de {chat_id}")
                    
                    # Responder qualquer mensagem
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                json={"chat_id": chat_id, "text": f"Recebi: {text}"})
                
                offset = update["update_id"] + 1
        
        time.sleep(1)
    
    except KeyboardInterrupt:
        print("Bot parado!")
        break
    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(2)