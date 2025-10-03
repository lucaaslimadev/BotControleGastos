# 📡 API Documentation - Expense Tracker Bot

## 🎯 Visão Geral da API

A API RESTful do Expense Tracker Bot fornece endpoints para integração com o dashboard web e futuras integrações de terceiros.

**Base URL**: `http://localhost:8000` (desenvolvimento) | `https://your-domain.com` (produção)

**Versão**: `v1.0`  
**Formato**: `JSON`  
**Autenticação**: Não requerida (single-user)

---

## 📊 Endpoints Principais

### 1. 📈 Dados Completos do Dashboard

```http
GET /api/complete-data
```

**Descrição**: Retorna todos os dados necessários para renderização do dashboard com analytics avançados.

**Parâmetros Query**:
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `periodo` | string | Não | `atual`, `anterior`, `ano` (default: `atual`) |

**Exemplo de Requisição**:
```bash
curl -X GET "http://localhost:8000/api/complete-data?periodo=atual"
```

**Resposta de Sucesso** (200):
```json
{
  "gastoAtual": 2450.75,
  "mediaMovel": 2200.50,
  "projecao": 2800.00,
  "economiaPossivel": 367.61,
  "categorias": {
    "Alimentação": 850.30,
    "Transporte": 420.15,
    "Saúde": 180.00,
    "Lazer": 300.50,
    "Casa": 699.80
  },
  "evolucaoMensal": {
    "labels": ["Nov/23", "Dez/23", "Jan/24", "Fev/24", "Mar/24"],
    "values": [1800.00, 2100.50, 1950.75, 2300.20, 2450.75]
  },
  "gastosPorDia": [120.50, 180.30, 200.15, 190.80, 220.40, 350.60, 280.90],
  "tendencia": {
    "labels": ["01/12", "02/12", "03/12", "04/12", "05/12"],
    "gastos": [85.50, 120.30, 95.80, 180.20, 110.40],
    "media": [85.50, 102.90, 100.53, 120.45, 118.44]
  },
  "insights": {
    "categoriaCresceu": "Transporte cresceu 15.2% este mês",
    "diaCaro": "Sábado, 15/12/2024 - R$ 350.60",
    "dicaEconomia": "Reduza 15% dos gastos em Alimentação e economize R$ 127.55",
    "padraoGastos": "Você gasta mais nas Sextas. Planeje atividades mais econômicas neste dia."
  },
  "planilhaLink": "https://docs.google.com/spreadsheets/d/SHEET_ID/edit",
  "changeAtual": 12.5,
  "changeMedia": -2.3,
  "changeProjecao": 8.7,
  "changeEconomia": 15.0
}
```

**Códigos de Erro**:
- `500`: Erro interno do servidor ou falha na conexão com Google Sheets

---

### 2. 🎯 Atualização de Meta Mensal

```http
POST /api/update-meta
```

**Descrição**: Atualiza a meta mensal do usuário.

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "meta": 2500.00
}
```

**Exemplo de Requisição**:
```bash
curl -X POST "http://localhost:8000/api/update-meta" \
  -H "Content-Type: application/json" \
  -d '{"meta": 2500.00}'
```

**Resposta de Sucesso** (200):
```json
{
  "success": true,
  "message": "Meta atualizada com sucesso",
  "novaMeta": 2500.00
}
```

---

### 3. 📄 Exportação de Relatório PDF

```http
GET /api/export-pdf
```

**Descrição**: Gera e retorna um relatório financeiro em PDF.

**Parâmetros Query**:
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `periodo` | string | Não | `mes`, `trimestre`, `ano` (default: `mes`) |

**Exemplo de Requisição**:
```bash
curl -X GET "http://localhost:8000/api/export-pdf?periodo=mes" \
  --output relatorio_gastos.pdf
```

**Resposta de Sucesso** (200):
- **Content-Type**: `application/pdf`
- **Content-Disposition**: `attachment; filename="relatorio_gastos_12_2024.pdf"`

**Estrutura do PDF**:
```
📄 Relatório de Gastos - Dezembro/2024
├── 📊 Resumo Executivo
│   ├── Total do mês: R$ 2.450,75
│   ├── Quantidade de gastos: 45
│   └── Gerado em: 15/12/2024 às 14:30
├── 📈 Análise por Categoria
├── 📅 Gastos Detalhados (últimos 20)
└── 💡 Insights e Recomendações
```

---

### 4. 💾 Backup de Dados

```http
GET /api/backup
```

**Descrição**: Gera backup completo dos dados em formato JSON.

**Exemplo de Requisição**:
```bash
curl -X GET "http://localhost:8000/api/backup" \
  --output backup_gastos.json
