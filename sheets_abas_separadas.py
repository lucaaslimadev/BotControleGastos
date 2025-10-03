"""
Google Sheets com Abas Separadas por Usuário
"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging
from config_telegram import TelegramConfig

logger = logging.getLogger(__name__)

class SheetsAbasSeparadas:
    """Serviço Google Sheets com aba separada por usuário"""
    
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.user_sheets = {}
        self._connect()
    
    def _connect(self):
        """Conecta com Google Sheets"""
        try:
            creds = Credentials.from_service_account_file(
                TelegramConfig.CREDENTIALS_FILE, 
                scopes=TelegramConfig.SCOPES
            )
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(TelegramConfig.SHEET_ID)
            logger.info("✅ Google Sheets conectado")
        except Exception as e:
            logger.error(f"❌ Erro Google Sheets: {e}")
    
    def get_user_sheet(self, chat_id, nome_usuario):
        """Obtém aba específica do usuário"""
        if chat_id in self.user_sheets:
            return self.user_sheets[chat_id]
        
        try:
            sheet_name = f"{nome_usuario}_{chat_id}"
            
            try:
                # Tentar abrir aba existente
                sheet = self.spreadsheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                # Criar nova aba
                sheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                # Configurar cabeçalho
                sheet.append_row(["Data", "Descrição", "Valor", "Categoria"])
            
            # Cache da aba
            self.user_sheets[chat_id] = sheet
            
            logger.info(f"✅ Aba do usuário {nome_usuario} configurada")
            return sheet
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar aba do usuário: {e}")
            return None
    
    def adicionar_gasto(self, chat_id, nome_usuario, descricao, valor, categoria):
        """Adiciona gasto na aba do usuário"""
        sheet = self.get_user_sheet(chat_id, nome_usuario)
        if not sheet:
            return False
        
        try:
            hoje = datetime.now().strftime("%d/%m/%Y")
            sheet.append_row([hoje, descricao, f"{valor:.2f}", categoria])
            logger.info(f"💰 Gasto de {nome_usuario}: {descricao} - R$ {valor:.2f}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar gasto: {e}")
            return False
    
    def calcular_saldo_mes(self, chat_id, nome_usuario):
        """Calcula total do mês do usuário"""
        sheet = self.get_user_sheet(chat_id, nome_usuario)
        if not sheet:
            return 0
        
        try:
            records = sheet.get_all_records()
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
    
    def get_user_data(self, chat_id, nome_usuario):
        """Retorna todos os dados do usuário"""
        sheet = self.get_user_sheet(chat_id, nome_usuario)
        if not sheet:
            return []
        
        try:
            return sheet.get_all_records()
        except Exception as e:
            logger.error(f"❌ Erro ao obter dados: {e}")
            return []