# 🤖 Setup Bot Telegram - Controle de Gastos

## 🚀 Migração Completa do WhatsApp para Telegram

### Por que Telegram?
- ✅ **Muito mais simples** - Apenas um token
- ✅ **Sem verificação de negócio** - Não precisa WhatsApp Business
- ✅ **API gratuita** - Sem limitações
- ✅ **Configuração rápida** - 5 minutos

## 📋 Passo a Passo

### 1. Criar Bot no Telegram
1. Abra o Telegram e procure por `@BotFather`
2. Digite `/newbot`
3. Escolha um nome: `Controle de Gastos Bot`
4. Escolha um username: `seunome_gastos_bot`
5. **Copie o token** que aparece (ex: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Configurar Variáveis
Edite seu arquivo `.env`:
```env
# Telegram
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Google Sheets (mantém o mesmo)
SHEET_ID=sua_planilha_id
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Executar Bot Telegram
```bash
python -c "from src.app_telegram import main; main()"
```

### 5. Configurar Webhook
Com o bot rodando, configure o webhook:
```bash
# Use ngrok para expor localmente
ngrok http 8000

# Configure webhook (substitua SEU_TOKEN e SUA_URL)
curl -X POST "https://api.telegram.org/botSEU_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://sua-url.ngrok.io/webhook"}'
```

## 📱 Como Usar

### Comandos Telegram
```
/start - Iniciar bot
/saldo - Total do mês
/hoje - Gastos de hoje
/exportar - Link da planilha
/deletar - Remove último gasto
/ajuda - Lista comandos
```

### Registrar Gastos
```
mercado 50
uber 25.50
R$ 100 farmácia
```

## 🔧 Diferenças do WhatsApp

| Recurso | WhatsApp | Telegram |
|---------|----------|----------|
| **Setup** | Complexo | Simples |
| **Token** | Múltiplos | 1 token |
| **Verificação** | Business | Não precisa |
| **Comandos** | Texto | `/comando` |
| **Markdown** | Limitado | Completo |
| **Webhook** | Complexo | Direto |

## 🎯 Vantagens Telegram

- **Sem limites de API**
- **Markdown completo**
- **Comandos nativos** (`/start`, `/help`)
- **Grupos e canais** (futuro)
- **Inline keyboards** (botões)
- **Arquivos e mídia**

## 🚀 Deploy Produção

### Railway/Render
```bash
# Adicione no seu deploy
TELEGRAM_TOKEN=seu_token_real
```

### Webhook Produção
```bash
curl -X POST "https://api.telegram.org/botSEU_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://seu-app.railway.app/webhook"}'
```

## 🔄 Migração dos Dados

Seus dados do Google Sheets **permanecem iguais**. Apenas muda a interface de comunicação.

## ✅ Teste Rápido

1. Inicie o bot: `python -c "from src.app_telegram import main; main()"`
2. Configure webhook local
3. Envie `/start` para seu bot
4. Teste: `mercado 50`
5. Verifique: `/saldo`

**Pronto! Seu bot está funcionando no Telegram! 🎉**