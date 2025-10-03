#!/usr/bin/env python3
"""
Bot com Planilhas Separadas por Usuário
"""
import json
import requests
import threading
import re
from datetime import datetime
from config_telegram import TelegramConfig
from sheets_multiusuario import SheetsMultiUsuario

class BotPlanilhasSeparadas:
    def __init__(self):
        TelegramConfig.validate()
        self.token = TelegramConfig.TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.sheets = SheetsMultiUsuario()
        
        # Cache de sessão HTTP
        self.session = requests.Session()
        self.session.timeout = 5
        
        # Usuários e configurações
        self.usuarios_file = 'usuarios.json'
        self.carregar_usuarios()
        
        # Categorias
        self.categorias = {
            'alimentação': ['mercado', 'supermercado', 'restaurante', 'lanche', 'pizza', 'comida', 'ifood'],
            'transporte': ['uber', 'taxi', 'gasolina', 'combustível', 'ônibus', '99'],
            'saúde': ['farmácia', 'médico', 'hospital', 'remédio', 'consulta'],
            'lazer': ['cinema', 'bar', 'show', 'viagem', 'netflix'],
            'casa': ['luz', 'água', 'internet', 'aluguel', 'condomínio'],
            'outros': []
        }
    
    def carregar_usuarios(self):
        """Carrega usuários"""
        try:
            with open(self.usuarios_file, 'r') as f:
                self.usuarios_data = json.load(f)
        except FileNotFoundError:
            self.usuarios_data = {
                "usuarios_autorizados": [
                    {"chat_id": 8077221512, "nome": "Lucas", "ativo": True, "admin": True}
                ],
                "configuracoes": {"permitir_novos_usuarios": False}
            }
            self.salvar_usuarios()
    
    def salvar_usuarios(self):
        """Salva usuários"""
        with open(self.usuarios_file, 'w') as f:
            json.dump(self.usuarios_data, f, indent=2)
    
    def get_usuario(self, chat_id):
        """Obtém dados do usuário"""
        return next((u for u in self.usuarios_data["usuarios_autorizados"] 
                    if u["chat_id"] == chat_id), None)
    
    def adicionar_usuario_automatico(self, chat_id, nome):
        """Adiciona usuário automaticamente"""
        if not self.get_usuario(chat_id):
            self.usuarios_data["usuarios_autorizados"].append({
                "chat_id": chat_id,
                "nome": nome,
                "ativo": True,
                "admin": False
            })
            self.salvar_usuarios()
            return True
        return False
    
    def extrair_valor(self, texto):
        """Extrai valor do texto"""
        match = re.search(r'(\d+(?:[.,]\d{1,2})?)', re.sub(r'r\$|reais?', '', texto, flags=re.IGNORECASE))
        return float(match.group().replace(',', '.')) if match else None
    
    def categorizar(self, descricao):
        """Categoriza gasto"""
        desc_lower = descricao.lower()
        for cat, palavras in self.categorias.items():
            if any(p in desc_lower for p in palavras):
                return cat
        return 'outros'
    
    def enviar_rapido(self, chat_id, texto):
        """Envio rápido"""
        def enviar():
            try:
                self.session.post(f"{self.base_url}/sendMessage", 
                                json={"chat_id": chat_id, "text": texto})
            except:
                pass
        threading.Thread(target=enviar, daemon=True).start()
    
    def processar_mensagem(self, chat_id, texto, nome_usuario):
        """Processa mensagem com planilha separada"""
        # Auto-adicionar usuário se permitido
        usuario = self.get_usuario(chat_id)
        if not usuario and self.usuarios_data["configuracoes"]["permitir_novos_usuarios"]:
            self.adicionar_usuario_automatico(chat_id, nome_usuario)
            usuario = self.get_usuario(chat_id)
            self.enviar_rapido(chat_id, f"🎉 Bem-vindo {nome_usuario}!\n\nSua planilha pessoal foi criada.")
        
        if not usuario or not usuario["ativo"]:
            self.enviar_rapido(chat_id, "❌ Usuário não autorizado")
            return
        
        # Comandos
        if texto.startswith('/'):
            comando = texto[1:].lower()
            
            if comando == "start":
                sheet_id = self.sheets.get_user_sheet_id(chat_id, usuario["nome"])
                msg = f"""🤖 *Olá {usuario["nome"]}!*

✅ Sua planilha pessoal está pronta!

*Como usar:*
• mercado 50
• uber 25.50  
• R$ 100 farmácia

*Comandos:*
/saldo - Seu saldo
/planilha - Link da sua planilha
/dashboard - Seu dashboard pessoal"""
                
                self.enviar_rapido(chat_id, msg)
            
            elif comando == "saldo":
                def calcular():
                    total = self.sheets.calcular_saldo_mes(chat_id, usuario["nome"])
                    mes = datetime.now().strftime("%m/%Y")
                    self.enviar_rapido(chat_id, f"💰 Seu saldo {mes}: R$ {total:.2f}")
                threading.Thread(target=calcular, daemon=True).start()
            
            elif comando == "planilha":
                sheet_id = self.sheets.get_user_sheet_id(chat_id, usuario["nome"])
                if sheet_id:
                    link = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
                    self.enviar_rapido(chat_id, f"📊 *Sua Planilha Pessoal*\n\n{link}")
            
            elif comando == "dashboard":
                self.enviar_rapido(chat_id, f"📊 *Seu Dashboard Pessoal*\n\nhttp://localhost:8001/user/{chat_id}")
        
        else:
            # Processar gasto na planilha do usuário
            valor = self.extrair_valor(texto)
            if valor:
                descricao = re.sub(r'\d+(?:[.,]\d{1,2})?|r\$|reais?', '', texto, flags=re.IGNORECASE).strip()
                categoria = self.categorizar(descricao)
                
                # Resposta imediata
                self.enviar_rapido(chat_id, f"⏳ Salvando na sua planilha...")
                
                # Salvamento em background
                def salvar():
                    if self.sheets.adicionar_gasto(chat_id, usuario["nome"], descricao, valor, categoria):
                        self.enviar_rapido(chat_id, f"✅ {descricao} - R$ {valor:.2f}\n📂 {categoria.title()}")
                    else:
                        self.enviar_rapido(chat_id, "❌ Erro ao salvar")
                
                threading.Thread(target=salvar, daemon=True).start()
            else:
                self.enviar_rapido(chat_id, "❌ Valor não identificado")
    
    def executar(self):
        """Executa bot"""
        print("🚀 Bot com Planilhas Separadas iniciado!")
        
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
                            nome_usuario = msg["from"].get("first_name", f"User{chat_id}")
                            
                            if texto:
                                print(f"📱 {nome_usuario} ({chat_id}): {texto}")
                                self.processar_mensagem(chat_id, texto, nome_usuario)
                        
                        offset = update["update_id"] + 1
                
            except KeyboardInterrupt:
                break
            except:
                pass

if __name__ == "__main__":
    bot = BotPlanilhasSeparadas()
    bot.executar()