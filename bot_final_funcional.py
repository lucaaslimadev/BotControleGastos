#!/usr/bin/env python3
"""
Bot Telegram - Controle de Gastos
Versão Final Funcional - Código Limpo
"""
import requests
import time
import re
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
from dotenv import load_dotenv

# Carregar variáveis
load_dotenv()

# Configurações
TOKEN = os.getenv('TELEGRAM_TOKEN')
SHEET_ID = os.getenv('SHEET_ID')
CREDENTIALS_FILE = 'config/credentials.json'

print(f"🔧 TOKEN: {TOKEN[:10]}..." if TOKEN else "❌ TOKEN não encontrado")
print(f"🔧 SHEET_ID: {SHEET_ID}")

if not TOKEN or not SHEET_ID:
    print("❌ Configurações faltando no .env")
    exit(1)

# Conectar Google Sheets
try:
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE, 
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_ID).sheet1
    
    # Configurar cabeçalho se necessário
    headers = sheet.row_values(1) if sheet.row_count > 0 else []
    if not headers or headers != ["Data", "Descrição", "Valor", "Categoria"]:
        sheet.clear()
        sheet.append_row(["Data", "Descrição", "Valor", "Categoria"])
    
    print("✅ Google Sheets conectado")
except Exception as e:
    print(f"❌ Erro Google Sheets: {e}")
    exit(1)

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
    """Envia mensagem para Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        response = requests.post(url, json={"chat_id": chat_id, "text": texto}, timeout=10)
        return response.status_code == 200
    except:
        return False

def salvar_gasto(descricao, valor, categoria):
    """Salva gasto na planilha"""
    try:
        hoje = datetime.now().strftime("%d/%m/%Y")
        sheet.append_row([hoje, descricao, f"{valor:.2f}", categoria])
        print(f"💰 SALVO: {descricao} - R$ {valor:.2f} ({categoria})")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        return False

def calcular_saldo():
    """Calcula saldo do mês"""
    try:
        records = sheet.get_all_records()
        mes_atual = datetime.now().strftime("%m/%Y")
        total = 0
        
        for record in records:
            data = str(record.get('Data', ''))
            if mes_atual in data:
                valor_str = str(record.get('Valor', '0')).replace(',', '.')
                try:
                    total += float(valor_str)
                except:
                    continue
        
        return total
    except:
        return 0

def processar_mensagem(chat_id, texto, nome_usuario):
    """Processa mensagem do usuário"""
    print(f"📱 {nome_usuario} ({chat_id}): {texto}")
    
    # Comandos
    if texto.startswith('/'):
        comando = texto[1:].lower()
        
        if comando == "start":
            enviar_mensagem(chat_id, f"🤖 Olá {nome_usuario}!\n\n✅ Bot funcionando!\n\nDigite: mercado 50")
        
        elif comando == "saldo":
            # Resposta imediata, cálculo em background
            enviar_mensagem(chat_id, "💰 Calculando...")
            import threading
            def calcular():
                total = calcular_saldo()
                mes = datetime.now().strftime("%m/%Y")
                enviar_mensagem(chat_id, f"💰 Saldo {mes}: R$ {total:.2f}")
            threading.Thread(target=calcular, daemon=True).start()
        
        elif comando == "planilha":
            link = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
            enviar_mensagem(chat_id, f"📊 Planilha:\n{link}")
        
        elif comando == "ajuda":
            enviar_mensagem(chat_id, """🤖 Comandos:

💰 Registrar gastos:
• mercado 50
• uber 25.50
• R$ 100 farmácia

📊 Consultas:
• /saldo - Total do mês
• /planilha - Ver planilha
• /ajuda - Esta mensagem""")
    
    else:
        # Processar gasto - RESPOSTA INSTANTÂNEA
        valor = extrair_valor(texto)
        if valor:
            descricao = limpar_descricao(texto)
            categoria = categorizar(descricao)
            
            # RESPOSTA IMEDIATA
            enviar_mensagem(chat_id, f"✅ {descricao} - R$ {valor:.2f}\n📂 {categoria.title()}")
            
            # Salvar em background
            import threading
            def salvar():
                if not salvar_gasto(descricao, valor, categoria):
                    enviar_mensagem(chat_id, "⚠️ Erro ao salvar (mas foi registrado)")
            threading.Thread(target=salvar, daemon=True).start()
        else:
            enviar_mensagem(chat_id, "❌ Valor não identificado\nExemplo: mercado 50")

def main():
    """Função principal do bot"""
    print("🚀 Bot Telegram - Controle de Gastos")
    print("✅ Configurações OK")
    
    # Limpar mensagens antigas
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=10)
        if r.json().get("result"):
            last_id = r.json()["result"][-1]["update_id"]
            requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}", timeout=10)
            print(f"🧹 Limpas {len(r.json()['result'])} mensagens antigas")
    except:
        pass
    
    print("✅ Bot aguardando mensagens...")
    
    offset = None
    while True:
        try:
            # Buscar mensagens - POLLING RÁPIDO
            r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", 
                           params={"timeout": 3, "offset": offset}, timeout=5)
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
            
            time.sleep(0.5)  # Polling mais rápido
            
        except KeyboardInterrupt:
            print("\n🛑 Bot interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()