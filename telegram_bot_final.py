#!/usr/bin/env python3
"""
Bot Telegram - Controle de Gastos
Versão Final Limpa - APENAS Telegram
"""
import requests
import time
import logging
import re
from datetime import datetime
from config_telegram import TelegramConfig
from sheets_telegram import SheetsService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Bot Telegram para Controle de Gastos"""
    
    def __init__(self):
        # Validar configurações
        TelegramConfig.validate()
        
        self.token = TelegramConfig.TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        # Inicializar serviços
        self.sheets = SheetsService()
        
        # Categorias
        self.categorias = {
            'alimentação': ['mercado', 'supermercado', 'restaurante', 'lanche', 'pizza', 'comida'],
            'transporte': ['uber', 'taxi', 'gasolina', 'combustível', 'ônibus'],
            'saúde': ['farmácia', 'médico', 'hospital', 'remédio'],
            'lazer': ['cinema', 'bar', 'show', 'viagem'],
            'casa': ['luz', 'água', 'internet', 'aluguel'],
            'outros': []
        }
    
    def extrair_valor(self, texto):
        """Extrai valor monetário do texto"""
        # Remove R$, reais, etc.
        texto_limpo = re.sub(r'(r\$|reais?|real)', '', texto, flags=re.IGNORECASE)
        
        # Procura números
        match = re.search(r'\d+(?:[.,]\d{1,2})?', texto_limpo)
        if match:
            valor = match.group().replace(',', '.')
            try:
                return float(valor)
            except ValueError:
                pass
        return None
    
    def limpar_descricao(self, texto):
        """Remove valores da descrição"""
        descricao = re.sub(r'\d+(?:[.,]\d{1,2})?|r\$|reais?|real', '', texto, flags=re.IGNORECASE)
        return re.sub(r'\s+', ' ', descricao).strip()
    
    def categorizar(self, descricao):
        """Categoriza o gasto"""
        descricao_lower = descricao.lower()
        
        for categoria, palavras in self.categorias.items():
            if any(palavra in descricao_lower for palavra in palavras):
                return categoria
        
        return 'outros'
    
    def enviar_mensagem(self, chat_id, texto):
        """Envia mensagem para o Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {"chat_id": chat_id, "text": texto}
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")
            return False
    
    def processar_comando(self, comando, chat_id):
        """Processa comandos do bot"""
        if comando == "start":
            texto = """🤖 *Bot Controle de Gastos*

✅ Funcionando!

*Como usar:*
• mercado 50
• uber 25.50
• R$ 100 farmácia

*Comandos:*
/saldo - Total do mês
/ajuda - Ajuda"""
            
            self.enviar_mensagem(chat_id, texto)
        
        elif comando == "saldo":
            total = self.sheets.calcular_saldo_mes()
            mes = datetime.now().strftime("%m/%Y")
            self.enviar_mensagem(chat_id, f"💰 Saldo {mes}: R$ {total:.2f}")
        
        elif comando == "ajuda":
            texto = """🤖 *Comandos*

💰 *Registrar gastos:*
• mercado 50
• uber 25.50
• R$ 100 farmácia

📊 *Consultas:*
• /saldo - Total do mês
• /ajuda - Esta mensagem"""
            
            self.enviar_mensagem(chat_id, texto)
    
    def processar_gasto(self, texto, chat_id):
        """Processa registro de gasto"""
        valor = self.extrair_valor(texto)
        
        if valor:
            descricao = self.limpar_descricao(texto)
            categoria = self.categorizar(descricao)
            
            logger.info(f"💰 Processando: {descricao} - R$ {valor:.2f} ({categoria})")
            
            if self.sheets.adicionar_gasto(descricao, valor, categoria):
                resposta = f"✅ {descricao} - R$ {valor:.2f}\n📂 {categoria.title()}"
                self.enviar_mensagem(chat_id, resposta)
                logger.info(f"✅ Gasto salvo: {descricao} - R$ {valor:.2f}")
            else:
                self.enviar_mensagem(chat_id, "❌ Erro ao salvar gasto")
        else:
            self.enviar_mensagem(chat_id, "❌ Valor não identificado\nExemplo: mercado 50")
    
    def processar_mensagem(self, message):
        """Processa mensagem recebida"""
        try:
            chat_id = message["chat"]["id"]
            texto = message.get("text", "").strip()
            
            if not texto:
                return
            
            logger.info(f"📱 Mensagem de {chat_id}: '{texto}'")
            
            # Comandos
            if texto.startswith('/'):
                comando = texto[1:].lower()
                self.processar_comando(comando, chat_id)
            else:
                # Gasto
                self.processar_gasto(texto, chat_id)
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")
    
    def obter_updates(self, offset=None):
        """Obtém atualizações do Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"timeout": 10}
            if offset:
                params["offset"] = offset
            
            response = requests.get(url, params=params, timeout=15)
            return response.json() if response.status_code == 200 else None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter updates: {e}")
            return None
    
    def limpar_mensagens_antigas(self):
        """Limpa mensagens antigas para evitar loop"""
        try:
            response = requests.get(f"{self.base_url}/getUpdates", timeout=10)
            data = response.json()
            
            if data.get("ok") and data["result"]:
                last_id = data["result"][-1]["update_id"]
                requests.get(f"{self.base_url}/getUpdates?offset={last_id + 1}", timeout=10)
                logger.info(f"🧹 Ignoradas {len(data['result'])} mensagens antigas")
                return last_id + 1
            
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao limpar mensagens: {e}")
            return None
    
    def executar(self):
        """Executa o bot"""
        logger.info("🚀 Iniciando Bot Telegram - Controle de Gastos")
        logger.info(f"📊 Google Sheets: {'✅ Conectado' if self.sheets.is_connected() else '❌ Desconectado'}")
        
        if not self.sheets.is_connected():
            logger.error("❌ Google Sheets não conectado. Parando bot.")
            return
        
        # Limpar mensagens antigas
        offset = self.limpar_mensagens_antigas()
        
        logger.info("✅ Bot aguardando mensagens NOVAS...")
        
        while True:
            try:
                updates = self.obter_updates(offset)
                
                if updates and updates.get("ok") and updates["result"]:
                    for update in updates["result"]:
                        if "message" in update:
                            self.processar_mensagem(update["message"])
                        
                        offset = update["update_id"] + 1
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop principal: {e}")
                time.sleep(5)

def main():
    """Função principal"""
    try:
        bot = TelegramBot()
        bot.executar()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()