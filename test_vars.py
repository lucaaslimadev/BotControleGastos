#!/usr/bin/env python3
"""
Teste das variáveis de ambiente do Railway
"""
import os

print("🔍 VERIFICANDO VARIÁVEIS DO RAILWAY:")
print("=" * 50)

# Variáveis principais
vars_principais = [
    'TELEGRAM_TOKEN',
    'SHEET_ID', 
    'GOOGLE_CREDENTIALS',
    'PORT'
]

for var in vars_principais:
    valor = os.getenv(var)
    if valor:
        if var == 'GOOGLE_CREDENTIALS':
            print(f"✅ {var}: JSON definido ({len(valor)} chars)")
        elif var == 'TELEGRAM_TOKEN':
            print(f"✅ {var}: {valor[:10]}...")
        else:
            print(f"✅ {var}: {valor}")
    else:
        print(f"❌ {var}: NÃO DEFINIDO")

print("\n🔍 TODAS AS VARIÁVEIS DE AMBIENTE:")
print("=" * 50)
for key, value in os.environ.items():
    if any(word in key.upper() for word in ['TOKEN', 'SHEET', 'GOOGLE', 'CRED', 'PORT']):
        if 'CREDENTIALS' in key or 'TOKEN' in key:
            print(f"{key}: {value[:20]}..." if len(value) > 20 else f"{key}: {value}")
        else:
            print(f"{key}: {value}")