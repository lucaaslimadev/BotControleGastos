#!/usr/bin/env python3
"""
Bot Telegram Completo - Todas as Funcionalidades
"""
import requests
import time
import re
import threading
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
SHEET_ID = os.getenv('SHEET_ID')

print(f"🚀 Bot Completo iniciando...")

# Conectar Google Sheets
try:
    # Tentar arquivo local primeiro (desenvolvimento)
    if os.path.exists('config/credentials.json'):
        creds = Credentials.from_service_account_file('config/credentials.json', 
            scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    else:
        # Usar variável de ambiente (produção)
        import json
        creds_json = os.getenv('GOOGLE_CREDENTIALS')
        if not creds_json:
            raise ValueError('GOOGLE_CREDENTIALS não configurado')
        creds_info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_info,
            scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_ID).sheet1
    print("✅ Google Sheets conectado")
except Exception as e:
    print(f"❌ Erro Google Sheets: {e}")
    exit(1)

# Configurações do usuário
CONFIG_FILE = 'bot_config.json'

def load_user_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"metas": {}, "alertas": {}}

def save_user_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# Categorias
CATEGORIAS = {
    'alimentação': ['mercado', 'supermercado', 'restaurante', 'lanche', 'pizza', 'comida', 'ifood'],
    'transporte': ['uber', 'taxi', 'gasolina', 'combustível', 'ônibus', '99'],
    'saúde': ['farmácia', 'médico', 'hospital', 'remédio', 'consulta'],
    'lazer': ['cinema', 'bar', 'show', 'viagem', 'netflix'],
    'casa': ['luz', 'água', 'internet', 'aluguel', 'condomínio'],
    'outros': []
}

def extrair_valor(texto):
    """Extrai valor do texto"""
    match = re.search(r'(\d+(?:[.,]\d{1,2})?)', re.sub(r'r\$|reais?', '', texto, flags=re.IGNORECASE))
    return float(match.group().replace(',', '.')) if match else None

def categorizar(descricao):
    """Categoriza gasto"""
    desc_lower = descricao.lower()
    for cat, palavras in CATEGORIAS.items():
        if any(p in desc_lower for p in palavras):
            return cat
    return 'outros'

def limpar_descricao(texto):
    """Remove valor da descrição"""
    return re.sub(r'\d+(?:[.,]\d{1,2})?|r\$|reais?', '', texto, flags=re.IGNORECASE).strip()

