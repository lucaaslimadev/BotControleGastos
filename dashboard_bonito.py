#!/usr/bin/env python3
"""
Dashboard Bonito com Gráficos e Rankings
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
try:
    creds = Credentials.from_service_account_file('config/credentials.json', 
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_ID).sheet1
    print("✅ Dashboard conectado")
except Exception as e:
    print(f"❌ Erro: {e}")
    sheet = None

@app.route("/")
def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>💰 Dashboard - Controle de Gastos</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh; 
                color: #333;
            }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .header { 
                text-align: center; 
                color: white; 
                margin-bottom: 40px; 
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            .header h1 { 
                font-size: 3rem; 
                margin-bottom: 10px; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                background: linear-gradient(45deg, #fff, #f0f0f0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .stats-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                gap: 25px; 
                margin-bottom: 40px; 
            }
            .stat-card { 
                background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
                padding: 30px; 
                border-radius: 20px; 
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .stat-card:hover { 
                transform: translateY(-10px); 
                box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            }
            .stat-icon { font-size: 3rem; margin-bottom: 15px; }
            .stat-value { 
                font-size: 2.5rem; 
                font-weight: bold; 
                margin-bottom: 10px;
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .stat-label { color: #666; font-size: 1.1rem; font-weight: 500; }
            
            .charts-grid { 
                display: grid; 
                grid-template-columns: 1fr 1fr; 
                gap: 30px; 
                margin-bottom: 40px; 
            }
            .chart-card { 
                background: white; 
                padding: 30px; 
                border-radius: 20px; 
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .chart-title { 
                font-size: 1.5rem; 
                font-weight: bold; 
                margin-bottom: 20px; 
                color: #333;
                text-align: center;
            }
            
            .ranking-section { 
                display: grid; 
                grid-template-columns: 1fr 1fr; 
                gap: 30px; 
                margin-bottom: 40px; 
            }
            .ranking-card { 
                background: white; 
                padding: 30px; 
                border-radius: 20px; 
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            }
            .ranking-title { 
                font-size: 1.5rem; 
                font-weight: bold; 
                margin-bottom: 25px; 
                color: #333;
                text-align: center;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }
            .ranking-item { 
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                padding: 15px 0; 
                border-bottom: 1px solid #eee;
                transition: background 0.3s ease;
            }
            .ranking-item:hover { background: #f8f9fa; }
            .ranking-item:last-child { border-bottom: none; }
            .ranking-position { 
                font-weight: bold; 
                font-size: 1.2rem;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }
            .pos-1 { background: linear-gradient(45deg, #FFD700, #FFA500); }
            .pos-2 { background: linear-gradient(45deg, #C0C0C0, #A9A9A9); }
            .pos-3 { background: linear-gradient(45deg, #CD7F32, #B8860B); }
            .pos-other { background: linear-gradient(45deg, #667eea, #764ba2); }
            .ranking-name { 
                flex: 1; 
                margin-left: 15px; 
                font-weight: 500;
                font-size: 1.1rem;
            }
            .ranking-value { 
                font-weight: bold; 
                color: #e74c3c;
                font-size: 1.2rem;
            }
            
            .actions { 
                text-align: center; 
                margin-top: 40px; 
            }
            .btn { 
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white; 
                padding: 15px 30px; 
                border: none;
                border-radius: 50px; 
                text-decoration: none; 
                margin: 10px; 
                font-size: 1.1rem;
                font-weight: 500;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            }
            .btn:hover { 
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            }
            
            .loading { 
                text-align: center; 
                color: white; 
                font-size: 1.5rem;
                padding: 50px;
            }
            
            @media (max-width: 768px) {
                .charts-grid, .ranking-section { grid-template-columns: 1fr; }
                .header h1 { font-size: 2rem; }
                .stat-value { font-size: 2rem; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💰 Dashboard Controle de Gastos</h1>
                <p>Análise completa dos seus gastos com gráficos e rankings</p>
            </div>
            
            <div id="loading" class="loading">
                <div>📊 Carregando dados...</div>
                <div style="margin-top: 10px;">⏳ Analisando gastos e gerando gráficos</div>
            </div>
            
            <div id="dashboard" style="display: none;">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">💸</div>
                        <div class="stat-value" id="gastoMes">R$ 0,00</div>
                        <div class="stat-label">Gasto este mês</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📈</div>
                        <div class="stat-value" id="totalGeral">R$ 0,00</div>
                        <div class="stat-label">Total geral</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📝</div>
                        <div class="stat-value" id="totalGastos">0</div>
                        <div class="stat-label">Total de gastos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📊</div>
                        <div class="stat-value" id="mediaGasto">R$ 0,00</div>
                        <div class="stat-label">Média por gasto</div>
                    </div>
                </div>
                
                <div class="charts-grid">
                    <div class="chart-card">
                        <div class="chart-title">📊 Gastos por Categoria</div>
                        <canvas id="categoryChart"></canvas>
                    </div>
                    <div class="chart-card">
                        <div class="chart-title">📅 Evolução Últimos 7 Dias</div>
                        <canvas id="weekChart"></canvas>
                    </div>
                </div>
                
                <div class="ranking-section">
                    <div class="ranking-card">
                        <div class="ranking-title">🏆 Ranking Categorias</div>
                        <div id="rankingCategorias"></div>
                    </div>
                    <div class="ranking-card">
                        <div class="ranking-title">💰 Maiores Gastos</div>
                        <div id="maioresGastos"></div>
                    </div>
                </div>
                
                <div class="actions">
                    <a href="https://t.me/Lucas_gastos_bot" class="btn">📱 Abrir Bot</a>
                    <a href="#" id="planilhaLink" class="btn">📊 Ver Planilha</a>
                    <button onclick="loadData()" class="btn">🔄 Atualizar</button>
                </div>
            </div>
        </div>
        
        <script>
            async function loadData() {
                try {
                    document.getElementById('loading').style.display = 'block';
                    document.getElementById('dashboard').style.display = 'none';
                    
                    const response = await fetch('/api/dashboard-data');
                    const data = await response.json();
                    
                    // Atualizar estatísticas
                    document.getElementById('gastoMes').textContent = `R$ ${data.gastoMes.toFixed(2)}`;
                    document.getElementById('totalGeral').textContent = `R$ ${data.totalGeral.toFixed(2)}`;
                    document.getElementById('totalGastos').textContent = data.totalGastos;
                    document.getElementById('mediaGasto').textContent = `R$ ${data.mediaGasto.toFixed(2)}`;
                    document.getElementById('planilhaLink').href = data.planilhaLink;
                    
                    // Gráfico de categorias
                    const ctx1 = document.getElementById('categoryChart').getContext('2d');
                    new Chart(ctx1, {
                        type: 'doughnut',
                        data: {
                            labels: Object.keys(data.categorias),
                            datasets: [{
                                data: Object.values(data.categorias),
                                backgroundColor: [
                                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                                ],
                                borderWidth: 3,
                                borderColor: '#fff'
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: { position: 'bottom', labels: { padding: 20, font: { size: 12 } } },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            return context.label + ': R$ ' + context.parsed.toFixed(2);
                                        }
                                    }
                                }
                            }
                        }
                    });
                    
                    // Gráfico semanal
                    const ctx2 = document.getElementById('weekChart').getContext('2d');
                    new Chart(ctx2, {
                        type: 'line',
                        data: {
                            labels: data.ultimosDias.labels,
                            datasets: [{
                                label: 'Gastos Diários',
                                data: data.ultimosDias.values,
                                borderColor: '#667eea',
                                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                tension: 0.4,
                                fill: true,
                                borderWidth: 3,
                                pointBackgroundColor: '#667eea',
                                pointBorderColor: '#fff',
                                pointBorderWidth: 2,
                                pointRadius: 6
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: { 
                                    beginAtZero: true,
                                    ticks: {
                                        callback: function(value) {
                                            return 'R$ ' + value.toFixed(0);
                                        }
                                    }
                                }
                            },
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            return 'R$ ' + context.parsed.y.toFixed(2);
                                        }
                                    }
                                }
                            }
                        }
                    });
                    
                    // Ranking de categorias
                    const rankingCat = document.getElementById('rankingCategorias');
                    rankingCat.innerHTML = Object.entries(data.categorias)
                        .sort(([,a], [,b]) => b - a)
                        .slice(0, 5)
                        .map(([cat, valor], index) => {
                            const posClass = index === 0 ? 'pos-1' : index === 1 ? 'pos-2' : index === 2 ? 'pos-3' : 'pos-other';
                            return `
                                <div class="ranking-item">
                                    <div class="ranking-position ${posClass}">${index + 1}</div>
                                    <div class="ranking-name">${cat}</div>
                                    <div class="ranking-value">R$ ${valor.toFixed(2)}</div>
                                </div>
                            `;
                        }).join('');
                    
                    // Maiores gastos
                    const maioresGastos = document.getElementById('maioresGastos');
                    maioresGastos.innerHTML = data.maioresGastos
                        .map((gasto, index) => {
                            const posClass = index === 0 ? 'pos-1' : index === 1 ? 'pos-2' : index === 2 ? 'pos-3' : 'pos-other';
                            return `
                                <div class="ranking-item">
                                    <div class="ranking-position ${posClass}">${index + 1}</div>
                                    <div class="ranking-name">${gasto.descricao}</div>
                                    <div class="ranking-value">R$ ${gasto.valor}</div>
                                </div>
                            `;
                        }).join('');
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                    
                } catch (error) {
                    document.getElementById('loading').innerHTML = '<div style="color: #ff6b6b;">❌ Erro ao carregar dados</div>';
                }
            }
            
            // Carregar dados ao iniciar
            loadData();
            
            // Atualizar automaticamente a cada 30 segundos
            setInterval(loadData, 30000);
        </script>
    </body>
    </html>
    """

