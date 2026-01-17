# Sistema de Barbeiros e Serviços - Documentação

## 📋 Visão Geral

O sistema foi atualizado para permitir que os clientes escolham **barbeiros** e **serviços** específicos ao fazer um agendamento. Agora o fluxo é:

1. **Dados do cliente** (nome, telefone)
2. **Escolha da data**
3. **Escolha do barbeiro**
4. **Escolha do serviço** (do barbeiro selecionado)
5. **Escolha do horário** (disponível para aquele barbeiro/serviço)
6. **Confirmação**

## 🆕 Novos Recursos

### Backend

#### Novos Models (models.py)

**Barbeiro:**
- `nome`: Nome do barbeiro
- `foto_url`: URL da foto do barbeiro
- `ativo`: Se está ativo
- `ordem`: Ordem de exibição
- Relacionamento many-to-many com Servico

**Servico:**
- `nome`: Nome do serviço
- `descricao`: Descrição do serviço
- `duracao`: Duração em minutos
- `preco`: Preço do serviço
- `ativo`: Se está ativo
- Relacionamento many-to-many com Barbeiro

**Agendamento (atualizado):**
- Adicionado: `barbeiro_id` (FK para Barbeiro)
- Adicionado: `servico_id` (FK para Servico)

#### Novas Rotas API

**Públicas (para clientes):**
- `GET /api/barbeiros` - Lista barbeiros ativos
- `GET /api/servicos` - Lista serviços ativos
- `GET /api/horarios-disponiveis?data=X&barbeiro_id=Y&servico_id=Z` - Horários específicos por barbeiro/serviço

**Admin (gerenciamento):**
- `GET /admin/barbeiros` - Lista todos os barbeiros
- `POST /admin/barbeiros` - Cria novo barbeiro
- `PUT /admin/barbeiros/<id>` - Atualiza barbeiro
- `DELETE /admin/barbeiros/<id>` - Deleta barbeiro
- `GET /admin/servicos` - Lista todos os serviços
- `POST /admin/servicos` - Cria novo serviço
- `PUT /admin/servicos/<id>` - Atualiza serviço
- `DELETE /admin/servicos/<id>` - Deleta serviço

### Frontend

#### Novo Fluxo no index.html

O Step 2 agora contém 3 sub-etapas:
1. Escolher barbeiro (cards com foto)
2. Escolher serviço (cards com nome, descrição, duração e preço)
3. Escolher horário (grid de horários)

#### Novas Funções JavaScript

- `carregarBarbeiros()` - Carrega barbeiros após selecionar data
- `selecionarBarbeiro(barbeiro, elemento)` - Seleciona um barbeiro e carrega seus serviços
- `selecionarServico(servico, elemento)` - Seleciona um serviço e carrega horários
- `buscarHorarios()` - Atualizado para usar barbeiro_id e servico_id

### Mensagens WhatsApp

As mensagens de confirmação e lembrete agora incluem:
- Nome do barbeiro
- Nome do serviço escolhido

Exemplo:
```
✅ Agendamento confirmado!

Olá João,

Seu horário foi agendado com sucesso:

📅 10/06/2024 às 10:00
Barbeiro: Bryan Victor Felippi
Serviço: Corte de Cabelo

Você receberá um lembrete 24 horas antes.

Obrigado! ✂️
```

## 🚀 Como Usar

### 1. Recriar o Banco de Dados

Execute o script de inicialização para criar as novas tabelas:

```bash
python init_db.py
```

Isso irá:
- Criar as tabelas `barbeiros`, `servicos` e `barbeiro_servico`
- Adicionar 3 barbeiros de exemplo
- Adicionar 5 serviços de exemplo
- Associar todos os serviços a todos os barbeiros

### 2. Personalizar Barbeiros

**Via código (init_db.py):** Edite os dados dos barbeiros nas linhas 54-73:
```python
barbeiros = [
    Barbeiro(
        nome="Bryan Victor Felippi",
        foto_url="https://via.placeholder.com/150?text=Bryan",
        ativo=True,
        ordem=1
    ),
    ...
]
```

**Dica:** Substitua as URLs de foto por:
- URLs de imagens hospedadas online
- Caminhos relativos como `/static/img/barbeiro1.jpg`