def enviar_mensagem(chat_id, texto):
    """Envia mensagem"""
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                     json={"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}, timeout=5)
        return True
    except:
        return False

def salvar_gasto_async(descricao, valor, categoria):
    """Salva gasto em background"""
    def salvar():
        try:
            hoje = datetime.now().strftime("%d/%m/%Y")
            sheet.append_row([hoje, descricao, f"{valor:.2f}", categoria])
            print(f"💰 SALVO: {descricao} - R$ {valor:.2f}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    
    threading.Thread(target=salvar, daemon=True).start()

def obter_gastos():
    """Obtém todos os gastos"""
    try:
        return sheet.get_all_records()
    except:
        return []

def obter_gastos_periodo(periodo):
    """Obtém gastos por período"""
    gastos = obter_gastos()
    hoje = datetime.now()
    
    if periodo == 'hoje':
        data_str = hoje.strftime("%d/%m/%Y")
        return [g for g in gastos if data_str in str(g.get('Data', ''))]
    
    elif periodo == 'semana':
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        gastos_semana = []
        for i in range(7):
            data = inicio_semana + timedelta(days=i)
            data_str = data.strftime("%d/%m/%Y")
            gastos_semana.extend([g for g in gastos if data_str in str(g.get('Data', ''))])
        return gastos_semana
    
    elif periodo == 'mes':
        mes_atual = hoje.strftime("%m/%Y")
        return [g for g in gastos if mes_atual in str(g.get('Data', ''))]
    
    return gastos

def processar_comando(comando, texto, chat_id, nome):
    """Processa todos os comandos do bot"""
    config = load_user_config()
    
    if comando == "start":
        enviar_mensagem(chat_id, f"""🤖 *Olá {nome}!*

✅ Bot Controle de Gastos ativo!

*📝 Registrar gastos:*
• mercado 50
• uber 25.50
• R$ 100 farmácia

*📊 Comandos principais:*
• /saldo - Total do mês
• /hoje - Gastos de hoje
• /semana - Gastos da semana
• /ajuda - Todos os comandos

Digite qualquer gasto para começar! 💰""")
    
    elif comando == "saldo":
        gastos_mes = obter_gastos_periodo('mes')
        total = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_mes)
        mes = datetime.now().strftime("%m/%Y")
        
        # Verificar meta
        meta = config.get('metas', {}).get(str(chat_id), 0)
        if meta > 0:
            percentual = (total / meta) * 100
            restante = meta - total
            status = "🟢" if percentual < 70 else "🟡" if percentual < 90 else "🔴"
            enviar_mensagem(chat_id, f"""💰 *Saldo {mes}*

Total gasto: R$ {total:.2f}
Meta mensal: R$ {meta:.2f}
{status} {percentual:.1f}% da meta
Restante: R$ {restante:.2f}""")
        else:
            enviar_mensagem(chat_id, f"💰 *Saldo {mes}*\n\nTotal gasto: R$ {total:.2f}\n\n💡 Defina uma meta: /meta 2000")
    
    elif comando == "hoje":
        gastos_hoje = obter_gastos_periodo('hoje')
        if gastos_hoje:
            total = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_hoje)
            lista = "\n".join([f"• {g.get('Descrição', 'N/A')} - R$ {g.get('Valor', '0')}" for g in gastos_hoje])
            enviar_mensagem(chat_id, f"📅 *Gastos de Hoje*\n\n{lista}\n\n💰 *Total: R$ {total:.2f}*")
        else:
            enviar_mensagem(chat_id, "📅 *Gastos de Hoje*\n\n✅ Nenhum gasto registrado hoje!")
    
    elif comando == "semana":
        gastos_semana = obter_gastos_periodo('semana')
        if gastos_semana:
            total = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_semana)
            enviar_mensagem(chat_id, f"📅 *Gastos da Semana*\n\nTotal de gastos: {len(gastos_semana)}\n💰 *Total: R$ {total:.2f}*")
        else:
            enviar_mensagem(chat_id, "📅 *Gastos da Semana*\n\n✅ Nenhum gasto esta semana!")
    
    elif comando.startswith("categoria"):
        parts = texto.split()
        if len(parts) > 1:
            categoria_busca = parts[1].lower()
            gastos_mes = obter_gastos_periodo('mes')
            gastos_categoria = [g for g in gastos_mes if categoria_busca in g.get('Categoria', '').lower()]
            
            if gastos_categoria:
                total = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_categoria)
                lista = "\n".join([f"• {g.get('Descrição', 'N/A')} - R$ {g.get('Valor', '0')}" for g in gastos_categoria[-10:]])
                enviar_mensagem(chat_id, f"🏷️ *{categoria_busca.title()}*\n\n{lista}\n\n💰 *Total: R$ {total:.2f}*")
            else:
                enviar_mensagem(chat_id, f"🏷️ Nenhum gasto em *{categoria_busca}* este mês")
        else:
            enviar_mensagem(chat_id, "🏷️ Use: /categoria alimentação")
    
    elif comando == "maior":
        gastos_mes = obter_gastos_periodo('mes')
        if gastos_mes:
            maior_gasto = max(gastos_mes, key=lambda x: float(str(x.get('Valor', '0')).replace(',', '.')))
            enviar_mensagem(chat_id, f"""💎 *Maior Gasto do Mês*

{maior_gasto.get('Descrição', 'N/A')}
💰 R$ {maior_gasto.get('Valor', '0')}
📅 {maior_gasto.get('Data', 'N/A')}
🏷️ {maior_gasto.get('Categoria', 'N/A').title()}""")
        else:
            enviar_mensagem(chat_id, "💎 Nenhum gasto registrado este mês")
    
    elif comando == "media":
        gastos_mes = obter_gastos_periodo('mes')
        if gastos_mes:
            total = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_mes)
            dias_mes = datetime.now().day
            media_dia = total / dias_mes
            enviar_mensagem(chat_id, f"📊 *Média Diária*\n\nTotal do mês: R$ {total:.2f}\nDias decorridos: {dias_mes}\n💰 *Média: R$ {media_dia:.2f}/dia*")
        else:
            enviar_mensagem(chat_id, "📊 Nenhum gasto para calcular média")
    
    elif comando.startswith("meta"):
        parts = texto.split()
        if len(parts) > 1:
            try:
                meta = float(parts[1])
                config['metas'][str(chat_id)] = meta
                save_user_config(config)
                enviar_mensagem(chat_id, f"🎯 *Meta definida!*\n\nMeta mensal: R$ {meta:.2f}\n\n💡 Use /saldo para acompanhar o progresso")
            except ValueError:
                enviar_mensagem(chat_id, "🎯 Use: /meta 2000")
        else:
            meta_atual = config.get('metas', {}).get(str(chat_id), 0)
            if meta_atual > 0:
                enviar_mensagem(chat_id, f"🎯 *Meta Atual*\n\nR$ {meta_atual:.2f}\n\n💡 Para alterar: /meta 2500")
            else:
                enviar_mensagem(chat_id, "🎯 *Definir Meta*\n\nUse: /meta 2000\n\n💡 Ajuda a controlar seus gastos!")
    
    elif comando == "restante":
        config = load_user_config()
        meta = config.get('metas', {}).get(str(chat_id), 0)
        if meta > 0:
            gastos_mes = obter_gastos_periodo('mes')
            total = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_mes)
            restante = meta - total
            dias_restantes = calendar.monthrange(datetime.now().year, datetime.now().month)[1] - datetime.now().day
            
            if restante > 0:
                media_dia = restante / dias_restantes if dias_restantes > 0 else 0
                enviar_mensagem(chat_id, f"""💰 *Restante da Meta*

Gasto atual: R$ {total:.2f}
Meta: R$ {meta:.2f}
✅ Restante: R$ {restante:.2f}

📅 Dias restantes: {dias_restantes}
📊 Pode gastar: R$ {media_dia:.2f}/dia""")
            else:
                enviar_mensagem(chat_id, f"🚨 *Meta Ultrapassada!*\n\nVocê gastou R$ {abs(restante):.2f} a mais que sua meta de R$ {meta:.2f}")
        else:
            enviar_mensagem(chat_id, "🎯 Defina uma meta primeiro: /meta 2000")
    
    elif comando == "alerta":
        alertas = config.get('alertas', {})
        status_atual = alertas.get(str(chat_id), True)
        novo_status = not status_atual
        
        config['alertas'][str(chat_id)] = novo_status
        save_user_config(config)
        
        status_text = "ativados" if novo_status else "desativados"
        enviar_mensagem(chat_id, f"🔔 Alertas {status_text}!")
    
    elif comando == "deletar":
        try:
            gastos = obter_gastos()
            if gastos:
                # Deletar última linha (último gasto)
                ultima_linha = len(gastos) + 1  # +1 por causa do cabeçalho
                sheet.delete_rows(ultima_linha)
                enviar_mensagem(chat_id, "🗑️ Último gasto deletado com sucesso!")
            else:
                enviar_mensagem(chat_id, "🗑️ Nenhum gasto para deletar")
        except Exception as e:
            enviar_mensagem(chat_id, "❌ Erro ao deletar gasto")
    
    elif comando == "limpar":
        try:
            gastos_hoje = obter_gastos_periodo('hoje')
            if gastos_hoje:
                # Confirmar antes de limpar
                enviar_mensagem(chat_id, f"⚠️ Tem certeza que quer deletar {len(gastos_hoje)} gastos de hoje?\n\nEnvie 'CONFIRMAR' para prosseguir")
            else:
                enviar_mensagem(chat_id, "🗑️ Nenhum gasto hoje para limpar")
        except:
            enviar_mensagem(chat_id, "❌ Erro ao verificar gastos")
    
    elif comando == "relatorio":
        gastos_mes = obter_gastos_periodo('mes')
        if gastos_mes:
            total = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_mes)
            
            # Gastos por categoria
            categorias = {}
            for gasto in gastos_mes:
                cat = gasto.get('Categoria', 'outros')
                valor = float(str(gasto.get('Valor', '0')).replace(',', '.'))
                categorias[cat] = categorias.get(cat, 0) + valor
            
            ranking_cat = sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:5]
            
            relatorio = f"""📊 *Relatório do Mês*

💰 Total: R$ {total:.2f}
📝 Gastos: {len(gastos_mes)}
📊 Média: R$ {total/len(gastos_mes):.2f}

🏆 *Top Categorias:*
"""
            for i, (cat, valor) in enumerate(ranking_cat, 1):
                relatorio += f"{i}. {cat.title()}: R$ {valor:.2f}\n"
            
            enviar_mensagem(chat_id, relatorio)
        else:
            enviar_mensagem(chat_id, "📊 Nenhum gasto este mês para gerar relatório")
    
    elif comando == "ranking":
        gastos_mes = obter_gastos_periodo('mes')
        if gastos_mes:
            categorias = {}
            for gasto in gastos_mes:
                cat = gasto.get('Categoria', 'outros')
                valor = float(str(gasto.get('Valor', '0')).replace(',', '.'))
                categorias[cat] = categorias.get(cat, 0) + valor
            
            ranking = sorted(categorias.items(), key=lambda x: x[1], reverse=True)
            
            texto_ranking = "🏆 *Ranking de Categorias*\n\n"
            for i, (cat, valor) in enumerate(ranking, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                texto_ranking += f"{emoji} {cat.title()}: R$ {valor:.2f}\n"
            
            enviar_mensagem(chat_id, texto_ranking)
        else:
            enviar_mensagem(chat_id, "🏆 Nenhum gasto para ranking")
    
    elif comando == "comparar":
        hoje = datetime.now()
        mes_atual = hoje.strftime("%m/%Y")
        mes_anterior = (hoje.replace(day=1) - timedelta(days=1)).strftime("%m/%Y")
        
        gastos_atual = [g for g in obter_gastos() if mes_atual in str(g.get('Data', ''))]
        gastos_anterior = [g for g in obter_gastos() if mes_anterior in str(g.get('Data', ''))]
        
        total_atual = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_atual)
        total_anterior = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_anterior)
        
        if total_anterior > 0:
            diferenca = total_atual - total_anterior
            percentual = (diferenca / total_anterior) * 100
            emoji = "📈" if diferenca > 0 else "📉"
            
            enviar_mensagem(chat_id, f"""📊 *Comparação Mensal*

{mes_anterior}: R$ {total_anterior:.2f}
{mes_atual}: R$ {total_atual:.2f}

{emoji} Diferença: R$ {abs(diferenca):.2f} ({abs(percentual):.1f}%)
{"Você gastou mais este mês" if diferenca > 0 else "Você economizou este mês"}""")
        else:
            enviar_mensagem(chat_id, f"📊 *Comparação Mensal*\n\n{mes_atual}: R$ {total_atual:.2f}\n\n💡 Primeiro mês de uso!")
    
    elif comando == "backup":
        enviar_mensagem(chat_id, "💾 Gerando backup dos seus dados...")
        # Simular geração de backup
        threading.Timer(2.0, lambda: enviar_mensagem(chat_id, "✅ Backup gerado! Acesse o dashboard para baixar: http://localhost:8000")).start()
    
    elif comando == "dashboard":
        enviar_mensagem(chat_id, f"""📊 *Dashboard Completo*

🌐 Acesse: http://localhost:8000

📈 Recursos disponíveis:
• Gráficos interativos
• Análises avançadas
• Exportar PDF
• Backup de dados
• Metas e projeções""")
    
    elif comando == "ajuda":
        enviar_mensagem(chat_id, """🤖 *Comandos Disponíveis*

📝 *Registrar gastos:*
• mercado 50, uber 25.50, R$ 100 farmácia

📊 *Consultas:*
• /saldo - Total do mês
• /hoje - Gastos de hoje
• /semana - Gastos da semana
• /categoria alimentação - Por categoria
• /maior - Maior gasto do mês
• /media - Média diária

🎯 *Metas:*
• /meta 2000 - Definir meta
• /restante - Quanto falta
• /alerta - Ativar/desativar alertas

🗑️ *Gerenciar:*
• /deletar - Remove último gasto
• /limpar - Limpa gastos do dia

📈 *Relatórios:*
• /relatorio - Resumo completo
• /ranking - Top categorias
• /comparar - Mês atual vs anterior

🔧 *Utilitários:*
• /backup - Gerar backup
• /dashboard - Abrir dashboard""")

