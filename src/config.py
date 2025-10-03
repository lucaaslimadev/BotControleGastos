"""
Configurações da aplicação - Telegram Bot
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações base da aplicação"""
    
    # Telegram Bot
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # Google Sheets
    SHEET_ID = os.getenv('SHEET_ID')
    CREDENTIALS_FILE = 'config/credentials.json'
    GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')  # JSON como string
    
    # Google Sheets Scopes
    GOOGLE_SHEETS_SCOPES = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Validação de configurações obrigatórias
    @classmethod
    def validate(cls):
        """Valida se todas as configurações obrigatórias estão definidas"""
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN não definido no .env")
        
        if not cls.SHEET_ID:
            raise ValueError("SHEET_ID não definido no .env")
        
        return True