#!/usr/bin/env python3
import requests
from src.sheets_service import SheetsService
from src.utils import extrair_valor_melhorado, limpar_descricao
from src.categories import categorizar_gasto

TOKEN = "7907909261:AAFTVrpSpIDNL8CiB5dKnqrlJvB81x-4oDs"
sheets = SheetsService()

# Processar mensagem "mercado 50" diretamente
texto = "mercado 50"
chat_id = 8077221512

print(f"Processando: '{texto}'")

valor = extrair_valor_melhorado(texto)
print(f"Valor extraído: {valor}")

descricao = limpar_descricao(texto)
print(f"Descrição: '{descricao}'")

categoria = categorizar_gasto(descricao)
print(f"Categoria: {categoria}")

resultado = sheets.adicionar_gasto(descricao, valor, categoria)
print(f"Salvo na planilha: {resultado}")

# Enviar resposta
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
response = requests.post(url, json={"chat_id": chat_id, "text": f"✅ {descricao} - R$ {valor:.2f}"})
print(f"Resposta enviada: {response.status_code}")

print("Teste concluído!")