```

**Resposta de Sucesso** (200):
```json
{
  "data_backup": "2024-12-15T14:30:00.000Z",
  "total_gastos": 156,
  "metadata": {
    "versao_sistema": "1.0.0",
    "formato_backup": "json_v1",
    "usuario": "single_user"
  },
  "gastos": [
    {
      "Data": "15/12/2024",
      "Descrição": "Mercado",
      "Valor": "150.00",
      "Categoria": "alimentação"
    },
    {
      "Data": "15/12/2024",
      "Descrição": "Uber",
      "Valor": "25.50",
      "Categoria": "transporte"
    }
  ],
  "estatisticas": {
    "total_por_categoria": {
      "alimentação": 850.30,
      "transporte": 420.15,
      "saúde": 180.00
    },
    "periodo_dados": {
      "inicio": "01/01/2024",
      "fim": "15/12/2024"
    }
  }
}
```

---

## 🔧 Endpoints de Sistema

### 5. ❤️ Health Check

```http
GET /api/health
```

**Descrição**: Verifica o status do sistema e dependências.

**Resposta de Sucesso** (200):
```json
{
  "status": "healthy",
  "timestamp": "2024-12-15T14:30:00.000Z",
  "version": "1.0.0",
  "dependencies": {
    "google_sheets": {
      "status": "connected",
      "response_time": "120ms"
    },
    "telegram_api": {
      "status": "active",
      "last_update": "2024-12-15T14:29:45.000Z"
    }
  },
  "metrics": {
    "uptime": "99.9%",
    "total_requests": 1547,
    "avg_response_time": "85ms"
  }
}
```

### 6. 📊 Métricas do Sistema

```http
GET /api/metrics
```

**Descrição**: Retorna métricas detalhadas do sistema.

**Resposta de Sucesso** (200):
```json
{
  "performance": {
    "requests_per_minute": 12.5,
    "avg_response_time": "85ms",
    "error_rate": "0.2%"
  },
  "usage": {
    "total_users": 1,
    "gastos_registrados_hoje": 8,
    "consultas_dashboard": 23
  },
  "resources": {
    "memory_usage": "45MB",
    "cpu_usage": "12%",
    "disk_usage": "2.1GB"
  }
}
```

---

## 🚨 Tratamento de Erros

### Códigos de Status HTTP

| Código | Descrição | Exemplo |
|--------|-----------|---------|
| `200` | Sucesso | Dados retornados com sucesso |
| `400` | Bad Request | Parâmetros inválidos |
| `404` | Not Found | Endpoint não encontrado |
| `500` | Internal Server Error | Erro na conexão com Google Sheets |
| `503` | Service Unavailable | Sistema em manutenção |

### Formato de Erro Padrão

```json
{
  "error": true,
  "code": "SHEETS_CONNECTION_ERROR",
  "message": "Falha na conexão com Google Sheets",
  "details": "Verifique as credenciais e permissões",
  "timestamp": "2024-12-15T14:30:00.000Z",
  "request_id": "req_123456789"
}
```

---

## 🔒 Segurança & Rate Limiting

### Rate Limiting

| Endpoint | Limite | Janela |
|----------|--------|--------|
| `/api/complete-data` | 60 req/min | Por IP |
| `/api/export-pdf` | 10 req/min | Por IP |
| `/api/backup` | 5 req/min | Por IP |
| Outros endpoints | 100 req/min | Por IP |

### Headers de Rate Limiting

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640123456
```

---

## 📝 Exemplos de Integração

### JavaScript (Frontend)

```javascript
// Carregar dados do dashboard
async function loadDashboardData() {
  try {
    const response = await fetch('/api/complete-data?periodo=atual');
    const data = await response.json();
    
    // Atualizar gráficos
    updateCharts(data);
    
  } catch (error) {
    console.error('Erro ao carregar dados:', error);
  }
}

// Atualizar meta
async function updateMeta(novaMeta) {
  try {
    const response = await fetch('/api/update-meta', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ meta: novaMeta })
    });
    
    const result = await response.json();
    console.log('Meta atualizada:', result);
    
  } catch (error) {
    console.error('Erro ao atualizar meta:', error);
  }
}
```

### Python (Cliente)

```python
import requests
import json

class ExpenseTrackerAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_dashboard_data(self, periodo="atual"):
        """Obtém dados completos do dashboard"""
        response = requests.get(
            f"{self.base_url}/api/complete-data",
            params={"periodo": periodo}
        )
        return response.json()
    
    def update_meta(self, meta_valor):
        """Atualiza meta mensal"""
        response = requests.post(
            f"{self.base_url}/api/update-meta",
            json={"meta": meta_valor}
        )
        return response.json()
    
    def export_pdf(self, periodo="mes"):
        """Exporta relatório PDF"""
        response = requests.get(
            f"{self.base_url}/api/export-pdf",
            params={"periodo": periodo}
        )
        
        if response.status_code == 200:
            with open("relatorio.pdf", "wb") as f:
                f.write(response.content)
            return True
        return False

# Uso
api = ExpenseTrackerAPI()
data = api.get_dashboard_data("atual")
print(f"Gasto atual: R$ {data['gastoAtual']:.2f}")
```

---

## 🔮 Roadmap da API

### Versão 1.1 (Q1 2025)
- [ ] **Autenticação JWT**: Multi-user support
- [ ] **WebSocket**: Real-time updates
- [ ] **GraphQL**: Query flexibility
- [ ] **API Versioning**: Backward compatibility

### Versão 2.0 (Q2 2025)
- [ ] **OpenAPI 3.0**: Documentação interativa
- [ ] **Webhooks**: Event notifications
- [ ] **Bulk Operations**: Batch processing
- [ ] **Advanced Filtering**: Complex queries

---

**Documentação mantida por**: Lucas Lima - Senior Backend Developer  
**Última atualização**: Dezembro 2024  
**Versão da API**: 1.0.0