"""
Configurações APENAS para Telegram Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

class TelegramConfig:
    """Configurações do Telegram Bot"""
    
    # Telegram
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # Google Sheets
    SHEET_ID = os.getenv('SHEET_ID')
    CREDENTIALS_FILE = 'config/credentials.json'
    
    # Google Sheets Scopes
    SCOPES = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    @classmethod
    def validate(cls):
        """Valida configurações"""
        if not cls.TOKEN:
            raise ValueError("❌ TELEGRAM_TOKEN não encontrado")
        if not cls.SHEET_ID:
            raise ValueError("❌ SHEET_ID não encontrado")
        return True