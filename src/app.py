"""
Bot WhatsApp - Controle de Gastos
Aplicação principal Flask
"""
from flask import Flask, request, render_template, url_for
import logging
from datetime import datetime

# Imports locais
from .config import Config
from .sheets_service import SheetsService
from .whatsapp_service import WhatsAppService
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

# Validar configurações
try:
    Config.validate()
    logger.info("✅ Configurações validadas com sucesso")
except ValueError as e:
    logger.error(f"❌ Erro de configuração: {e}")
    exit(1)

# Inicializar serviços
sheets_service = SheetsService()
whatsapp_service = WhatsAppService()

@app.route("/")
def home():
    """Página inicial"""
    return render_template('home.html', sheet_id=Config.SHEET_ID)

@app.route("/health")
def health_check():
    """Endpoint de health check"""
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "google_sheets": sheets_service.is_connected(),
            "whatsapp": bool(Config.WHATSAPP_TOKEN)
        }
    }
    return status

@app.route("/dashboard")
def dashboard():
    """Dashboard com estatísticas dos gastos"""
    try:
        # Obter dados
        gastos = sheets_service.obter_todos_gastos()
        gastos_por_categoria = sheets_service.obter_gastos_por_categoria()
        
        # Calcular estatísticas
        total_geral = sum(gastos_por_categoria.values())
        gastos_mes_atual = sheets_service.calcular_saldo_mes()
        
        return render_template('dashboard.html',
                             gastos=gastos,
                             gastos_por_categoria=gastos_por_categoria,
                             total_geral=total_geral,
                             gastos_mes_atual=gastos_mes_atual,
                             sheet_id=Config.SHEET_ID)
    
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        return f"Erro ao carregar dashboard: {e}", 500

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """Endpoint do webhook do WhatsApp"""
    
    if request.method == "GET":
        return _verificar_webhook()
    
    elif request.method == "POST":
        return _processar_mensagem()

def _verificar_webhook():
    """Verifica o webhook do WhatsApp"""
    verify_token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    logger.info(f"Verificação webhook - Token: {verify_token}")
    
    if verify_token == Config.VERIFY_TOKEN:
        logger.info("✅ Webhook verificado com sucesso!")
        return challenge
    else:
        logger.error("❌ Token de verificação inválido")
        return "Erro de verificação", 403

def _processar_mensagem():
    """Processa mensagem recebida do WhatsApp"""
    try:
        data = request.get_json()
        
        # Validar estrutura do webhook
        if not _validar_estrutura_webhook(data):
            return "ok", 200
        
        # Extrair dados da mensagem
        message_data = _extrair_dados_mensagem(data)
        if not message_data:
            return "ok", 200
        
        text, number = message_data
        logger.info(f"📱 Mensagem de {number}: '{text}'")
        
        # Processar comando ou gasto
        _processar_comando_ou_gasto(text, number)
        
        return "ok", 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}")
        return "ok", 200

def _validar_estrutura_webhook(data):
    """Valida estrutura do webhook"""
    if not data or "entry" not in data:
        return False
    
    entry = data.get("entry", [])
    if not entry or not entry[0].get("changes"):
        return False
    
    changes = entry[0].get("changes", [])
    if not changes or not changes[0].get("value", {}).get("messages"):
        return False
    
    return True

def _extrair_dados_mensagem(data):
    """Extrai dados da mensagem do webhook"""
    try:
        messages = data["entry"][0]["changes"][0]["value"]["messages"]
        if not messages:
            return None
        
        message = messages[0]
        text = message.get("text", {}).get("body", "").lower().strip()
        number = message.get("from")
        
        if not text or not number:
            return None
        
        return text, number
        
    except (KeyError, IndexError):
        return None

def _processar_comando_ou_gasto(text, number):
    """Processa comando ou registra gasto"""
    comando = extrair_comando(text)
    
    if comando:
        _processar_comando(comando, text, number)
    else:
        _processar_gasto(text, number)

def _processar_comando(comando, text, number):
    """Processa comandos específicos"""
    
    if comando == "saldo":
        total = sheets_service.calcular_saldo_mes()
        mes_atual = datetime.now().strftime("%m/%Y")
        whatsapp_service.enviar_saldo_mensal(number, total, mes_atual)
    
    elif comando == "hoje":
        gastos_hoje, total = sheets_service.obter_gastos_hoje()
        whatsapp_service.enviar_lista_gastos(number, gastos_hoje, "📅 Gastos de Hoje")
    
    elif comando == "exportar":
        link_planilha = f"https://docs.google.com/spreadsheets/d/{Config.SHEET_ID}/edit"
        whatsapp_service.enviar_mensagem_formatada(
            number,
            "📊 Planilha de Gastos",
            f"Acesse sua planilha completa:\n{link_planilha}",
            "Mantenha seus gastos sempre organizados!"
        )
    
    elif comando in ["deletar", "apagar"]:
        if sheets_service.deletar_ultimo_gasto():
            whatsapp_service.enviar_mensagem(number, "✅ Último gasto deletado com sucesso!")
        else:
            whatsapp_service.enviar_mensagem(number, "❌ Erro ao deletar gasto")
    
    elif comando in ["ajuda", "help", "comandos"]:
        whatsapp_service.enviar_ajuda(number)

def _processar_gasto(text, number):
    """Processa registro de gasto"""
    valor = extrair_valor_melhorado(text)
    
    if valor:
        descricao = limpar_descricao(text)
        categoria = categorizar_gasto(descricao)
        
        if sheets_service.adicionar_gasto(descricao, valor, categoria):
            # Sucesso
            whatsapp_service.enviar_mensagem_formatada(
                number,
                "✅ Gasto Registrado",
                f"{descricao} - R$ {valor:.2f}",
                f"📂 Categoria: {categoria.title()}"
            )
            
            logger.info(f"💰 GASTO REGISTRADO: {descricao} - R$ {valor:.2f} ({categoria})")
        else:
            # Erro ao salvar
            whatsapp_service.enviar_mensagem(number, "❌ Erro ao salvar gasto. Tente novamente.")
    else:
        # Valor não identificado
        whatsapp_service.enviar_erro_valor(number)

# Rotas de teste (apenas em desenvolvimento)
if Config.FLASK_ENV == 'development':
    
    @app.route("/test")
    def test():
        """Página de teste"""
        return {
            "status": "Bot funcionando!",
            "config": {
                "sheets_connected": sheets_service.is_connected(),
                "whatsapp_configured": bool(Config.WHATSAPP_TOKEN)
            }
        }
    
    @app.route("/test-send/<number>")
    def test_send(number):
        """Teste de envio de mensagem"""
        success = whatsapp_service.enviar_mensagem(
            number, 
            "🤖 Teste do bot! Se você recebeu esta mensagem, está funcionando! 🎉"
        )
        return {"success": success, "number": number}

def main():
    """Função principal"""
    logger.info("🚀 Iniciando Bot WhatsApp - Controle de Gastos")
    logger.info(f"📊 Google Sheets: {'✅ Conectado' if sheets_service.is_connected() else '❌ Desconectado'}")
    logger.info(f"📱 WhatsApp: {'✅ Configurado' if Config.WHATSAPP_TOKEN else '❌ Não configurado'}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.FLASK_DEBUG
    )

if __name__ == "__main__":
    main()