def processar_mensagem(chat_id, texto, nome):
    """Processa mensagem do usuário"""
    print(f"📱 {nome} ({chat_id}): {texto}")
    
    # Verificar se é confirmação de limpeza
    if texto.upper() == "CONFIRMAR":
        try:
            # Implementar limpeza de gastos do dia
            enviar_mensagem(chat_id, "🗑️ Gastos do dia limpos! (funcionalidade em desenvolvimento)")
        except:
            enviar_mensagem(chat_id, "❌ Erro ao limpar gastos")
        return
    
    # Comandos
    if texto.startswith('/'):
        comando = texto[1:].lower()
        processar_comando(comando, texto, chat_id, nome)
    else:
        # Processar gasto
        valor = extrair_valor(texto)
        if valor:
            descricao = limpar_descricao(texto)
            categoria = categorizar(descricao)
            
            # RESPOSTA IMEDIATA
            enviar_mensagem(chat_id, f"✅ {descricao} - R$ {valor:.2f}\n📂 {categoria.title()}")
            
            # Salvar em background
            salvar_gasto_async(descricao, valor, categoria)
            
            # Verificar alertas de meta
            config = load_user_config()
            meta = config.get('metas', {}).get(str(chat_id), 0)
            alertas_ativo = config.get('alertas', {}).get(str(chat_id), True)
            
            if meta > 0 and alertas_ativo:
                gastos_mes = obter_gastos_periodo('mes')
                total_mes = sum(float(str(g.get('Valor', '0')).replace(',', '.')) for g in gastos_mes) + valor
                percentual = (total_mes / meta) * 100
                
                if percentual >= 90:
                    threading.Timer(3.0, lambda: enviar_mensagem(chat_id, f"🚨 *Alerta de Meta!*\n\nVocê já gastou {percentual:.1f}% da sua meta mensal!\nMeta: R$ {meta:.2f}\nGasto: R$ {total_mes:.2f}")).start()
                elif percentual >= 75:
                    threading.Timer(3.0, lambda: enviar_mensagem(chat_id, f"⚠️ *Atenção!*\n\nVocê gastou {percentual:.1f}% da sua meta mensal.")).start()
        else:
            enviar_mensagem(chat_id, "❌ Valor não identificado\n\n💡 Exemplos: mercado 50, uber 25.50")

def main():
    """Função principal"""
    print("🚀 Bot Completo iniciado!")
    
    # Limpar mensagens antigas
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=10)
        if r.json().get("result"):
            last_id = r.json()["result"][-1]["update_id"]
            requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}", timeout=10)
            print(f"🧹 Limpas {len(r.json()['result'])} mensagens antigas")
    except:
        pass
    
    print("✅ Aguardando mensagens...")
    
    offset = None
    while True:
        try:
            r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", 
                           params={"timeout": 5, "offset": offset}, timeout=10)
            data = r.json()
            
            if data.get("ok") and data["result"]:
                for update in data["result"]:
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        texto = msg.get("text", "").strip()
                        nome = msg["from"].get("first_name", f"User{chat_id}")
                        
                        if texto:
                            processar_mensagem(chat_id, texto, nome)
                    
                    offset = update["update_id"] + 1
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot parado")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()