#!/usr/bin/env python3
"""
Dashboard Completo - Controle Financeiro Avançado
"""
from flask import Flask, jsonify, request
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Conectar Google Sheets - FORÇAR LEITURA DAS VARIÁVEIS
SHEET_ID = os.environ.get('SHEET_ID')  # Usar environ em vez de getenv
PORT = int(os.environ.get('PORT', 8000))
GOOGLE_CREDENTIALS = os.environ.get('GOOGLE_CREDENTIALS')

# Debug das variáveis
print(f"🔍 SHEET_ID: {SHEET_ID[:10] + '...' if SHEET_ID else 'NÃO DEFINIDO'}")
print(f"🔍 PORT: {PORT}")
print(f"🔍 GOOGLE_CREDENTIALS: {'✅ Definido (' + str(len(GOOGLE_CREDENTIALS)) + ' chars)' if GOOGLE_CREDENTIALS else '❌ Não definido'}")
print("🚀 Forçando deploy...")

try:
    if not SHEET_ID:
        raise ValueError('SHEET_ID não configurado no Railway')
    
    if not GOOGLE_CREDENTIALS:
        raise ValueError('GOOGLE_CREDENTIALS não configurado no Railway')
    
    print("🌐 Conectando com Google Sheets...")
    print(f"📊 Credenciais: {len(GOOGLE_CREDENTIALS)} caracteres")
    print(f"📊 SHEET_ID COMPLETO: {SHEET_ID}")
    
    creds_info = json.loads(GOOGLE_CREDENTIALS)
    print(f"🔑 Service Account Email: {creds_info.get('client_email', 'N/A')}")
    
    creds = Credentials.from_service_account_info(creds_info,
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    
    gc = gspread.authorize(creds)
    print(f"🔍 Tentando abrir planilha: {SHEET_ID}")
    sheet = gc.open_by_key(SHEET_ID).sheet1
    
    # Testar conexão
    test_records = sheet.get_all_records()
    print(f"✅ Dashboard conectado! {len(test_records)} registros encontrados")
    
except Exception as e:
    print(f"❌ ERRO CRÍTICO: {e}")
    print(f"❌ Variáveis: SHEET_ID={bool(SHEET_ID)}, CREDENTIALS={bool(GOOGLE_CREDENTIALS)}")
    print("❌ DEPLOY ATIVO - VERIFICANDO VARIÁVEIS")
    sheet = None

# Configurações (simulando banco de dados)
CONFIG_FILE = 'dashboard_config.json'

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"meta_mensal": 2000, "alertas": True}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

@app.route("/health")
def health_check():
    return {"status": "ok", "service": "running"}

@app.route("/debug")
def debug_vars():
    """Debug das variáveis de ambiente"""
    return {
        "SHEET_ID": SHEET_ID[:10] + "..." if SHEET_ID else "NÃO DEFINIDO",
        "GOOGLE_CREDENTIALS": "DEFINIDO" if os.getenv('GOOGLE_CREDENTIALS') else "NÃO DEFINIDO",
        "TELEGRAM_TOKEN": "DEFINIDO" if os.getenv('TELEGRAM_TOKEN') else "NÃO DEFINIDO",
        "PORT": PORT,
        "sheet_connected": sheet is not None
    }

