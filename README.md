# 🤖 Bot WhatsApp - Controle de Gastos

Um bot inteligente para WhatsApp que ajuda você a controlar seus gastos pessoais de forma simples e eficiente.

## 📋 Funcionalidades

### 💬 Comandos WhatsApp
- **Registrar gastos**: `mercado 50`, `uber 25.50`, `R$ 100 farmácia`
- **Consultar saldo**: `saldo` - Total gasto no mês
- **Gastos do dia**: `hoje` - Lista gastos do dia atual
- **Exportar dados**: `exportar` - Link da planilha Google Sheets
- **Deletar gasto**: `deletar` - Remove último gasto registrado
- **Ajuda**: `ajuda` - Lista todos os comandos

### 🏷️ Categorização Automática
- **Alimentação**: mercado, restaurante, lanche, pizza
- **Transporte**: uber, taxi, gasolina, ônibus
- **Saúde**: farmácia, médico, hospital, remédio
- **Lazer**: cinema, bar, show, viagem
- **Casa**: luz, água, internet, aluguel
- **Educação**: curso, livro, escola, material

### 📊 Dashboard Web
- Estatísticas mensais e gerais
- Gráficos por categoria
- Histórico de gastos
- Interface responsiva

### 🎯 Recursos Avançados
- Reconhecimento inteligente de valores
- Suporte a múltiplos formatos: "50", "R$ 50", "cinquenta reais"
- Integração com Google Sheets
- Logs detalhados
- Tratamento de erros robusto

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- Conta no Meta for Developers
- Google Cloud Service Account
- ngrok (para desenvolvimento local)

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/bot-controle-gastos.git
cd bot-controle-gastos
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:
```env
WHATSAPP_TOKEN=seu_token_aqui
PHONE_NUMBER_ID=seu_phone_id_aqui
SHEET_ID=id_da_sua_planilha
VERIFY_TOKEN=seu_token_verificacao
```

### 4. Configure o Google Sheets
1. Crie um projeto no Google Cloud Console
2. Ative a Google Sheets API
3. Crie uma Service Account
4. Baixe o arquivo `credentials.json`
5. Coloque o arquivo na pasta `config/`

### 5. Execute o bot
```bash
python src/app.py
```

### 6. Configure o webhook
1. Use ngrok para expor sua aplicação: `ngrok http 8000`
2. Configure o webhook no Meta for Developers
3. URL: `https://sua-url.ngrok.io/webhook`
4. Token: valor do `VERIFY_TOKEN`

## 📱 Como Usar

### Registrar Gastos
```
mercado 150
uber 25.50
R$ 100 farmácia
cinquenta reais gasolina
```

### Consultar Informações
```
saldo          # Total do mês
hoje           # Gastos de hoje
exportar       # Link da planilha
deletar        # Remove último gasto
ajuda          # Lista comandos
```

## 🛠️ Tecnologias

- **Backend**: Python, Flask
- **WhatsApp API**: Meta Business API
- **Banco de Dados**: Google Sheets
- **Frontend**: HTML, CSS, JavaScript
- **Deploy**: ngrok (desenvolvimento)

## 📊 Dashboard

Acesse `http://localhost:8000/dashboard` para ver:
- Estatísticas mensais
- Gastos por categoria
- Histórico detalhado
- Links úteis

## 🔧 Configuração Avançada

### Personalizar Categorias
Edite o arquivo `src/categories.py` para adicionar suas próprias categorias e palavras-chave.

### Modificar Templates
Os templates HTML estão em `templates/` e podem ser personalizados.

### Logs
Os logs são salvos automaticamente e podem ser configurados em `src/config.py`.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -m 'Adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/bot-controle-gastos/issues)
- **Documentação**: [Wiki](https://github.com/seu-usuario/bot-controle-gastos/wiki)

## 📈 Roadmap

- [ ] Notificações por email
- [ ] Relatórios em PDF
- [ ] Integração com bancos
- [ ] App mobile
- [ ] Múltiplos usuários
- [ ] Backup automático

---

⭐ Se este projeto te ajudou, deixe uma estrela no GitHub!