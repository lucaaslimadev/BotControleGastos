# 🤝 Guia de Contribuição - Expense Tracker Bot

## 🎯 Bem-vindo à Comunidade

Obrigado pelo interesse em contribuir com o **Expense Tracker Bot**! Este guia fornece todas as informações necessárias para contribuir de forma efetiva e profissional.

---

## 📋 Índice

- [🚀 Primeiros Passos](#-primeiros-passos)
- [🔧 Setup do Ambiente](#-setup-do-ambiente)
- [📝 Padrões de Código](#-padrões-de-código)
- [🧪 Testes](#-testes)
- [📦 Processo de Contribuição](#-processo-de-contribuição)
- [🐛 Reportando Bugs](#-reportando-bugs)
- [💡 Sugerindo Features](#-sugerindo-features)
- [📖 Documentação](#-documentação)

---

## 🚀 Primeiros Passos

### Tipos de Contribuição Aceitas

- 🐛 **Bug Fixes**: Correções de problemas identificados
- ✨ **Features**: Novas funcionalidades
- 📚 **Documentação**: Melhorias na documentação
- 🎨 **UI/UX**: Melhorias na interface
- ⚡ **Performance**: Otimizações de performance
- 🔒 **Security**: Melhorias de segurança
- 🧪 **Tests**: Adição ou melhoria de testes

### Antes de Começar

1. ⭐ **Star** o repositório
2. 🍴 **Fork** o projeto
3. 📖 Leia toda esta documentação
4. 🔍 Verifique as [Issues abertas](https://github.com/lucaslima/BotControleGastos/issues)
5. 💬 Participe das [Discussions](https://github.com/lucaslima/BotControleGastos/discussions)

---

## 🔧 Setup do Ambiente

### 1. Clonagem e Configuração Inicial

```bash
# Fork o repositório no GitHub primeiro
git clone https://github.com/SEU_USERNAME/BotControleGastos.git
cd BotControleGastos

# Adicionar upstream
git remote add upstream https://github.com/lucaslima/BotControleGastos.git

# Verificar remotes
git remote -v
```

### 2. Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Verificar Python
python --version  # Deve ser 3.11+
```

### 3. Instalação de Dependências

```bash
# Dependências principais
pip install -r requirements.txt

# Dependências de desenvolvimento
pip install -r requirements-dev.txt

# Verificar instalação
pip list
```

### 4. Configuração do Ambiente

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar .env com suas credenciais de desenvolvimento
# TELEGRAM_TOKEN=seu_token_de_teste
# SHEET_ID=sua_planilha_de_teste
```

### 5. Pre-commit Hooks

```bash
# Instalar pre-commit hooks
pre-commit install

# Testar hooks
pre-commit run --all-files
```

---

## 📝 Padrões de Código

### Code Style

Utilizamos **Black** para formatação automática e **Flake8** para linting:

```bash
# Formatação automática
black .

# Verificar linting
flake8 .

# Organizar imports
isort .

# Type checking
mypy bot_completo.py dashboard_completo.py
```

### Configurações

**pyproject.toml**:
```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
```

### Convenções de Nomenclatura

```python
# Variáveis e funções: snake_case
def processar_gasto(valor_gasto):
    categoria_detectada = categorizar_automaticamente(valor_gasto)
    return categoria_detectada

# Classes: PascalCase
class GerenciadorGastos:
    def __init__(self):
        self.total_gastos = 0

# Constantes: UPPER_SNAKE_CASE
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MAX_RETRIES = 3

# Arquivos: snake_case.py
# bot_completo.py, dashboard_completo.py
```

### Docstrings

Utilizamos o formato **Google Style**:

```python
def calcular_media_movel(gastos: List[Dict], janela: int = 7) -> float:
    """Calcula média móvel dos gastos.
    
    Args:
        gastos: Lista de dicionários com dados dos gastos
        janela: Tamanho da janela para cálculo (default: 7)
        
    Returns:
        Valor da média móvel calculada
        
    Raises:
        ValueError: Se a janela for menor que 1
        
    Example:
        >>> gastos = [{'valor': 100}, {'valor': 200}]
        >>> calcular_media_movel(gastos, 2)
        150.0
    """
    if janela < 1:
        raise ValueError("Janela deve ser maior que 0")
    
    # Implementação...
    return media_calculada
```

---

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── __init__.py
├── test_bot.py              # Testes do bot
├── test_dashboard.py        # Testes do dashboard
├── test_analytics.py        # Testes de analytics
├── test_integration.py      # Testes de integração
└── fixtures/
    ├── sample_data.json     # Dados de teste
    └── mock_responses.py    # Mocks para APIs
```

### Executando Testes

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=. --cov-report=html

# Testes específicos
pytest tests/test_bot.py

# Testes com verbose
pytest -v

# Testes em paralelo
pytest -n auto
```

### Exemplo de Teste

```python
# tests/test_bot.py
import pytest
from unittest.mock import Mock, patch
from bot_completo import extrair_valor, categorizar

class TestBotFunctions:
    """Testes para funções principais do bot."""
    
    def test_extrair_valor_formato_simples(self):
        """Testa extração de valor em formato simples."""
        assert extrair_valor("mercado 50") == 50.0
        assert extrair_valor("uber 25.50") == 25.5
        assert extrair_valor("R$ 100") == 100.0
    
    def test_extrair_valor_formato_complexo(self):
        """Testa extração de valor em formatos complexos."""
        assert extrair_valor("R$ 1.250,75") == 1250.75
        assert extrair_valor("1,500.00") == 1500.0
    
    def test_categorizar_alimentacao(self):
        """Testa categorização de gastos com alimentação."""
        assert categorizar("mercado") == "alimentação"
        assert categorizar("supermercado") == "alimentação"
        assert categorizar("restaurante") == "alimentação"
    
    @patch('bot_completo.sheet')
    def test_salvar_gasto_async(self, mock_sheet):
        """Testa salvamento assíncrono de gastos."""
        mock_sheet.append_row.return_value = True
        
        # Implementar teste...
        assert True  # Placeholder

    def test_categorizar_caso_nao_encontrado(self):
        """Testa categorização quando não encontra categoria."""
        assert categorizar("item_desconhecido") == "outros"
```

### Coverage Mínimo

- **Cobertura mínima**: 80%
- **Funções críticas**: 95%
- **Novas features**: 90%

---

## 📦 Processo de Contribuição

### 1. Workflow Git

```bash
# Sincronizar com upstream
git fetch upstream
git checkout main
git merge upstream/main

# Criar branch para feature
git checkout -b feature/nome-da-feature

# Ou para bugfix
git checkout -b fix/nome-do-bug
```

### 2. Convenção de Commits

Utilizamos **Conventional Commits**:

```bash
# Tipos de commit
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação
refactor: refatoração
test: testes
chore: manutenção

# Exemplos
git commit -m "feat: adiciona análise de ROI para investimentos"
git commit -m "fix: corrige cálculo de média móvel"
git commit -m "docs: atualiza README com novas instruções"
git commit -m "test: adiciona testes para categorização automática"
```

### 3. Pull Request

**Template de PR**:

```markdown
## 📝 Descrição

Breve descrição das mudanças implementadas.

## 🔧 Tipo de Mudança

- [ ] Bug fix (mudança que corrige um problema)
- [ ] Nova feature (mudança que adiciona funcionalidade)
- [ ] Breaking change (mudança que quebra compatibilidade)
- [ ] Documentação

## 🧪 Testes

- [ ] Testes passando localmente
- [ ] Novos testes adicionados
- [ ] Coverage mantido/melhorado

## 📋 Checklist

- [ ] Código segue padrões do projeto
- [ ] Self-review realizado
- [ ] Documentação atualizada
- [ ] Sem conflitos com main

## 📸 Screenshots (se aplicável)

## 🔗 Issues Relacionadas

Closes #123
```

### 4. Code Review

**Critérios de Aprovação**:
- ✅ Código limpo e bem documentado
- ✅ Testes passando
- ✅ Coverage adequado
- ✅ Performance não degradada
- ✅ Segurança mantida
- ✅ Documentação atualizada

---

## 🐛 Reportando Bugs

### Template de Bug Report

```markdown
**Descrição do Bug**
Descrição clara e concisa do problema.

**Passos para Reproduzir**
1. Vá para '...'
2. Clique em '....'
3. Role para baixo até '....'
4. Veja o erro

**Comportamento Esperado**
Descrição do que deveria acontecer.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente:**
 - OS: [e.g. iOS]
 - Browser [e.g. chrome, safari]
 - Versão [e.g. 22]

**Contexto Adicional**
Qualquer outra informação relevante.
```

---

## 💡 Sugerindo Features

### Template de Feature Request

```markdown
**A feature está relacionada a um problema?**
Descrição clara do problema. Ex: Estou sempre frustrado quando [...]

**Descreva a solução desejada**
Descrição clara e concisa do que você quer que aconteça.

**Descreva alternativas consideradas**
Descrição de soluções ou features alternativas consideradas.

**Contexto adicional**
Qualquer outro contexto ou screenshots sobre a feature.
```

---

## 📖 Documentação

### Atualizando Documentação

- **README.md**: Informações gerais e setup
- **API_DOCUMENTATION.md**: Documentação da API
- **ARCHITECTURE.md**: Arquitetura do sistema
- **Docstrings**: Documentação inline do código

### Padrões de Documentação

```markdown
# Título Principal

## Seção

### Subseção

**Negrito para destaque**
*Itálico para ênfase*

```python
# Blocos de código com syntax highlighting
def exemplo():
    return "código"
```

| Coluna 1 | Coluna 2 |
|----------|----------|
| Valor 1  | Valor 2  |
```

---

## 🏆 Reconhecimento

### Contributors

Todos os contribuidores são reconhecidos no README principal e recebem:

- 🏷️ Badge de contributor
- 📝 Menção nos release notes
- 🎉 Destaque nas redes sociais

### Níveis de Contribuição

- **🥉 Bronze**: 1-5 PRs aceitos
- **🥈 Silver**: 6-15 PRs aceitos
- **🥇 Gold**: 16+ PRs aceitos
- **💎 Diamond**: Maintainer status

---

## 📞 Suporte

### Canais de Comunicação

- 🐛 **Issues**: Para bugs e features
- 💬 **Discussions**: Para dúvidas gerais
- 📧 **Email**: Para questões privadas
- 💬 **Discord**: Para chat em tempo real (futuro)

### Tempo de Resposta

- **Issues críticas**: 24h
- **PRs**: 48-72h
- **Discussions**: 24-48h
- **Email**: 48-72h

---

## 📜 Código de Conduta

### Nossos Compromissos

- 🤝 Ambiente acolhedor e inclusivo
- 🎯 Foco em colaboração construtiva
- 📚 Compartilhamento de conhecimento
- 🚀 Crescimento mútuo

### Comportamentos Esperados

- ✅ Linguagem respeitosa e inclusiva
- ✅ Feedback construtivo
- ✅ Foco no que é melhor para a comunidade
- ✅ Empatia com outros membros

### Comportamentos Inaceitáveis

- ❌ Linguagem ou imagens sexualizadas
- ❌ Trolling, insultos ou ataques pessoais
- ❌ Assédio público ou privado
- ❌ Publicar informações privadas sem permissão

---

**Obrigado por contribuir! 🚀**

---

**Mantido por**: Lucas Lima - Senior Software Engineer  
**Última atualização**: Dezembro 2024  
**Versão**: 1.0.0