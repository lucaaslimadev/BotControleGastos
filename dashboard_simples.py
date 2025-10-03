#!/usr/bin/env python3
"""
Dashboard Simples e Funcional
"""
from flask import Flask, jsonify
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Conectar Google Sheets
SHEET_ID = os.getenv('SHEET_ID')
CREDENTIALS_FILE = 'config/credentials.json'

try:
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE, 
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_ID).sheet1
    print("✅ Dashboard conectado ao Google Sheets")
except Exception as e:
    print(f"❌ Erro Dashboard: {e}")
    sheet = None

@app.route("/")
def home():
    """Dashboard principal"""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>💰 Controle de Gastos</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; color: white; margin-bottom: 30px; }
            .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); text-align: center; }
            .card-title { color: #666; margin-bottom: 10px; }
            .card-value { font-size: 2rem; font-weight: bold; }
            .card-mes { color: #e74c3c; }
            .card-total { color: #3498db; }
            .card-count { color: #27ae60; }
            .chart-container { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin-bottom: 20px; }
            .recent { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
            .expense-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
            .btn { background: #3498db; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; margin: 10px; }
            .loading { text-align: center; color: white; font-size: 1.2rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💰 Controle de Gastos</h1>
                <p>Dashboard em tempo real</p>
            </div>
            
            <div id="loading" class="loading">📊 Carregando dados...</div>
            <div id="dashboard" style="display: none;">
                <div class="cards">
                    <div class="card">
                        <div class="card-title">💸 Gasto este mês</div>
                        <div class="card-value card-mes" id="gastoMes">R$ 0,00</div>
                    </div>
                    <div class="card">
                        <div class="card-title">📈 Total geral</div>
                        <div class="card-value card-total" id="totalGeral">R$ 0,00</div>
                    </div>
                    <div class="card">
                        <div class="card-title">📝 Quantidade</div>
                        <div class="card-value card-count" id="totalGastos">0</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>📊 Gastos por Categoria</h3>
                    <canvas id="categoryChart"></canvas>
                </div>
                
                <div class="recent">
                    <h3>📋 Últimos Gastos</h3>
                    <div id="recentExpenses"></div>
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="https://t.me/Lucas_gastos_bot" class="btn">📱 Bot Telegram</a>
                        <a href="#" id="planilhaLink" class="btn">📊 Ver Planilha</a>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function loadData() {
                try {
                    const response = await fetch('/api/data');
                    const data = await response.json();
                    
                    // Atualizar cards
                    document.getElementById('gastoMes').textContent = `R$ ${data.gastoMes.toFixed(2)}`;
                    document.getElementById('totalGeral').textContent = `R$ ${data.totalGeral.toFixed(2)}`;
                    document.getElementById('totalGastos').textContent = data.totalGastos;
                    
                    // Link da planilha
                    document.getElementById('planilhaLink').href = data.planilhaLink;
                    
                    // Gráfico
                    const ctx = document.getElementById('categoryChart').getContext('2d');
                    new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: Object.keys(data.categorias),
                            datasets: [{
                                data: Object.values(data.categorias),
                                backgroundColor: ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
                            }]
                        },
                        options: { responsive: true }
                    });
                    
                    // Últimos gastos
                    document.getElementById('recentExpenses').innerHTML = data.ultimosGastos.map(gasto => `
                        <div class="expense-item">
                            <div><strong>${gasto.descricao}</strong><br><small>${gasto.data} • ${gasto.categoria}</small></div>
                            <div style="font-weight: bold; color: #e74c3c;">R$ ${gasto.valor}</div>
                        </div>
                    `).join('');
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                    
                } catch (error) {
                    document.getElementById('loading').textContent = '❌ Erro ao carregar dados';
                }
            }
            
            loadData();
            setInterval(loadData, 30000);
        </script>
    </body>
    </html>
    """

@app.route("/api/data")
def api_data():
    """API de dados"""
    if not sheet:
        return jsonify({"error": "Planilha não conectada"}), 500
    
    try:
        gastos = sheet.get_all_records()
        
        # Estatísticas
        total_geral = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos if g.get('Valor'))
        
        # Saldo do mês
        mes_atual = datetime.now().strftime("%m/%Y")
        total_mes = sum(float(str(g.get('Valor', '0')).replace(',', '.')) 
                       for g in gastos if mes_atual in str(g.get('Data', '')))
        
        # Categorias
        categorias = {}
        for gasto in gastos:
            cat = gasto.get('Categoria', 'outros').title()
            valor_str = str(gasto.get('Valor', '0')).replace(',', '.')
            try:
                valor = float(valor_str)
                categorias[cat] = categorias.get(cat, 0) + valor
            except:
                continue
        
        # Últimos gastos
        ultimos_gastos = []
        for gasto in gastos[-10:]:
            ultimos_gastos.append({
                'descricao': gasto.get('Descrição', 'N/A'),
                'valor': gasto.get('Valor', '0'),
                'data': gasto.get('Data', 'N/A'),
                'categoria': gasto.get('Categoria', 'outros').title()
            })
        
        return jsonify({
            'gastoMes': total_mes,
            'totalGeral': total_geral,
            'totalGastos': len(gastos),
            'categorias': categorias,
            'planilhaLink': f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
            'ultimosGastos': list(reversed(ultimos_gastos))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)