"""
Google Sheets Multi-usuário - Planilha separada por usuário
"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging
from config_telegram import TelegramConfig

logger = logging.getLogger(__name__)

class SheetsMultiUsuario:
    """Serviço Google Sheets com planilha separada por usuário"""
    
    def __init__(self):
        self.client = None
        self.user_sheets = {}  # Cache de planilhas por usuário
        self._connect()
    
    def _connect(self):
        """Conecta com Google Sheets"""
        try:
            creds = Credentials.from_service_account_file(
                TelegramConfig.CREDENTIALS_FILE, 
                scopes=TelegramConfig.SCOPES
            )
            self.client = gspread.authorize(creds)
            logger.info("✅ Google Sheets conectado")
        except Exception as e:
            logger.error(f"❌ Erro Google Sheets: {e}")
    
    def get_user_sheet(self, chat_id, nome_usuario):
        """Obtém planilha específica do usuário"""
        if chat_id in self.user_sheets:
            return self.user_sheets[chat_id]
        
        try:
            # Nome da planilha: "Gastos_NomeUsuario_ID"
            sheet_name = f"Gastos_{nome_usuario}_{chat_id}"
            
            try:
                # Tentar abrir planilha existente
                spreadsheet = self.client.open(sheet_name)
            except gspread.SpreadsheetNotFound:
                # Criar nova planilha
                spreadsheet = self.client.create(sheet_name)
                # Compartilhar com o email do usuário (opcional)
                # spreadsheet.share('email@usuario.com', perm_type='user', role='writer')
            
            sheet = spreadsheet.sheet1
            
            # Configurar cabeçalho se necessário
            headers = sheet.row_values(1) if sheet.row_count > 0 else []
            if not headers or headers != ["Data", "Descrição", "Valor", "Categoria"]:
                sheet.clear()
                sheet.append_row(["Data", "Descrição", "Valor", "Categoria"])
            
            # Cache da planilha
            self.user_sheets[chat_id] = {
                'sheet': sheet,
                'spreadsheet': spreadsheet,
                'sheet_id': spreadsheet.id
            }
            
            logger.info(f"✅ Planilha do usuário {nome_usuario} configurada")
            return self.user_sheets[chat_id]
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar planilha do usuário: {e}")
            return None
    
    def adicionar_gasto(self, chat_id, nome_usuario, descricao, valor, categoria):
        """Adiciona gasto na planilha do usuário"""
        user_sheet_data = self.get_user_sheet(chat_id, nome_usuario)
        if not user_sheet_data:
            return False
        
        try:
            hoje = datetime.now().strftime("%d/%m/%Y")
            user_sheet_data['sheet'].append_row([hoje, descricao, f"{valor:.2f}", categoria])
            logger.info(f"💰 Gasto de {nome_usuario}: {descricao} - R$ {valor:.2f}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar gasto: {e}")
            return False
    
    def calcular_saldo_mes(self, chat_id, nome_usuario):
        """Calcula total do mês do usuário"""
        user_sheet_data = self.get_user_sheet(chat_id, nome_usuario)
        if not user_sheet_data:
            return 0
        
        try:
            records = user_sheet_data['sheet'].get_all_records()
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
    
    def get_user_sheet_id(self, chat_id, nome_usuario):
        """Retorna ID da planilha do usuário"""
        user_sheet_data = self.get_user_sheet(chat_id, nome_usuario)
        return user_sheet_data['sheet_id'] if user_sheet_data else None
    
    def get_user_data(self, chat_id, nome_usuario):
        """Retorna todos os dados do usuário para dashboard"""
        user_sheet_data = self.get_user_sheet(chat_id, nome_usuario)
        if not user_sheet_data:
            return []
        
        try:
            return user_sheet_data['sheet'].get_all_records()
        except Exception as e:
            logger.error(f"❌ Erro ao obter dados: {e}")
            return []