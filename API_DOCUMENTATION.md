# 📡 DOCUMENTAÇÃO DA API - Sistema de Agendamento

## 🌐 Base URL
- **Desenvolvimento**: `http://localhost:5000`
- **Produção**: `https://seu-dominio.com`

---

## 🔓 ROTAS PÚBLICAS (Cliente)

### 📅 Agendamentos

#### Criar Agendamento
```http
POST /api/agendar
Content-Type: application/json

{
  "nome_cliente": "João Silva Santos",
  "telefone": "(11) 98765-4321",
  "email": "joao@email.com",  // opcional
  "data_hora": "2026-02-15T14:30:00",
  "barbeiro_id": 1,
  "servico_id": 2,
  "observacoes": "Preferência por degradê",  // opcional
  "sem_whatsapp": false  // opcional, padrão false
}
```

**Resposta (201)**:
```json
{
  "mensagem": "Agendamento criado com sucesso!",
  "agendamento": {...},
  "cliente": {...},
  "lembrete_agendado": true
}
```

**Erros Possíveis**:
- `400` - Dados inválidos (nome incompleto, telefone inválido)
- `409` - Horário já ocupado
- `400` - Barbeiro/serviço não disponível

---

#### Confirmar/Cancelar Agendamento
```http
POST /api/confirmar/<token>
Content-Type: application/json

{
  "acao": "confirmar"  // ou "cancelar"
}
```

**Resposta (200)**:
```json
{
  "mensagem": "Agendamento confirmado com sucesso!"
}
```

**Erros**:
- `404` - Token inválido
- `400` - Cancelamento fora do prazo (menos de 2h)

---

#### Reagendar
```http
POST /api/reagendar/<token>
Content-Type: application/json

{
  "nova_data_hora": "2026-02-16T15:00:00"
}
```

**Validações**:
- Prazo mínimo de 2h (configurável)
- Novo horário deve estar disponível
- Agendamento não pode estar cancelado

**Resposta (200)**:
```json
{
  "mensagem": "Agendamento reagendado com sucesso!",
  "agendamento": {...}
}
```

**Erros**:
- `400` - Fora do prazo mínimo
- `409` - Novo horário já ocupado

---

### ⭐ Avaliação

#### Avaliar Atendimento
```http
POST /api/avaliar/<token>
Content-Type: application/json

{
  "avaliacao": 5,  // 1 a 5
  "comentario": "Excelente atendimento!"  // opcional
}
```

**Validações**:
- Só pode avaliar após o atendimento
- Não pode avaliar duas vezes
- Avaliação deve ser 1-5

**Resposta (200)**:
```json
{
  "mensagem": "Obrigado pela sua avaliação!"
}
```

---

### 📋 Lista de Espera

#### Entrar na Lista
```http
POST /api/lista-espera
Content-Type: application/json

{
  "nome_cliente": "Maria Santos",
  "telefone": "(11) 98888-7777",
  "email": "maria@email.com",  // opcional
  "barbeiro_id": 1,
  "servico_id": 2,
  "data_preferencia": "2026-02-15",
  "horario_preferencia": "14:00",  // opcional
  "observacoes": "Qualquer horário da tarde"  // opcional
}
```

**Resposta (201)**:
```json
{
  "mensagem": "Você foi adicionado à lista de espera! Avisaremos quando houver disponibilidade.",
  "lista_espera": {...}
}
```

---

### 🖼️ Galeria

#### Listar Trabalhos
```http
GET /api/galeria
```

**Resposta (200)**:
```json
{
  "trabalhos": [
    {
      "id": 1,
      "titulo": "Degradê Clássico",
      "descricao": "Corte masculino com degradê baixo",
      "imagem_url": "/static/uploads/corte1.jpg",
      "barbeiro": {...},
      "servico": {...}
    }
  ]
}
```

---

### 🔍 Consultas

#### Buscar Cliente
```http
GET /api/buscar-cliente?termo=João
```