### 3. Personalizar Serviços

Edite os serviços nas linhas 81-111 do init_db.py:
```python
servicos = [
    Servico(
        nome="Corte de Cabelo",
        descricao="Corte masculino profissional",
        duracao=30,  # minutos
        preco=45.00,  # reais
        ativo=True
    ),
    ...
]
```

### 4. Gerenciar via Admin (futuro)

As rotas de admin já estão prontas. Você precisará criar a interface em `admin.html` para:
- Listar barbeiros e serviços
- Adicionar/Editar/Remover barbeiros
- Adicionar/Editar/Remover serviços
- Associar serviços aos barbeiros
- Upload de fotos dos barbeiros

## 📊 Estrutura de Dados

### Barbeiro
```json
{
  "id": 1,
  "nome": "Bryan Victor Felippi",
  "foto_url": "https://...",
  "ativo": true,
  "ordem": 1,
  "servicos": [...],
  "servicos_ids": [1, 2, 3],
  "servicos_count": 3
}
```

### Servico
```json
{
  "id": 1,
  "nome": "Corte de Cabelo",
  "descricao": "Corte masculino profissional",
  "duracao": 30,
  "preco": 45.00,
  "ativo": true
}
```

### Agendamento
```json
{
  "id": 1,
  "nome_cliente": "João Silva",
  "telefone": "11999998888",
  "data_hora": "2024-06-10T10:00:00",
  "barbeiro_id": 1,
  "servico_id": 1,
  "status": "confirmado",
  "barbeiro": { objeto Barbeiro },
  "servico": { objeto Servico }
}
```

## ⚙️ Configurações Importantes

### Horários Disponíveis

A lógica de horários agora considera:
- **Barbeiro específico**: Cada barbeiro tem sua própria agenda
- **Duração do serviço**: O intervalo entre horários se adapta à duração do serviço
  - Corte (30min) → horários a cada 30min
  - Combo (45min) → horários a cada 45min

Exemplo: Se o serviço dura 45min e a barbearia funciona das 9h às 18h:
```
9:00, 9:45, 10:30, 11:15, 12:00, ...
```

### Associação Barbeiro-Serviço

Por padrão, todos os barbeiros oferecem todos os serviços. Para personalizar:

**No init_db.py:**
```python
# Exemplo: Bryan só faz corte e barba
bryan = Barbeiro.query.filter_by(nome="Bryan Victor Felippi").first()
corte = Servico.query.filter_by(nome="Corte de Cabelo").first()
barba = Servico.query.filter_by(nome="Barba").first()
bryan.servicos = [corte, barba]
db.session.commit()
```

**Via API (futuro):**
```bash
PUT /admin/barbeiros/1
{
  "servicos_ids": [1, 2]  # IDs dos serviços que ele oferece
}
```

## 🔧 Troubleshooting

### Erro "Barbeiro não encontrado"
- Verifique se os barbeiros estão marcados como `ativo=True`
- Execute `python init_db.py` para criar barbeiros

### Erro "Serviço não disponível para o barbeiro"
- O serviço pode não estar associado ao barbeiro
- Verifique a tabela `barbeiro_servico` no banco de dados

### Nenhum horário disponível
- Verifique se o barbeiro tem outros agendamentos
- Confirme a duração do serviço (pode não caber na agenda)
- Verifique os dias de funcionamento da barbearia

## 📝 Próximos Passos

1. ✅ Backend de barbeiros e serviços - **COMPLETO**
2. ✅ Frontend de agendamento atualizado - **COMPLETO**
3. ✅ Mensagens WhatsApp atualizadas - **COMPLETO**
4. ⏳ **Interface Admin para gerenciar barbeiros/serviços** - PENDENTE
5. ⏳ Upload de fotos dos barbeiros - PENDENTE
6. ⏳ Relatórios por barbeiro - PENDENTE

## 💡 Dicas

- Use fotos de qualidade para os barbeiros (150x150px mínimo)
- Escolha durações realistas para os serviços
- Mantenha a lista de serviços enxuta (5-8 serviços)
- Ordene os barbeiros por popularidade usando o campo `ordem`
