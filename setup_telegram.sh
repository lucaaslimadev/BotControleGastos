#!/bin/bash
# Setup rápido do Telegram Bot

echo "🤖 Setup Telegram Bot - Controle de Gastos"
echo "=========================================="

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "📝 Copie .env.example para .env e configure TELEGRAM_TOKEN"
    exit 1
fi

# Testar conexão
echo "🔍 Testando conexão com Telegram..."
python test_telegram.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Bot configurado com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Execute: ngrok http 8000"
    echo "2. Configure webhook com a URL do ngrok"
    echo "3. Execute: python -c 'from src.app_telegram import main; main()'"
    echo "4. Teste no Telegram: /start"
else
    echo ""
    echo "❌ Configuração falhou!"
    echo "📝 Verifique o TELEGRAM_TOKEN no arquivo .env"
fi