**Resposta (200)**:
```json
{
  "clientes": [
    {
      "id": 1,
      "nome_completo": "João Silva Santos",
      "telefone": "11987654321",
      "total_agendamentos": 5
    }
  ]
}
```

---

#### Listar Barbeiros
```http
GET /api/barbeiros
```

**Resposta (200)**:
```json
{
  "barbeiros": [
    {
      "id": 1,
      "nome": "Bryan Victor",
      "foto_url": "/static/img/barbeiro1.jpg",
      "ativo": true,
      "servicos": [...]
    }
  ]
}
```

---

#### Listar Serviços
```http
GET /api/servicos
```

**Resposta (200)**:
```json
{
  "servicos": [
    {
      "id": 1,
      "nome": "Corte de Cabelo",
      "descricao": "Corte masculino completo",
      "duracao": 30,
      "preco": 45.00,
      "ativo": true
    }
  ]
}
```

---

#### Horários Disponíveis
```http
GET /api/horarios?data=2026-02-15&barbeiro_id=1&servico_id=2
```

**Parâmetros**:
- `data` (obrigatório): YYYY-MM-DD
- `barbeiro_id` (obrigatório)
- `servico_id` (obrigatório)

**Resposta (200)**:
```json
{
  "horarios": ["09:00", "09:30", "10:00", "10:30"]
}
```

---

#### Datas Disponíveis
```http
GET /api/datas-disponiveis?mes=2026-02
```

**Resposta (200)**:
```json
{
  "datas_indisponiveis": ["2026-02-10", "2026-02-17"]
}
```

---

## 🔒 ROTAS ADMIN (Requer Autenticação)

### 📊 Dashboard

#### Estatísticas
```http
GET /admin/estatisticas
```

**Resposta (200)**:
```json
{
  "total_agendamentos": 150,
  "agendamentos_hoje": 12,
  "agendamentos_mes": 89,
  "receita_mes": 3500.00,
  "avaliacoes_media": 4.7,
  "clientes_total": 78
}
```

---

### 📅 Gestão de Agendamentos

#### Listar Agendamentos
```http
GET /admin/agendamentos?data=2026-02-15&status=confirmado
```

**Parâmetros (todos opcionais)**:
- `data`: Filtrar por data
- `status`: confirmado, cancelado, concluido
- `barbeiro_id`: Filtrar por barbeiro

---

#### Criar Agendamento (Admin)
```http
POST /admin/agendamentos
```

Mesmos parâmetros do `/api/agendar`, mas permite:
- Agendar no passado
- Ignorar validações de horário
- Forçar criação

---

#### Atualizar Status
```http
PUT /admin/agendamentos/<id>
Content-Type: application/json

{
  "status": "concluido"
}
```

---

### 📋 Lista de Espera (Admin)

#### Listar
```http
GET /admin/lista-espera?status=aguardando
```

**Status possíveis**: aguardando, notificado, convertido, cancelado

---

#### Notificar Cliente
```http
POST /admin/lista-espera/<id>/notificar
```

Marca como notificado e muda status para "notificado"

---

#### Remover da Lista
```http
DELETE /admin/lista-espera/<id>
```

---

### 👨‍💼 Gestão de Barbeiros

#### Criar Barbeiro
```http
POST /admin/barbeiros
Content-Type: application/json

{
  "nome": "Carlos Mendes",
  "foto_url": "/static/uploads/carlos.jpg",
  "servicos_ids": [1, 2, 3],
  "ordem": 1
}
```

---

#### Atualizar Barbeiro
```http
PUT /admin/barbeiros/<id>
Content-Type: application/json

{
  "nome": "Carlos Mendes Silva",
  "ativo": true,
  "servicos_ids": [1, 2, 3, 4]
}
```

---

#### Deletar Barbeiro
```http
DELETE /admin/barbeiros/<id>
```

Desativa o barbeiro (soft delete)

---

### ✂️ Gestão de Serviços

