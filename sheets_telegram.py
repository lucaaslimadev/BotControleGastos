"""
Google Sheets Service APENAS para Telegram
"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging
from config_telegram import TelegramConfig

logger = logging.getLogger(__name__)

class SheetsService:
    """Serviço Google Sheets para Telegram Bot"""
    
    def __init__(self):
        self.client = None
        self.sheet = None
        self._connect()
    
    def _connect(self):
        """Conecta com Google Sheets"""
        try:
            creds = Credentials.from_service_account_file(
                TelegramConfig.CREDENTIALS_FILE, 
                scopes=TelegramConfig.SCOPES
            )
            
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_key(TelegramConfig.SHEET_ID).sheet1
            
            # Configurar cabeçalho
            headers = self.sheet.row_values(1)
            if not headers or headers != ["Data", "Descrição", "Valor", "Categoria"]:
                self.sheet.clear()
                self.sheet.append_row(["Data", "Descrição", "Valor", "Categoria"])
            
            logger.info("✅ Google Sheets conectado")
            
        except Exception as e:
            logger.error(f"❌ Erro Google Sheets: {e}")
            self.sheet = None
    
    def is_connected(self):
        """Verifica conexão"""
        return self.sheet is not None
    
    def adicionar_gasto(self, descricao, valor, categoria):
        """Adiciona gasto à planilha"""
        if not self.is_connected():
            return False
        
        try:
            hoje = datetime.now().strftime("%d/%m/%Y")
            self.sheet.append_row([hoje, descricao, f"{valor:.2f}", categoria])
            logger.info(f"💰 Gasto adicionado: {descricao} - R$ {valor:.2f}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar gasto: {e}")
            return False
    
    def calcular_saldo_mes(self):
        """Calcula total do mês"""
        if not self.is_connected():
            return 0
        
        try:
            records = self.sheet.get_all_records()
            mes_atual = datetime.now().strftime("%m/%Y")
            total = 0
            
            for record in records:
                data = str(record.get('Data', ''))
                if mes_atual in data:
                    valor_str = str(record.get('Valor', '0')).replace(',', '.')
                    try:
                        total += float(valor_str)
                    except ValueError:
                        continue
            
            return total
        except Exception as e:
            logger.error(f"❌ Erro ao calcular saldo: {e}")
            return 0