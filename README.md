# Mundo Invest API

API interna para gerenciamento de clientes e seus patrimônios investidos, com mapeamento simulado de operações para o Pipefy via GraphQL.

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose

---

## Configuração

```bash
cp .env.example .env
```

Edite o `.env` conforme necessário. Variáveis disponíveis:

| Variável | Descrição |
|---|---|
| `ENV` | Ambiente: `local` ou `prod` |
| `DATABASE_URL` | URL de conexão com o banco (asyncpg para PostgreSQL, aiosqlite para SQLite) |
| `PIPEFY_PIPE_ID` | ID do pipe no Pipefy onde os cards serão criados |
| `PIPEFY_FIELD_ID_NOME_CLIENTE` | `field_id` do campo Nome do Cliente no pipe |
| `PIPEFY_FIELD_ID_EMAIL_CLIENTE` | `field_id` do campo E-mail do Cliente no pipe |
| `PIPEFY_FIELD_ID_TIPO_SOLICITACAO` | `field_id` do campo Tipo de Solicitação no pipe |
| `PIPEFY_FIELD_ID_VALOR_PATRIMONIO` | `field_id` do campo Valor do Patrimônio no pipe |
| `PIPEFY_FIELD_ID_STATUS` | `field_id` do campo Status no pipe |
| `PIPEFY_FIELD_ID_PRIORIDADE` | `field_id` do campo Prioridade no pipe |
| `API_KEY` | Chave de autenticação exigida no header `X-API-Key` |

---

## Execução local

### Com Docker (PostgreSQL)

```bash
docker compose up --build
```

A API estará disponível em `http://localhost:8000`.
A documentação estará em `http://localhost:8000/docs`.

### Sem Docker (SQLite)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Ajuste o DATABASE_URL no .env para SQLite:
# DATABASE_URL=sqlite+aiosqlite:///./mundoinvest.db

uvicorn app.main:app --reload
```


---

## Testes

Os testes usam banco SQLite in-memory.

```bash
# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Rodar todos os testes
pytest

# Rodar com verbose
pytest -v

# Rodar arquivo específico
pytest tests/test_clientes.py -v
pytest tests/test_webhooks.py -v
pytest tests/test_pipefy_client.py -v
```

---

## Endpoints

Todos os endpoints exigem o header `X-API-Key`.

### POST /clientes

Cria um novo cliente e simula o envio de um card ao Pipefy.

```bash
curl -X POST http://localhost:8000/clientes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 76106710fcc3680c23a50adbef5096b843fb7755a77a85b8f2ea9e85f964e86a" \
  -d '{
    "cliente_nome": "João Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250000
  }'
```

**Response 201:**
```json
{
  "data": {
    "createCard": {
      "card": {
        "id": "972452911"
      }
    }
  }
}
```

**Response 409 — e-mail já cadastrado:**
```json
{
  "detail": {
    "error": "conflict",
    "message": "Cliente com e-mail 'joao.silva@example.com' já está cadastrado"
  }
}
```

---

### POST /webhooks/pipefy/card-updated

Simula o recebimento de um webhook do Pipefy quando um card é atualizado. Substitua card_id por um id valido.

```bash
curl -X POST http://localhost:8000/webhooks/pipefy/card-updated \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 76106710fcc3680c23a50adbef5096b843fb7755a77a85b8f2ea9e85f964e86a" \
  -d '{
    "event_id": "evt_123",
    "card_id": "972452911",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-25T12:00:00Z"
  }'
```

**Response 200:**
```json
{
  "data": {
    "updateFieldsValues": {
      "success": true
    }
  }
}
```

**Response 409 — evento duplicado:**
```json
{
  "detail": {
    "error": "conflict",
    "message": "Evento 'evt_123' já foi processado"
  }
}
```

**Response 404 — cliente não encontrado:**
```json
{
  "detail": {
    "error": "not_found",
    "message": "Cliente com e-mail 'joaosilva@example.com' não encontrado"
  }
}
```

**Response 404 — card_id invalido para o cliente:**
```json
{
  "detail": {
    "error": "not_found",
    "message": "Card '580893721' não encontrado para o cliente 'joao.silva@example.com'"
  }
}
```