@app.route("/")
def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>💰 Dashboard Financeiro Completo</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh; 
                color: #333;
            }
            .container { max-width: 1600px; margin: 0 auto; padding: 20px; }
            .header { 
                text-align: center; 
                color: white; 
                margin-bottom: 30px; 
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            .header h1 { 
                font-size: 2.5rem; 
                margin-bottom: 10px; 
                background: linear-gradient(45deg, #fff, #f0f0f0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .controls { 
                display: flex; 
                justify-content: center; 
                gap: 15px; 
                margin-bottom: 30px; 
                flex-wrap: wrap;
            }
            .control-item { 
                background: white; 
                padding: 10px 20px; 
                border-radius: 25px; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .control-item select, .control-item input { 
                border: none; 
                background: transparent; 
                font-size: 1rem; 
                outline: none;
            }
            
            .stats-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
                margin-bottom: 30px; 
            }
            .stat-card { 
                background: white;
                padding: 25px; 
                border-radius: 15px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            .stat-card:hover { transform: translateY(-5px); }
            .stat-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(45deg, #667eea, #764ba2);
            }
            .stat-icon { font-size: 2.5rem; margin-bottom: 10px; }
            .stat-value { 
                font-size: 2rem; 
                font-weight: bold; 
                margin-bottom: 5px;
                color: #333;
            }
            .stat-label { color: #666; font-size: 0.9rem; }
            .stat-change { 
                font-size: 0.8rem; 
                margin-top: 5px;
                padding: 3px 8px;
                border-radius: 10px;
            }
            .positive { background: #d4edda; color: #155724; }
            .negative { background: #f8d7da; color: #721c24; }
            
            .progress-container { 
                background: white; 
                padding: 25px; 
                border-radius: 15px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .progress-title { 
                font-size: 1.3rem; 
                font-weight: bold; 
                margin-bottom: 15px;
                text-align: center;
            }
            .progress-bar { 
                width: 100%; 
                height: 25px; 
                background: #e9ecef; 
                border-radius: 15px; 
                overflow: hidden;
                position: relative;
            }
            .progress-fill { 
                height: 100%; 
                background: linear-gradient(45deg, #28a745, #20c997); 
                border-radius: 15px;
                transition: width 0.5s ease;
                position: relative;
            }
            .progress-fill.warning { background: linear-gradient(45deg, #ffc107, #fd7e14); }
            .progress-fill.danger { background: linear-gradient(45deg, #dc3545, #e83e8c); }
            .progress-text { 
                position: absolute; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%);
                font-weight: bold;
                color: white;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            }
            
            .charts-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
                gap: 25px; 
                margin-bottom: 30px; 
            }
            .chart-card { 
                background: white; 
                padding: 25px; 
                border-radius: 15px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }
            .chart-title { 
                font-size: 1.3rem; 
                font-weight: bold; 
                margin-bottom: 20px; 
                text-align: center;
                color: #333;
            }
            
            .insights-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; 
                margin-bottom: 30px; 
            }
            .insight-card { 
                background: white; 
                padding: 20px; 
                border-radius: 15px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }
            .insight-title { 
                font-size: 1.1rem; 
                font-weight: bold; 
                margin-bottom: 10px;
                color: #333;
            }
            .insight-content { 
                color: #666; 
                line-height: 1.5;
            }
            
            .actions { 
                text-align: center; 
                margin-top: 30px; 
            }
            .btn { 
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white; 
                padding: 12px 25px; 
                border: none;
                border-radius: 25px; 
                text-decoration: none; 
                margin: 5px; 
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .btn:hover { 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            }
            
            .loading { 
                text-align: center; 
                color: white; 
                font-size: 1.2rem;
                padding: 50px;
            }
            
            @media (max-width: 768px) {
                .charts-grid { grid-template-columns: 1fr; }
                .header h1 { font-size: 2rem; }
                .controls { flex-direction: column; align-items: center; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💰 Dashboard Financeiro Completo</h1>
                <p>Controle total dos seus gastos com análises avançadas</p>
                <div style="background: rgba(255,255,255,0.2); padding: 10px; border-radius: 10px; margin-top: 10px; font-size: 0.9rem;">
                    <div>🔍 Debug Info:</div>
                    <div>Sheet Connected: """ + str(sheet is not None) + """</div>
                    <div>Sheet ID: """ + (SHEET_ID[:10] + "..." if SHEET_ID else "NOT FOUND") + """</div>
                    <div>Credentials: """ + ("OK" if os.getenv('GOOGLE_CREDENTIALS') else "NOT FOUND") + """</div>
                </div>
            </div>
            
            <div class="controls">
                <div class="control-item">
                    <label>📅 Período: </label>
                    <select id="periodoSelect" onchange="loadData()">
                        <option value="atual">Mês Atual</option>
                        <option value="anterior">Mês Anterior</option>
                        <option value="ano">Ano Atual</option>
                    </select>
                </div>
                <div class="control-item">
                    <label>🎯 Meta Mensal: R$ </label>
                    <input type="number" id="metaInput" value="2000" onchange="updateMeta()" style="width: 80px;">
                </div>
                <div class="control-item">
                    <button class="btn" onclick="exportarRelatorio()">📄 Exportar PDF</button>
                </div>
            </div>
            
            <div id="loading" class="loading">📊 Carregando análises financeiras...</div>
            
            <div id="dashboard" style="display: none;">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">💸</div>
                        <div class="stat-value" id="gastoAtual">R$ 0,00</div>
                        <div class="stat-label">Gasto Atual</div>
                        <div class="stat-change" id="changeAtual"></div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🎯</div>
                        <div class="stat-value" id="restanteMeta">R$ 0,00</div>
                        <div class="stat-label">Restante da Meta</div>
                        <div class="stat-change" id="changeRestante"></div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📅</div>
                        <div class="stat-value" id="ultimos7Dias">R$ 0,00</div>
                        <div class="stat-label">Últimos 7 Dias</div>
                        <div class="stat-change" id="change7Dias"></div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🏆</div>
                        <div class="stat-value" id="maiorGasto">R$ 0,00</div>
                        <div class="stat-label">Maior Gasto Individual</div>
                        <div class="stat-change" id="changeMaior"></div>
                    </div>
                </div>
                
                <div class="progress-container">
                    <div class="progress-title">🎯 Progresso da Meta Mensal</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill">
                            <div class="progress-text" id="progressText">0%</div>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 10px; color: #666;" id="progressInfo"></div>
                </div>
                
                <div class="charts-grid">
                    <div class="chart-card">
                        <div class="chart-title">📊 Gastos por Categoria</div>
                        <canvas id="categoryChart"></canvas>
                    </div>
                    <div class="chart-card">
                        <div class="chart-title">📅 Gastos por Semana do Mês</div>
                        <canvas id="weeklyChart"></canvas>
                    </div>
                    <div class="chart-card">
                        <div class="chart-title">📅 Gastos por Dia da Semana</div>
                        <canvas id="weekdayChart"></canvas>
                    </div>
                    <div class="chart-card">
                        <div class="chart-title">🏆 Top 5 Maiores Gastos</div>
                        <canvas id="topGastosChart"></canvas>
                    </div>
                </div>
                
                <div class="insights-grid">
                    <div class="insight-card">
                        <div class="insight-title">🏆 Categoria que Mais Cresceu</div>
                        <div class="insight-content" id="categoriaCresceu"></div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">💎 Dia Mais Caro</div>
                        <div class="insight-content" id="diaCaro"></div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">💡 Dica de Economia</div>
                        <div class="insight-content" id="dicaEconomia"></div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-title">📊 Padrão de Gastos</div>
                        <div class="insight-content" id="padraoGastos"></div>
                    </div>
                </div>
                
                <div class="actions">
                    <a href="https://t.me/Lucas_gastos_bot" class="btn">📱 Bot Telegram</a>
                    <a href="#" id="planilhaLink" class="btn">📊 Ver Planilha</a>
                    <button onclick="loadData()" class="btn">🔄 Atualizar</button>
                    <button onclick="backupDados()" class="btn">💾 Backup</button>
                </div>
            </div>
        </div>
        
        <script>
            let currentData = {};
            
            async function loadData() {
                try {
                    document.getElementById('loading').style.display = 'block';
                    document.getElementById('dashboard').style.display = 'none';
                    
                    const periodo = document.getElementById('periodoSelect').value;
                    const response = await fetch(`/api/complete-data?periodo=${periodo}`);
                    currentData = await response.json();
                    
                    updateStats();
                    updateProgress();
                    updateCharts();
                    updateInsights();
                    
                    document.getElementById('planilhaLink').href = currentData.planilhaLink;
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                    
                } catch (error) {
                    document.getElementById('loading').innerHTML = '<div style="color: #ff6b6b;">❌ Erro ao carregar dados</div>';
                }
            }
            
            function updateStats() {
                document.getElementById('gastoAtual').textContent = `R$ ${currentData.gastoAtual.toFixed(2)}`;
                document.getElementById('restanteMeta').textContent = `R$ ${currentData.restanteMeta.toFixed(2)}`;
                document.getElementById('ultimos7Dias').textContent = `R$ ${currentData.ultimos7Dias.toFixed(2)}`;
                document.getElementById('maiorGasto').textContent = `R$ ${currentData.maiorGasto.toFixed(2)}`;
                
                // Mudanças percentuais
                updateChange('changeAtual', currentData.changeAtual);
                updateChange('changeRestante', currentData.changeRestante);
                updateChange('change7Dias', currentData.change7Dias);
                updateChange('changeMaior', currentData.changeMaior);
            }
            
            function updateChange(elementId, change) {
                const element = document.getElementById(elementId);
                const isPositive = change >= 0;
                element.textContent = `${isPositive ? '+' : ''}${change.toFixed(1)}%`;
                element.className = `stat-change ${isPositive ? 'positive' : 'negative'}`;
            }
            
            function updateProgress() {
                const meta = parseFloat(document.getElementById('metaInput').value);
                const gasto = currentData.gastoAtual;
                const percentage = Math.min((gasto / meta) * 100, 100);
                
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');
                const progressInfo = document.getElementById('progressInfo');
                
                progressFill.style.width = `${percentage}%`;
                progressText.textContent = `${percentage.toFixed(1)}%`;
                
                if (percentage < 70) {
                    progressFill.className = 'progress-fill';
                } else if (percentage < 90) {
                    progressFill.className = 'progress-fill warning';
                } else {
                    progressFill.className = 'progress-fill danger';
                }
                
                const restante = meta - gasto;
                progressInfo.textContent = restante > 0 ? 
                    `Restam R$ ${restante.toFixed(2)} da sua meta` : 
                    `Você ultrapassou a meta em R$ ${Math.abs(restante).toFixed(2)}`;
            }
            
            function updateCharts() {
                // Gráfico de categorias
                const ctx1 = document.getElementById('categoryChart').getContext('2d');
                new Chart(ctx1, {
                    type: 'doughnut',
                    data: {
                        labels: Object.keys(currentData.categorias),
                        datasets: [{
                            data: Object.values(currentData.categorias),
                            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
                        }]
                    },
                    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
                });
                
                // Gráfico semanal
                const ctx2 = document.getElementById('weeklyChart').getContext('2d');
                new Chart(ctx2, {
                    type: 'bar',
                    data: {
                        labels: currentData.gastosPorSemana.labels,
                        datasets: [{
                            label: 'Gastos por Semana',
                            data: currentData.gastosPorSemana.values,
                            backgroundColor: 'rgba(102, 126, 234, 0.8)'
                        }]
                    },
                    options: { responsive: true, scales: { y: { beginAtZero: true } } }
                });
                
                // Gráfico por dia da semana
                const ctx3 = document.getElementById('weekdayChart').getContext('2d');
                new Chart(ctx3, {
                    type: 'bar',
                    data: {
                        labels: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
                        datasets: [{
                            label: 'Gastos por Dia',
                            data: currentData.gastosPorDia,
                            backgroundColor: 'rgba(102, 126, 234, 0.8)'
                        }]
                    },
                    options: { responsive: true, scales: { y: { beginAtZero: true } } }
                });
                
                // Gráfico Top 5 Gastos
                const ctx4 = document.getElementById('topGastosChart').getContext('2d');
                new Chart(ctx4, {
                    type: 'bar',
                    data: {
                        labels: currentData.topGastos.labels,
                        datasets: [{
                            label: 'Valor (R$)',
                            data: currentData.topGastos.values,
                            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
                        }]
                    },
                    options: { 
                        responsive: true, 
                        indexAxis: 'y',
                        scales: { x: { beginAtZero: true } },
                        plugins: { legend: { display: false } }
                    }
                });
            }
            
            function updateInsights() {
                document.getElementById('categoriaCresceu').innerHTML = currentData.insights.categoriaCresceu;
                document.getElementById('diaCaro').innerHTML = currentData.insights.diaCaro;
                document.getElementById('dicaEconomia').innerHTML = currentData.insights.dicaEconomia;
                document.getElementById('padraoGastos').innerHTML = currentData.insights.padraoGastos;
            }
            
            async function updateMeta() {
                const meta = document.getElementById('metaInput').value;
                await fetch('/api/update-meta', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ meta: parseFloat(meta) })
                });
                updateProgress();
            }
            
            function exportarRelatorio() {
                // Criar link temporário para download
                const link = document.createElement('a');
                link.href = '/api/export-pdf';
                link.download = 'relatorio_gastos.pdf';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
            
            function backupDados() {
                // Criar link temporário para download
                const link = document.createElement('a');
                link.href = '/api/backup';
                link.download = 'backup_gastos.json';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
            
            // Carregar dados ao iniciar
            loadData();
            
            // Atualizar automaticamente
            setInterval(loadData, 60000);
        </script>
    </body>
    </html>
    """

@app.route("/api/complete-data")
def complete_data():
    """API completa com todas as análises"""
    global sheet
    
    if not sheet:
        return jsonify({'error': 'Google Sheets não conectado'}), 500
    
    try:
        periodo = request.args.get('periodo', 'atual')
        gastos = sheet.get_all_records()
        print(f"📋 Total de gastos: {len(gastos)}")
        config = load_config()
        
        # Análises por período
        hoje = datetime.now()
        
        if periodo == 'atual':
            mes_atual = hoje.strftime("%m/%Y")
            gastos_periodo = [g for g in gastos if mes_atual in str(g.get('Data', ''))]
        elif periodo == 'anterior':
            mes_anterior = (hoje.replace(day=1) - timedelta(days=1)).strftime("%m/%Y")
            gastos_periodo = [g for g in gastos if mes_anterior in str(g.get('Data', ''))]
        else:  # ano
            ano_atual = hoje.strftime("%Y")
            gastos_periodo = [g for g in gastos if ano_atual in str(g.get('Data', ''))]
        
        # Cálculos básicos
        gasto_atual = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_periodo)
        
        # Meta mensal
        meta_mensal = config.get('meta_mensal', 2000)
        restante_meta = max(0, meta_mensal - gasto_atual)
        
        # Gastos últimos 7 dias
        ultimos_7_dias = calcular_ultimos_7_dias(gastos)
        
        # Maior gasto individual do mês
        maior_gasto = max([float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_periodo], default=0)
        
        # Categorias
        categorias = {}
        for gasto in gastos_periodo:
            cat = gasto.get('Categoria', 'outros').title()
            valor = float(str(gasto.get('Valor', '0')).replace(',', '.'))
            categorias[cat] = categorias.get(cat, 0) + valor
        
        # Evolução mensal (últimos 12 meses)
        evolucao_mensal = calcular_evolucao_mensal(gastos, 12)
        
        # Gastos por dia da semana
        gastos_por_dia = calcular_gastos_por_dia_semana(gastos_periodo)
        
        # Gastos por semana do mês
        gastos_por_semana = calcular_gastos_por_semana_mes(gastos_periodo)
        
        # Top 5 maiores gastos
        top_gastos = calcular_top_gastos(gastos_periodo, 5)
        
        # Insights
        insights = gerar_insights(gastos, gastos_periodo, categorias)
        
        # Mudanças percentuais (comparação com mês anterior)
        changes = calcular_mudancas_novas(gastos, gasto_atual, restante_meta, ultimos_7_dias, maior_gasto)
        
        return jsonify({
            'gastoAtual': gasto_atual,
            'restanteMeta': restante_meta,
            'ultimos7Dias': ultimos_7_dias,
            'maiorGasto': maior_gasto,
            'categorias': categorias,
            'gastosPorDia': gastos_por_dia,
            'gastosPorSemana': gastos_por_semana,
            'topGastos': top_gastos,
            'insights': insights,
            'planilhaLink': f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
            'changeAtual': changes['atual'],
            'changeRestante': changes['restante'],
            'change7Dias': changes['dias7'],
            'changeMaior': changes['maior']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calcular_media_movel(gastos, meses):
    """Calcula média móvel dos últimos N meses"""
    hoje = datetime.now()
    total = 0
    count = 0
    
    for i in range(meses):
        mes = (hoje.replace(day=1) - timedelta(days=i*30)).strftime("%m/%Y")
        gastos_mes = [g for g in gastos if mes in str(g.get('Data', ''))]
        total += sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_mes)
        count += 1
    
    return total / count if count > 0 else 0

def calcular_evolucao_mensal(gastos, meses):
    """Calcula evolução dos últimos N meses"""
    hoje = datetime.now()
    labels = []
    values = []
    
    for i in range(meses-1, -1, -1):
        mes_data = hoje.replace(day=1) - timedelta(days=i*30)
        mes_str = mes_data.strftime("%m/%Y")
        mes_label = mes_data.strftime("%b/%y")
        
        gastos_mes = [g for g in gastos if mes_str in str(g.get('Data', ''))]
        total_mes = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_mes)
        
        labels.append(mes_label)
        values.append(total_mes)
    
    return {'labels': labels, 'values': values}

def calcular_gastos_por_dia_semana(gastos_periodo):
    """Calcula gastos por dia da semana"""
    gastos_dia = [0] * 7  # Dom=0, Seg=1, ..., Sáb=6
    
    for gasto in gastos_periodo:
        try:
            data_str = gasto.get('Data', '')
            if '/' in data_str:
                data = datetime.strptime(data_str, '%d/%m/%Y')
                dia_semana = data.weekday()
                dia_semana = (dia_semana + 1) % 7  # Ajustar para Dom=0
                valor = float(str(gasto.get('Valor', '0')).replace(',', '.'))
                gastos_dia[dia_semana] += valor
        except:
            continue
    
    return gastos_dia

def calcular_tendencia(gastos):
    """Calcula tendência dos últimos 30 dias"""
    hoje = datetime.now()
    labels = []
    gastos_values = []
    media_values = []
    
    for i in range(29, -1, -1):
        data = hoje - timedelta(days=i)
        data_str = data.strftime('%d/%m/%Y')
        
        gastos_dia = [g for g in gastos if data_str in str(g.get('Data', ''))]
        total_dia = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_dia)
        
        labels.append(data.strftime('%d/%m'))
        gastos_values.append(total_dia)
        
        # Média móvel de 7 dias
        if len(gastos_values) >= 7:
            media_7_dias = sum(gastos_values[-7:]) / 7
            media_values.append(media_7_dias)
        else:
            media_values.append(total_dia)
    
    return {'labels': labels, 'gastos': gastos_values, 'media': media_values}

def gerar_insights(gastos, gastos_periodo, categorias):
    """Gera insights inteligentes com dados reais"""
    
    # Dia mais caro (dados reais)
    gastos_por_data = {}
    for gasto in gastos_periodo:
        data = gasto.get('Data', '')
        if data:
            valor = float(str(gasto.get('Valor', '0')).replace(',', '.'))
            gastos_por_data[data] = gastos_por_data.get(data, 0) + valor
    
    if gastos_por_data:
        dia_mais_caro = max(gastos_por_data.items(), key=lambda x: x[1])
        try:
            data_obj = datetime.strptime(dia_mais_caro[0], '%d/%m/%Y')
            dia_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'][data_obj.weekday()]
            dia_caro = f"{dia_semana}, {dia_mais_caro[0]} - R$ {dia_mais_caro[1]:.2f}"
        except:
            dia_caro = f"{dia_mais_caro[0]} - R$ {dia_mais_caro[1]:.2f}"
    else:
        dia_caro = "Nenhum gasto registrado ainda"
    
    # Categoria que mais cresceu (comparação com mês anterior)
    hoje = datetime.now()
    mes_anterior = (hoje.replace(day=1) - timedelta(days=1)).strftime("%m/%Y")
    gastos_mes_anterior = [g for g in gastos if mes_anterior in str(g.get('Data', ''))]
    
    categorias_anterior = {}
    for gasto in gastos_mes_anterior:
        cat = gasto.get('Categoria', 'outros').title()
        valor = float(str(gasto.get('Valor', '0')).replace(',', '.'))
        categorias_anterior[cat] = categorias_anterior.get(cat, 0) + valor
    
    maior_crescimento = ""
    for cat, valor_atual in categorias.items():
        valor_anterior = categorias_anterior.get(cat, 0)
        if valor_anterior > 0:
            crescimento = ((valor_atual - valor_anterior) / valor_anterior) * 100
            if crescimento > 0:
                maior_crescimento = f"{cat} cresceu {crescimento:.1f}% este mês"
                break
    
    if not maior_crescimento:
        if categorias:
            maior_cat = max(categorias.items(), key=lambda x: x[1])[0]
            maior_crescimento = f"{maior_cat} é sua maior categoria de gastos"
        else:
            maior_crescimento = "Comece registrando seus gastos para ver tendências"
    
    # Dica de economia (baseada na maior categoria)
    if categorias:
        maior_categoria = max(categorias.items(), key=lambda x: x[1])
        economia_possivel = maior_categoria[1] * 0.15  # 15% de economia
        dica_economia = f"Reduza 15% dos gastos em {maior_categoria[0]} e economize R$ {economia_possivel:.2f}"
    else:
        dica_economia = "Registre mais gastos para receber dicas personalizadas"
    
    # Padrão de gastos (baseado nos dias da semana)
    gastos_semana = calcular_gastos_por_dia_semana(gastos_periodo)
    if sum(gastos_semana) > 0:
        dias = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
        dia_maior_gasto = dias[gastos_semana.index(max(gastos_semana))]
        padrao_gastos = f"Você gasta mais nas {dia_maior_gasto}s. Planeje atividades mais econômicas neste dia."
    else:
        padrao_gastos = "Continue registrando gastos para identificar padrões"
    
    return {
        'categoriaCresceu': maior_crescimento,
        'diaCaro': dia_caro,
        'dicaEconomia': dica_economia,
        'padraoGastos': padrao_gastos
    }

def calcular_ultimos_7_dias(gastos):
    """Calcula gastos dos últimos 7 dias"""
    hoje = datetime.now()
    total_7_dias = 0
    
    for i in range(7):
        data = hoje - timedelta(days=i)
        data_str = data.strftime('%d/%m/%Y')
        gastos_dia = [g for g in gastos if data_str in str(g.get('Data', ''))]
        total_7_dias += sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_dia)
    
    return total_7_dias

def calcular_gastos_por_semana_mes(gastos_periodo):
    """Calcula gastos por semana do mês atual"""
    hoje = datetime.now()
    primeiro_dia = hoje.replace(day=1)
    
    # Dividir o mês em 4 semanas
    semanas = {
        'Semana 1 (1-7)': 0,
        'Semana 2 (8-14)': 0,
        'Semana 3 (15-21)': 0,
        'Semana 4 (22+)': 0
    }
    
    for gasto in gastos_periodo:
        try:
            data_str = gasto.get('Data', '')
            if '/' in data_str:
                data = datetime.strptime(data_str, '%d/%m/%Y')
                dia = data.day
                valor = float(str(gasto.get('Valor', '0')).replace(',', '.'))
                
                if 1 <= dia <= 7:
                    semanas['Semana 1 (1-7)'] += valor
                elif 8 <= dia <= 14:
                    semanas['Semana 2 (8-14)'] += valor
                elif 15 <= dia <= 21:
                    semanas['Semana 3 (15-21)'] += valor
                else:
                    semanas['Semana 4 (22+)'] += valor
        except:
            continue
    
    return {
        'labels': list(semanas.keys()),
        'values': list(semanas.values())
    }

def calcular_top_gastos(gastos_periodo, limite=5):
    """Calcula os maiores gastos individuais"""
    gastos_ordenados = []
    
    for gasto in gastos_periodo:
        try:
            descricao = gasto.get('Descrição', 'N/A')[:20]
            valor = float(str(gasto.get('Valor', '0')).replace(',', '.'))
            data = gasto.get('Data', '')
            
            gastos_ordenados.append({
                'descricao': f"{descricao} ({data})",
                'valor': valor
            })
        except:
            continue
    
    # Ordenar por valor e pegar os top N
    gastos_ordenados.sort(key=lambda x: x['valor'], reverse=True)
    top_gastos = gastos_ordenados[:limite]
    
    return {
        'labels': [g['descricao'] for g in top_gastos],
        'values': [g['valor'] for g in top_gastos]
    }

def calcular_mudancas_novas(gastos, gasto_atual, restante_meta, ultimos_7_dias, maior_gasto):
    """Calcula mudanças percentuais com as novas métricas"""
    hoje = datetime.now()
    mes_anterior = (hoje.replace(day=1) - timedelta(days=1)).strftime("%m/%Y")
    
    # Gasto do mês anterior
    gastos_mes_anterior = [g for g in gastos if mes_anterior in str(g.get('Data', ''))]
    gasto_anterior = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_mes_anterior)
    
    # Calcular mudanças
    change_atual = ((gasto_atual - gasto_anterior) / gasto_anterior * 100) if gasto_anterior > 0 else 0
    
    # Para restante da meta (positivo = bom, negativo = ruim)
    change_restante = (restante_meta / 2000 * 100) - 50  # Baseado na meta padrão
    
    # Para 7 dias (comparar com média semanal do mês anterior)
    media_semanal_anterior = gasto_anterior / 4 if gasto_anterior > 0 else 0
    change_7_dias = ((ultimos_7_dias - media_semanal_anterior) / media_semanal_anterior * 100) if media_semanal_anterior > 0 else 0
    
    # Para maior gasto (comparar com maior do mês anterior)
    maior_anterior = max([float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_mes_anterior], default=0)
    change_maior = ((maior_gasto - maior_anterior) / maior_anterior * 100) if maior_anterior > 0 else 0
    
    return {
        'atual': change_atual,
        'restante': change_restante,
        'dias7': change_7_dias,
        'maior': change_maior
    }

@app.route("/api/update-meta", methods=['POST'])
def update_meta():
    """Atualiza meta mensal"""
    data = request.get_json()
    config = load_config()
    config['meta_mensal'] = data['meta']
    save_config(config)
    return jsonify({'success': True})

@app.route("/api/export-pdf")
def export_pdf():
    """Exporta relatório em PDF real"""
    try:
        from flask import send_file
        import io
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Obter dados
        gastos = sheet.get_all_records() if sheet else []
        hoje = datetime.now()
        mes_atual = hoje.strftime("%m/%Y")
        gastos_mes = [g for g in gastos if mes_atual in str(g.get('Data', ''))]
        total_mes = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_mes)
        
        # Criar PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Título
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, 750, f"Relatório de Gastos - {hoje.strftime('%B/%Y')}")
        
        # Resumo
        p.setFont("Helvetica", 12)
        p.drawString(50, 700, f"Total do mês: R$ {total_mes:.2f}")
        p.drawString(50, 680, f"Quantidade de gastos: {len(gastos_mes)}")
        p.drawString(50, 660, f"Gerado em: {hoje.strftime('%d/%m/%Y às %H:%M')}")
        
        # Lista de gastos
        p.drawString(50, 620, "Gastos do mês:")
        y = 600
        for gasto in gastos_mes[-20:]:  # Últimos 20 gastos
            desc = gasto.get('Descrição', 'N/A')[:30]
            valor = gasto.get('Valor', '0')
            data = gasto.get('Data', 'N/A')
            p.drawString(50, y, f"{data} - {desc} - R$ {valor}")
            y -= 20
            if y < 100:
                break
        
        p.save()
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'relatorio_gastos_{hoje.strftime("%m_%Y")}.pdf',
            mimetype='application/pdf'
        )
        
    except ImportError:
        return "Para gerar PDF, instale: pip install reportlab"
    except Exception as e:
        return f"Erro ao gerar PDF: {str(e)}"

@app.route("/api/backup")
def backup():
    """Backup dos dados real"""
    try:
        from flask import send_file
        import json
        import io
        
        # Obter todos os dados
        gastos = sheet.get_all_records() if sheet else []
        
        # Criar backup JSON
        backup_data = {
            'data_backup': datetime.now().isoformat(),
            'total_gastos': len(gastos),
            'gastos': gastos
        }
        
        # Converter para JSON
        json_str = json.dumps(backup_data, indent=2, ensure_ascii=False)
        buffer = io.BytesIO(json_str.encode('utf-8'))
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'backup_gastos_{datetime.now().strftime("%Y%m%d_%H%M")}.json',
            mimetype='application/json'
        )
        
    except Exception as e:
        return f"Erro ao gerar backup: {str(e)}"

def start_bot_background():
    """Inicia o bot em background"""
    import subprocess
    import sys
    try:
        subprocess.Popen([sys.executable, 'bot_completo.py'])
        print("✅ Bot iniciado em background")
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")

if __name__ == "__main__":
    print(f"🌐 Dashboard iniciando em http://localhost:{PORT}")
    
    # Iniciar bot em background
    import threading
    bot_thread = threading.Thread(target=start_bot_background, daemon=True)
    bot_thread.start()
    
    # Aguardar um pouco para o bot iniciar
    import time
    time.sleep(2)
    
    # Iniciar dashboard
    app.run(host='0.0.0.0', port=PORT, debug=False)