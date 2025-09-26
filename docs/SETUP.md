# 🚀 Guia de Configuração

Este guia te ajudará a configurar o Bot WhatsApp - Controle de Gastos do zero.

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta no Meta for Developers
- Projeto no Google Cloud Console
- ngrok (para desenvolvimento local)

## 🔧 Configuração Passo a Passo

### 1. Configuração do Google Sheets

#### 1.1 Criar Projeto no Google Cloud
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a **Google Sheets API**:
   - Vá em "APIs & Services" > "Library"
   - Procure por "Google Sheets API"
   - Clique em "Enable"

#### 1.2 Criar Service Account
1. Vá em "APIs & Services" > "Credentials"
2. Clique em "Create Credentials" > "Service Account"
3. Preencha os dados:
   - Nome: `bot-gastos-sa`
   - Descrição: `Service Account para Bot de Gastos`
4. Clique em "Create and Continue"
5. Pule as permissões opcionais
6. Clique em "Done"

#### 1.3 Gerar Chave JSON
1. Na lista de Service Accounts, clique na que você criou
2. Vá na aba "Keys"
3. Clique em "Add Key" > "Create New Key"
4. Selecione "JSON" e clique em "Create"
5. Salve o arquivo como `credentials.json` na pasta `config/`

#### 1.4 Criar Planilha Google Sheets
1. Crie uma nova planilha no Google Sheets
2. Copie o ID da planilha da URL (parte entre `/d/` e `/edit`)
3. Compartilhe a planilha com o email da Service Account
4. Dê permissão de "Editor"

### 2. Configuração do WhatsApp Business API

#### 2.1 Criar App no Meta for Developers
1. Acesse [Meta for Developers](https://developers.facebook.com/)
2. Clique em "My Apps" > "Create App"
3. Selecione "Business" como tipo
4. Preencha os dados do app
5. Adicione o produto "WhatsApp"

#### 2.2 Configurar WhatsApp Business
1. No painel do app, vá em "WhatsApp" > "API Setup"
2. Anote o **Access Token** (temporário)
3. Anote o **Phone Number ID**
4. Adicione seu número na lista de destinatários de teste

#### 2.3 Gerar Token Permanente (Opcional)
Para produção, você precisará gerar um token permanente:
1. Vá em "WhatsApp" > "Configuration"
2. Configure um token de longa duração
3. Siga o processo de verificação do Meta

### 3. Configuração do Projeto

#### 3.1 Clonar e Instalar
```bash
git clone <seu-repositorio>
cd bot-controle-gastos
pip install -r requirements.txt
```

#### 3.2 Configurar Variáveis de Ambiente
```bash
cp .env.example .env
```

Edite o arquivo `.env`:
```env
WHATSAPP_TOKEN=seu_token_aqui
PHONE_NUMBER_ID=seu_phone_id_aqui
SHEET_ID=id_da_sua_planilha
VERIFY_TOKEN=token_personalizado_para_webhook
```

#### 3.3 Mover Credenciais
```bash
mv credentials.json config/credentials.json
```

### 4. Configuração do Webhook

#### 4.1 Expor Aplicação Local
```bash
# Terminal 1: Executar a aplicação
python run.py

# Terminal 2: Expor com ngrok
ngrok http 8000
```

#### 4.2 Configurar Webhook no Meta
1. No Meta for Developers, vá em "WhatsApp" > "Configuration"
2. Na seção "Webhook", clique em "Edit"
3. Configure:
   - **Callback URL**: `https://sua-url.ngrok.io/webhook`
   - **Verify Token**: valor do `VERIFY_TOKEN` do seu `.env`
   - **Webhook Fields**: marque apenas `messages`
4. Clique em "Verify and Save"

## ✅ Teste da Configuração

### 1. Verificar Conexões
Acesse `http://localhost:8000/health` para verificar o status dos serviços.

### 2. Testar Dashboard
Acesse `http://localhost:8000/dashboard` para ver o dashboard.

### 3. Testar WhatsApp
Envie uma mensagem para o número do WhatsApp Business:
```
mercado 50
```

## 🔧 Solução de Problemas

### Erro: "Google Sheets não conectado"
- Verifique se o arquivo `config/credentials.json` existe
- Confirme se a Service Account tem acesso à planilha
- Verifique se a Google Sheets API está ativada

### Erro: "TOKEN EXPIRADO"
- Gere um novo token no Meta for Developers
- Atualize o arquivo `.env`
- Reinicie a aplicação

### Erro: "Webhook não verificado"
- Confirme se a URL do ngrok está correta
- Verifique se o `VERIFY_TOKEN` está correto
- Certifique-se de que a aplicação está rodando

### Mensagens não chegam
- Verifique se seu número está na lista de destinatários
- Confirme se está usando WhatsApp Business
- Para produção, solicite aprovação do app no Meta

## 📚 Próximos Passos

Após a configuração básica:

1. **Personalizar Categorias**: Edite `src/categories.py`
2. **Customizar Templates**: Modifique arquivos em `templates/`
3. **Deploy em Produção**: Configure em um servidor real
4. **Monitoramento**: Configure logs e alertas

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs da aplicação
2. Consulte a documentação oficial das APIs
3. Abra uma issue no GitHub