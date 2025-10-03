#!/usr/bin/env python3
"""
Dashboard Web - Controle de Gastos Telegram
"""
from flask import Flask, render_template
import logging
from sheets_telegram import SheetsService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Inicializar serviços
sheets_service = SheetsService()

@app.route("/")
def home():
    """Página inicial"""
    return """
    <html>
    <head><title>Bot Telegram - Controle de Gastos</title></head>
    <body style="font-family: Arial; padding: 20px; background: #f5f5f5;">
        <div style="max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #2c3e50; text-align: center;">🤖 Bot Telegram - Controle de Gastos</h1>
            
            <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #27ae60; margin: 0;">✅ Sistema Funcionando</h3>
                <p style="margin: 5px 0 0 0;">Bot Telegram configurado e operacional</p>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                <div style="text-align: center;">
                    <h3>📊 Dashboard</h3>
                    <a href="/dashboard" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Ver Estatísticas</a>
                </div>
                
                <div style="text-align: center;">
                    <h3>📱 Telegram</h3>
                    <a href="https://t.me/Lucas_gastos_bot" target="_blank" style="background: #0088cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Abrir Bot</a>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>📝 Como Usar:</h3>
                <ul>
                    <li><strong>Registrar gastos:</strong> mercado 50, uber 25.50, R$ 100 farmácia</li>
                    <li><strong>Ver saldo:</strong> /saldo</li>
                    <li><strong>Ajuda:</strong> /ajuda</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/dashboard")
def dashboard():
    """Dashboard com estatísticas"""
    try:
        if not sheets_service.is_connected():
            return """
            <html>
            <head><title>Dashboard - Erro</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>❌ Google Sheets não conectado</h1>
                <p>Verifique as credenciais e tente novamente.</p>
                <a href="/">← Voltar</a>
            </body>
            </html>
            """, 500
        
        # Obter dados
        gastos = sheets_service.sheet.get_all_records() if sheets_service.sheet else []
        total_mes = sheets_service.calcular_saldo_mes()
        
        # Calcular estatísticas
        total_geral = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos if g.get('Valor'))
        total_gastos = len(gastos)
        
        # Gastos por categoria
        categorias = {}
        for gasto in gastos:
            cat = gasto.get('Categoria', 'outros')
            valor_str = str(gasto.get('Valor', '0')).replace(',', '.')
            try:
                valor = float(valor_str)
                categorias[cat] = categorias.get(cat, 0) + valor
            except ValueError:
                continue
        
        # HTML do dashboard
        html = f"""
        <html>
        <head>
            <title>Dashboard - Controle de Gastos</title>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial; padding: 20px; background: #f5f5f5;">
            <div style="max-width: 1200px; margin: 0 auto;">
                <h1 style="color: #2c3e50; text-align: center;">📊 Dashboard - Controle de Gastos</h1>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0;">
                    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center;">
                        <h3 style="color: #e74c3c; margin: 0;">💰 Gasto este mês</h3>
                        <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #e74c3c;">R$ {total_mes:.2f}</p>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center;">
                        <h3 style="color: #3498db; margin: 0;">📈 Total geral</h3>
                        <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #3498db;">R$ {total_geral:.2f}</p>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center;">
                        <h3 style="color: #27ae60; margin: 0;">📝 Total de gastos</h3>
                        <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #27ae60;">{total_gastos}</p>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <h3 style="color: #2c3e50;">📂 Gastos por Categoria</h3>
                        {''.join([f'<p><strong>{cat.title()}:</strong> R$ {valor:.2f}</p>' for cat, valor in sorted(categorias.items(), key=lambda x: x[1], reverse=True)])}
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <h3 style="color: #2c3e50;">📋 Últimos Gastos</h3>
                        {''.join([f'<p><small>{g.get("Data", "N/A")}</small><br><strong>{g.get("Descrição", "N/A")}</strong> - R$ {g.get("Valor", "0")}</p>' for g in gastos[-5:]])}
                    </div>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="https://docs.google.com/spreadsheets/d/{sheets_service.sheet.id}/edit" target="_blank" 
                       style="background: #27ae60; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 0 10px;">
                       📊 Abrir Planilha Completa
                    </a>
                    <a href="/" style="background: #95a5a6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 0 10px;">
                       ← Voltar
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        return f"""
        <html>
        <head><title>Dashboard - Erro</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>❌ Erro no Dashboard</h1>
            <p>Erro: {str(e)}</p>
            <a href="/">← Voltar</a>
        </body>
        </html>
        """, 500

@app.route("/health")
def health():
    """Health check"""
    return {
        "status": "ok",
        "sheets_connected": sheets_service.is_connected(),
        "timestamp": "2025-10-03T09:00:00Z"
    }

def main():
    """Executar dashboard"""
    logger.info("🚀 Iniciando Dashboard Web")
    logger.info(f"📊 Google Sheets: {'✅ Conectado' if sheets_service.is_connected() else '❌ Desconectado'}")
    
    app.run(host='0.0.0.0', port=8000, debug=True)

if __name__ == "__main__":
    main()