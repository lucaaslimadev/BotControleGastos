# 🚀 Guia de Deploy

## Opções de Deploy

### 1. Railway (Recomendado)
- ✅ Gratuito até 500h/mês
- ✅ Deploy automático via GitHub
- ✅ Suporte nativo ao Python
- ✅ Variáveis de ambiente fáceis

#### Passos:
1. Acesse [railway.app](https://railway.app)
2. Conecte sua conta GitHub
3. Selecione este repositório
4. Configure as variáveis de ambiente:
   - `TELEGRAM_TOKEN`
   - `SHEET_ID`
   - `PORT=8000`
5. Faça upload do `credentials.json` na pasta `config/`
6. Deploy automático!

### 2. Heroku
- ✅ Plano gratuito disponível
- ✅ Fácil configuração
- ⚠️ Dorme após 30min de inatividade

#### Passos:
1. Instale Heroku CLI
2. `heroku create seu-app-name`
3. `heroku config:set TELEGRAM_TOKEN=seu_token`
4. `heroku config:set SHEET_ID=seu_sheet_id`
5. `git push heroku main`

### 3. Render
- ✅ Gratuito com limitações
- ✅ Deploy via GitHub
- ⚠️ Pode ser mais lento

## Configuração Pré-Deploy

### 1. Telegram Bot
1. Fale com @BotFather no Telegram
2. `/newbot` e siga as instruções
3. Copie o token gerado
4. Configure no `.env` ou variáveis do deploy

### 2. Google Sheets
1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto
3. Ative a Google Sheets API
4. Crie uma Service Account
5. Baixe o `credentials.json`
6. Crie uma planilha e copie o ID da URL
7. Compartilhe a planilha com o email da Service Account

### 3. Estrutura da Planilha
A planilha deve ter as colunas:
- A: Data
- B: Categoria  
- C: Descrição
- D: Valor

## Verificação Pós-Deploy

1. ✅ Bot responde no Telegram
2. ✅ Dashboard acessível via URL
3. ✅ Dados salvos na planilha
4. ✅ Logs funcionando

## Troubleshooting

### Bot não responde
- Verifique o `TELEGRAM_TOKEN`
- Confirme que o bot está ativo
- Veja os logs do deploy

### Erro Google Sheets
- Verifique o `credentials.json`
- Confirme permissões da planilha
- Teste o `SHEET_ID`

### Dashboard não carrega
- Verifique a porta configurada
- Confirme se o processo web está rodando
- Veja logs de erro

## Monitoramento

- Logs disponíveis no painel da plataforma
- Dashboard mostra estatísticas em tempo real
- Bot envia confirmações de cada operação

## Backup

- Use `/backup` no bot para download dos dados
- Configure backup automático da planilha
- Mantenha cópia do `credentials.json`