@app.route("/api/dashboard-data")
def dashboard_data():
    """API com dados completos do dashboard"""
    if not sheet:
        return jsonify({"error": "Planilha não conectada"}), 500
    
    try:
        gastos = sheet.get_all_records()
        
        # Estatísticas básicas
        total_geral = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos if g.get('Valor'))
        
        # Saldo do mês atual
        mes_atual = datetime.now().strftime("%m/%Y")
        gastos_mes = [g for g in gastos if mes_atual in str(g.get('Data', ''))]
        total_mes = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_mes)
        
        # Média por gasto
        media_gasto = total_geral / len(gastos) if gastos else 0
        
        # Gastos por categoria
        categorias = {}
        for gasto in gastos:
            cat = gasto.get('Categoria', 'outros').title()
            valor_str = str(gasto.get('Valor', '0')).replace(',', '.')
            try:
                valor = float(valor_str)
                categorias[cat] = categorias.get(cat, 0) + valor
            except:
                continue
        
        # Últimos 7 dias
        hoje = datetime.now()
        ultimos_dias = {(hoje - timedelta(days=i)).strftime('%d/%m'): 0 for i in range(6, -1, -1)}
        
        for gasto in gastos:
            data_str = gasto.get('Data', '')
            if '/' in data_str:
                try:
                    data_gasto = datetime.strptime(data_str, '%d/%m/%Y')
                    if (hoje - data_gasto).days <= 7:
                        dia_key = data_gasto.strftime('%d/%m')
                        if dia_key in ultimos_dias:
                            valor = float(str(gasto.get('Valor', '0')).replace(',', '.'))
                            ultimos_dias[dia_key] += valor
                except:
                    continue
        
        # Maiores gastos individuais
        maiores_gastos = []
        for gasto in gastos:
            try:
                valor = float(str(gasto.get('Valor', '0')).replace(',', '.'))
                maiores_gastos.append({
                    'descricao': gasto.get('Descrição', 'N/A'),
                    'valor': gasto.get('Valor', '0'),
                    'data': gasto.get('Data', 'N/A'),
                    'valor_num': valor
                })
            except:
                continue
        
        maiores_gastos.sort(key=lambda x: x['valor_num'], reverse=True)
        maiores_gastos = maiores_gastos[:5]
        
        return jsonify({
            'gastoMes': total_mes,
            'totalGeral': total_geral,
            'totalGastos': len(gastos),
            'mediaGasto': media_gasto,
            'categorias': categorias,
            'planilhaLink': f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
            'ultimosDias': {
                'labels': list(ultimos_dias.keys()),
                'values': list(ultimos_dias.values())
            },
            'maioresGastos': maiores_gastos
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)