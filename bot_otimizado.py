#!/usr/bin/env python3
"""
Bot Telegram Otimizado - Resposta Rápida
"""
import requests
import time
import re
import threading
from datetime import datetime
from config_telegram import TelegramConfig
from sheets_telegram import SheetsService

class BotOtimizado:
    def __init__(self):
        TelegramConfig.validate()
        self.token = TelegramConfig.TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.sheets = SheetsService()
        
        # Cache de sessão HTTP para conexões rápidas
        self.session = requests.Session()
        self.session.timeout = 5
        
        # Categorias otimizadas
        self.categorias = {
            'alimentação': ['mercado', 'supermercado', 'restaurante', 'lanche', 'pizza', 'comida', 'ifood'],
            'transporte': ['uber', 'taxi', 'gasolina', 'combustível', 'ônibus', '99'],
            'saúde': ['farmácia', 'médico', 'hospital', 'remédio', 'consulta'],
            'lazer': ['cinema', 'bar', 'show', 'viagem', 'netflix'],
            'casa': ['luz', 'água', 'internet', 'aluguel', 'condomínio'],
            'outros': []
        }
    
    def extrair_valor(self, texto):
        """Extração otimizada de valor"""
        match = re.search(r'(\d+(?:[.,]\d{1,2})?)', re.sub(r'r\$|reais?', '', texto, flags=re.IGNORECASE))
        return float(match.group().replace(',', '.')) if match else None
    
    def categorizar(self, descricao):
        """Categorização otimizada"""
        desc_lower = descricao.lower()
        for cat, palavras in self.categorias.items():
            if any(p in desc_lower for p in palavras):
                return cat
        return 'outros'
    
    def enviar_rapido(self, chat_id, texto):
        """Envio otimizado - não bloqueia"""
        def enviar():
            try:
                self.session.post(f"{self.base_url}/sendMessage", 
                                json={"chat_id": chat_id, "text": texto})
            except:
                pass
        
        threading.Thread(target=enviar, daemon=True).start()
    
    def salvar_async(self, descricao, valor, categoria, chat_id):
        """Salvamento assíncrono - não bloqueia resposta"""
        def salvar():
            try:
                if self.sheets.adicionar_gasto(descricao, valor, categoria):
                    self.enviar_rapido(chat_id, f"✅ {descricao} - R$ {valor:.2f}\n📂 {categoria.title()}")
                else:
                    self.enviar_rapido(chat_id, "❌ Erro ao salvar")
            except:
                self.enviar_rapido(chat_id, "❌ Erro ao salvar")
        
        threading.Thread(target=salvar, daemon=True).start()
    
    def processar_mensagem(self, chat_id, texto):
        """Processamento otimizado"""
        if texto.startswith('/'):
            comando = texto[1:].lower()
            
            if comando == "start":
                self.enviar_rapido(chat_id, "🤖 Bot funcionando!\n\nDigite: mercado 50")
            elif comando == "saldo":
                # Resposta imediata, cálculo em background
                self.enviar_rapido(chat_id, "💰 Calculando saldo...")
                def calcular():
                    total = self.sheets.calcular_saldo_mes()
                    mes = datetime.now().strftime("%m/%Y")
                    self.enviar_rapido(chat_id, f"💰 Saldo {mes}: R$ {total:.2f}")
                threading.Thread(target=calcular, daemon=True).start()
        else:
            # Processar gasto
            valor = self.extrair_valor(texto)
            if valor:
                descricao = re.sub(r'\d+(?:[.,]\d{1,2})?|r\$|reais?', '', texto, flags=re.IGNORECASE).strip()
                categoria = self.categorizar(descricao)
                
                # Resposta IMEDIATA
                self.enviar_rapido(chat_id, f"⏳ Salvando: {descricao} - R$ {valor:.2f}")
                
                # Salvamento em background
                self.salvar_async(descricao, valor, categoria, chat_id)
            else:
                self.enviar_rapido(chat_id, "❌ Valor não identificado")
    
    def executar(self):
        """Loop principal otimizado"""
        print("🚀 Bot Otimizado iniciado!")
        
        # Limpar mensagens antigas
        try:
            r = self.session.get(f"{self.base_url}/getUpdates")
            if r.json().get("result"):
                last_id = r.json()["result"][-1]["update_id"]
                self.session.get(f"{self.base_url}/getUpdates?offset={last_id + 1}")
        except:
            pass
        
        offset = None
        while True:
            try:
                r = self.session.get(f"{self.base_url}/getUpdates", 
                                   params={"timeout": 3, "offset": offset})
                data = r.json()
                
                if data.get("ok") and data["result"]:
                    for update in data["result"]:
                        if "message" in update:
                            msg = update["message"]
                            chat_id = msg["chat"]["id"]
                            texto = msg.get("text", "").strip()
                            
                            if texto:
                                print(f"📱 {chat_id}: {texto}")
                                self.processar_mensagem(chat_id, texto)
                        
                        offset = update["update_id"] + 1
                
                time.sleep(0.5)  # Polling mais rápido
                
            except KeyboardInterrupt:
                break
            except:
                time.sleep(2)

if __name__ == "__main__":
    bot = BotOtimizado()
    bot.executar()