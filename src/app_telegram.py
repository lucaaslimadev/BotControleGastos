"""
Bot Telegram - Controle de Gastos
Aplicação principal Flask para Telegram
"""
from flask import Flask, request, render_template
import logging
from datetime import datetime

# Imports locais
from .config import Config
from .sheets_service import SheetsService
from .telegram_service import TelegramService
from .categories import categorizar_gasto
from .utils import extrair_valor_melhorado, limpar_descricao, extrair_comando

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')

# Inicializar serviços
sheets_service = SheetsService()
telegram_service = TelegramService()

@app.route("/")
def home():
    """Página inicial"""
    return render_template('home.html', sheet_id=Config.SHEET_ID)

@app.route("/dashboard")
def dashboard():
    """Dashboard com estatísticas dos gastos"""
    try:
        if not sheets_service.is_connected():
            return "<h1>❌ Google Sheets não conectado</h1>", 500
        
        gastos = sheets_service.obter_todos_gastos()
        gastos_por_categoria = sheets_service.obter_gastos_por_categoria()
        produtos_mais_gastos = sheets_service.obter_produtos_mais_gastos(8)
        
        total_geral = sum(gastos_por_categoria.values()) if gastos_por_categoria else 0
        gastos_mes_atual = sheets_service.calcular_saldo_mes()
        
        return render_template('dashboard.html',
                             gastos=gastos,
                             gastos_por_categoria=gastos_por_categoria,
                             produtos_mais_gastos=produtos_mais_gastos,
                             total_geral=total_geral,
                             gastos_mes_atual=gastos_mes_atual,
                             sheet_id=Config.SHEET_ID)
    
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        return f"<h1>❌ Erro no Dashboard</h1><p>{str(e)}</p>", 500

@app.route("/webhook", methods=["POST"])
def webhook():
    """Endpoint do webhook do Telegram"""
    try:
        data = request.get_json()
        
        if not data or "message" not in data:
            return "ok", 200
        
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        
        if not text:
            return "ok", 200
        
        logger.info(f"📱 Mensagem de {chat_id}: '{text}'")
        
        # Processar comando ou gasto
        _processar_comando_ou_gasto(text, chat_id)
        
        return "ok", 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}")
        return "ok", 200

def _processar_comando_ou_gasto(text, chat_id):
    """Processa comando ou registra gasto"""
    # Comandos com /
    if text.startswith('/'):
        comando = text[1:].lower()
        _processar_comando(comando, text, chat_id)
    else:
        # Verificar comandos sem /
        comando = extrair_comando(text)
        if comando:
            _processar_comando(comando, text, chat_id)
        else:
            _processar_gasto(text, chat_id)

def _processar_comando(comando, text, chat_id):
    """Processa comandos específicos"""
    
    if comando == "saldo":
        total = sheets_service.calcular_saldo_mes()
        mes_atual = datetime.now().strftime("%m/%Y")
        telegram_service.enviar_saldo_mensal(chat_id, total, mes_atual)
    
    elif comando == "hoje":
        gastos_hoje, total = sheets_service.obter_gastos_hoje()
        telegram_service.enviar_lista_gastos(chat_id, gastos_hoje, "📅 Gastos de Hoje")
    
    elif comando == "exportar":
        link_planilha = f"https://docs.google.com/spreadsheets/d/{Config.SHEET_ID}/edit"
        telegram_service.enviar_mensagem_formatada(
            chat_id,
            "📊 Planilha de Gastos",
            f"Acesse sua planilha completa:\n{link_planilha}",
            "Mantenha seus gastos sempre organizados!"
        )
    
    elif comando in ["deletar", "apagar"]:
        if sheets_service.deletar_ultimo_gasto():
            telegram_service.enviar_mensagem(chat_id, "✅ Último gasto deletado com sucesso!")
        else:
            telegram_service.enviar_mensagem(chat_id, "❌ Erro ao deletar gasto")
    
    elif comando in ["ajuda", "help", "comandos", "start"]:
        telegram_service.enviar_ajuda(chat_id)

def _processar_gasto(text, chat_id):
    """Processa registro de gasto"""
    valor = extrair_valor_melhorado(text)
    
    if valor:
        descricao = limpar_descricao(text)
        categoria = categorizar_gasto(descricao)
        
        if sheets_service.adicionar_gasto(descricao, valor, categoria):
            telegram_service.enviar_mensagem_formatada(
                chat_id,
                "✅ Gasto Registrado",
                f"{descricao} - R$ {valor:.2f}",
                f"📂 Categoria: {categoria.title()}"
            )
            
            logger.info(f"💰 GASTO REGISTRADO: {descricao} - R$ {valor:.2f} ({categoria})")
        else:
            telegram_service.enviar_mensagem(chat_id, "❌ Erro ao salvar gasto. Tente novamente.")
    else:
        telegram_service.enviar_erro_valor(chat_id)

def main():
    """Função principal"""
    logger.info("🚀 Iniciando Bot Telegram - Controle de Gastos")
    logger.info(f"📊 Google Sheets: {'✅ Conectado' if sheets_service.is_connected() else '❌ Desconectado'}")
    logger.info(f"🤖 Telegram: {'✅ Configurado' if Config.TELEGRAM_TOKEN else '❌ Não configurado'}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.FLASK_DEBUG
    )

if __name__ == "__main__":
    main()