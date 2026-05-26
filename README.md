# mundo-invest-api

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
        "id": "750893428"
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
    "card_id": "750893428",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-25T12:00:00Z"
  }'
```

**Response 200:**
```json
{
  "data": {
    "updateFieldsValues": {
      "card": {
        "id": "750893428",
        "fields": [
          { "name": "Status", "value": "Processado" },
          { "name": "Prioridade", "value": "prioridade_alta" }
        ]
      },
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

---