# 🚀 Guia de Deploy

Este guia mostra como fazer deploy do seu bot para manter funcionando 24/7.

## 🎯 Opções Recomendadas (Gratuitas)

### 1. Railway (Mais Fácil) 🚂

#### Vantagens:
- ✅ 500 horas gratuitas/mês
- ✅ Deploy automático via GitHub
- ✅ Domínio HTTPS automático
- ✅ Logs em tempo real

#### Como fazer:
1. **Criar conta**: [railway.app](https://railway.app)
2. **Conectar GitHub**: Autorize acesso ao repositório
3. **Fazer deploy**: Clique em "Deploy from GitHub repo"
4. **Configurar variáveis**:
   ```
   WHATSAPP_TOKEN=seu_token
   PHONE_NUMBER_ID=seu_id
   SHEET_ID=sua_planilha_id
   VERIFY_TOKEN=seu_verify_token
   FLASK_ENV=production
   ```
5. **Upload credentials**: Adicione `credentials.json` via interface

### 2. Render 🎨

#### Vantagens:
- ✅ 750 horas gratuitas/mês
- ✅ SSL automático
- ✅ Deploy contínuo

#### Como fazer:
1. **Criar conta**: [render.com](https://render.com)
2. **Conectar repositório**: Link com GitHub
3. **Configurar serviço**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
4. **Adicionar variáveis de ambiente**
5. **Upload credentials.json**

### 3. Heroku 💜

#### Como fazer:
1. **Instalar Heroku CLI**:
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Ou baixar de heroku.com/cli
   ```

2. **Login e criar app**:
   ```bash
   heroku login
   heroku create seu-bot-gastos
   ```

3. **Configurar variáveis**:
   ```bash
   heroku config:set WHATSAPP_TOKEN=seu_token
   heroku config:set PHONE_NUMBER_ID=seu_id
   heroku config:set SHEET_ID=sua_planilha_id
   heroku config:set VERIFY_TOKEN=seu_verify_token
   heroku config:set FLASK_ENV=production
   ```

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy inicial"
   git push heroku main
   ```

## 🔧 Configuração Pós-Deploy

### 1. Obter URL do Deploy
Após o deploy, você receberá uma URL como:
- Railway: `https://seu-app.railway.app`
- Render: `https://seu-app.onrender.com`
- Heroku: `https://seu-app.herokuapp.com`

### 2. Atualizar Webhook no Meta
1. **Meta for Developers** → **WhatsApp** → **Configuration**
2. **Webhook URL**: `https://sua-url-do-deploy/webhook`
3. **Verify Token**: mesmo valor do `.env`
4. **Salvar e verificar**

### 3. Testar Funcionamento
1. **Health Check**: `https://sua-url/health`
2. **Dashboard**: `https://sua-url/dashboard`
3. **Enviar mensagem** pelo WhatsApp

## 📊 Monitoramento

### Logs em Tempo Real:
```bash
# Railway
railway logs

# Render
# Via dashboard web

# Heroku
heroku logs --tail
```

### Health Check:
Todas as plataformas monitoram automaticamente via `/health`

## 🔄 Deploy Automático

### GitHub Actions (Opcional):
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: railway up
```

## 💰 Custos e Limites

### Railway:
- **Gratuito**: 500 horas/mês
- **Pago**: $5/mês (ilimitado)

### Render:
- **Gratuito**: 750 horas/mês
- **Pago**: $7/mês (ilimitado)

### Heroku:
- **Gratuito**: 550-1000 horas/mês
- **Pago**: $7/mês (ilimitado)

## 🛠️ Solução de Problemas

### Bot não responde:
1. Verificar logs da aplicação
2. Confirmar webhook configurado
3. Testar health check

### Erro de credenciais:
1. Verificar variáveis de ambiente
2. Confirmar upload do credentials.json
3. Testar conexão Google Sheets

### App "dormindo":
- Planos gratuitos podem "dormir" após inatividade
- Solução: upgrade para plano pago ou usar serviço de ping

## 🎯 Recomendação Final

**Para começar**: Use **Railway** (mais fácil)
**Para produção**: Considere plano pago de qualquer plataforma

## 📱 Próximos Passos

Após deploy bem-sucedido:
1. **Monitorar logs** regularmente
2. **Backup das configurações**
3. **Documentar URL final**
4. **Configurar alertas** (opcional)