#### Criar Serviço
```http
POST /admin/servicos
Content-Type: application/json

{
  "nome": "Barba Completa",
  "descricao": "Barba com acabamento",
  "duracao": 20,
  "preco": 30.00
}
```

---

#### Atualizar Serviço
```http
PUT /admin/servicos/<id>
```

---

#### Deletar Serviço
```http
DELETE /admin/servicos/<id>
```

---

### 📅 Horários Especiais

#### Criar Horário Especial
```http
POST /admin/horarios-especiais
Content-Type: application/json

{
  "data": "2026-02-20",
  "barbeiro_id": 1,  // null para todos
  "descricao": "Feriado - Horário Reduzido",
  "horario_abertura": "09:00",
  "horario_fechamento": "14:00"
}
```

---

### 🚫 Dias Fechados

#### Marcar Dia Fechado
```http
POST /admin/dias-indisponiveis
Content-Type: application/json

{
  "data": "2026-02-25",
  "motivo": "Feriado Nacional"
}
```

---

#### Remover Dia Fechado
```http
DELETE /admin/dias-indisponiveis/<id>
```

---

## 🔐 Autenticação Admin

### Login
```http
POST /admin/login
Content-Type: application/json

{
  "senha": "SuaSenhaDoEnv"
}
```

**Resposta (200)**:
```json
{
  "mensagem": "Login realizado com sucesso",
  "redirect": "/admin"
}
```

Session cookie é criado automaticamente

---

### Logout
```http
POST /admin/logout
```

---

## 📝 Headers Comuns

### Para todas as requisições:
```http
Content-Type: application/json
Accept: application/json
```

### Para rotas admin (após login):
```http
Cookie: session=<session_token>
```

---

## ⚡ Rate Limiting

**Limites padrão**:
- 200 requisições por dia
- 50 requisições por hora

**Resposta ao exceder**:
```json
{
  "error": "Rate limit exceeded"
}
```

Status: `429 Too Many Requests`

---

## 🛡️ Validações Implementadas

### Nome
- Mínimo 2 palavras
- Cada parte com mínimo 2 caracteres
- Apenas letras, espaços e acentos

### Telefone
- Formato brasileiro: (XX) XXXXX-XXXX
- 10 ou 11 dígitos
- DDD válido (11-99)

### Email (opcional)
- Formato válido de email
- Sanitizado para prevenir XSS

### Data/Hora
- Não pode ser no passado
- Horário comercial (6h-23h)
- Respeita dias fechados

### Observações
- Máximo 500 caracteres
- Sanitizado (remove HTML/scripts)

---

## 🚨 Códigos de Status HTTP

- `200` - Sucesso
- `201` - Criado com sucesso
- `400` - Erro de validação / dados inválidos
- `401` - Não autenticado (admin)
- `403` - Sem permissão
- `404` - Não encontrado
- `409` - Conflito (horário ocupado)
- `429` - Rate limit excedido
- `500` - Erro interno do servidor

---

## 💡 Exemplos Práticos

### Criar Agendamento Completo
```javascript
const response = await fetch('/api/agendar', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    nome_cliente: 'Pedro Henrique Silva',
    telefone: '(11) 98765-4321',
    data_hora: '2026-02-20T15:30:00',
    barbeiro_id: 1,
    servico_id: 3,
    observacoes: 'Corte social'
  })
});

const data = await response.json();
console.log(data.mensagem);
```

---

### Reagendar
```javascript
const token = 'abc123...';
const response = await fetch(`/api/reagendar/${token}`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    nova_data_hora: '2026-02-21T16:00:00'
  })
});
```

---

### Avaliar Atendimento
```javascript
const token = 'abc123...';
await fetch(`/api/avaliar/${token}`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    avaliacao: 5,
    comentario: 'Excelente profissional!'
  })
});
```

---

**📚 Documentação completa das melhorias: `MELHORIAS_IMPLEMENTADAS.md`**
