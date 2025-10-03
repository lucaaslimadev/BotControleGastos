#!/usr/bin/env python3
"""
Dashboard Melhorado - Controle de Gastos
"""
from flask import Flask, render_template, jsonify
import json
from datetime import datetime, timedelta
from sheets_telegram import SheetsService

app = Flask(__name__)
sheets_service = SheetsService()

@app.route("/")
def home():
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
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; color: white; margin-bottom: 30px; }
            .header h1 { font-size: 2.5rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); transition: transform 0.3s ease; }
            .card:hover { transform: translateY(-5px); }
            .card-title { font-size: 1.1rem; color: #666; margin-bottom: 10px; }
            .card-value { font-size: 2rem; font-weight: bold; margin-bottom: 5px; }
            .card-mes { color: #e74c3c; }
            .card-total { color: #3498db; }
            .card-count { color: #27ae60; }
            .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
            .chart-container { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
            .recent-expenses { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
            .expense-item { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #eee; }
            .expense-item:last-child { border-bottom: none; }
            .expense-desc { font-weight: 500; }
            .expense-date { color: #666; font-size: 0.9rem; }
            .expense-value { font-weight: bold; color: #e74c3c; }
            .btn { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 8px; text-decoration: none; display: inline-block; transition: background 0.3s; }
            .btn:hover { background: #2980b9; }
            .loading { text-align: center; color: white; font-size: 1.2rem; }
            @media (max-width: 768px) {
                .charts { grid-template-columns: 1fr; }
                .header h1 { font-size: 2rem; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💰 Controle de Gastos</h1>
                <p>Dashboard inteligente para seus gastos</p>
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
                
                <div class="charts">
                    <div class="chart-container">
                        <h3>📊 Gastos por Categoria</h3>
                        <canvas id="categoryChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>📅 Últimos 7 dias</h3>
                        <canvas id="weekChart"></canvas>
                    </div>
                </div>
                
                <div class="recent-expenses">
                    <h3>📋 Últimos Gastos</h3>
                    <div id="recentExpenses"></div>
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="https://t.me/Lucas_gastos_bot" class="btn">📱 Abrir Bot Telegram</a>
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
                    
                    // Gráfico de categorias
                    const ctx1 = document.getElementById('categoryChart').getContext('2d');
                    new Chart(ctx1, {
                        type: 'doughnut',
                        data: {
                            labels: Object.keys(data.categorias),
                            datasets: [{
                                data: Object.values(data.categorias),
                                backgroundColor: ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e']
                            }]
                        },
                        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
                    });
                    
                    // Gráfico semanal
                    const ctx2 = document.getElementById('weekChart').getContext('2d');
                    new Chart(ctx2, {
                        type: 'line',
                        data: {
                            labels: data.ultimosDias.labels,
                            datasets: [{
                                label: 'Gastos',
                                data: data.ultimosDias.values,
                                borderColor: '#3498db',
                                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: { responsive: true, scales: { y: { beginAtZero: true } } }
                    });
                    
                    // Últimos gastos
                    const recentDiv = document.getElementById('recentExpenses');
                    recentDiv.innerHTML = data.ultimosGastos.map(gasto => `
                        <div class="expense-item">
                            <div>
                                <div class="expense-desc">${gasto.descricao}</div>
                                <div class="expense-date">${gasto.data} • ${gasto.categoria}</div>
                            </div>
                            <div class="expense-value">R$ ${gasto.valor}</div>
                        </div>
                    `).join('');
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                    
                } catch (error) {
                    document.getElementById('loading').textContent = '❌ Erro ao carregar dados';
                }
            }
            
            loadData();
            setInterval(loadData, 30000); // Atualiza a cada 30 segundos
        </script>
    </body>
    </html>
    """

@app.route("/api/data")
def api_data():
    """API para dados do dashboard"""
    try:
        gastos = sheets_service.sheet.get_all_records() if sheets_service.sheet else []
        
        # Calcular estatísticas
        total_geral = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos if g.get('Valor'))
        total_mes = sheets_service.calcular_saldo_mes()
        
        # Gastos por categoria
        categorias = {}
        for gasto in gastos:
            cat = gasto.get('Categoria', 'outros').title()
            valor_str = str(gasto.get('Valor', '0')).replace(',', '.')
            try:
                valor = float(valor_str)
                categorias[cat] = categorias.get(cat, 0) + valor
            except ValueError:
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
                except ValueError:
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
            'ultimosDias': {
                'labels': list(ultimos_dias.keys()),
                'values': list(ultimos_dias.values())
            },
            'ultimosGastos': list(reversed(ultimos_gastos))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)