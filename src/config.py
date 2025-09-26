"""
Configurações da aplicação
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações base da aplicação"""
    
    # WhatsApp Business API
    WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
    PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
    
    # Google Sheets
    SHEET_ID = os.getenv('SHEET_ID')
    CREDENTIALS_FILE = 'config/credentials.json'
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 8000))
    HOST = '0.0.0.0'
    
    # Para produção, desabilitar debug
    if FLASK_ENV == 'production':
        FLASK_DEBUG = False
    
    # Google Sheets Scopes
    GOOGLE_SHEETS_SCOPES = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Validação de configurações obrigatórias
    @classmethod
    def validate(cls):
        """Valida se todas as configurações obrigatórias estão definidas"""
        required_configs = [
            'WHATSAPP_TOKEN',
            'PHONE_NUMBER_ID',
            'VERIFY_TOKEN',
            'SHEET_ID'
        ]
        
        missing_configs = []
        for config in required_configs:
            if not getattr(cls, config):
                missing_configs.append(config)
        
        if missing_configs:
            raise ValueError(f"Configurações obrigatórias não definidas: {', '.join(missing_configs)}")
        
        return True