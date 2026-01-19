# Atualização: Sistema de Horários por Barbeiro

## Mudanças Implementadas

### 1. **Renomeação da Seção**
- ✅ "Configurações" foi renomeado para "Horários" no painel admin
- ✅ O ícone e o menu lateral foram atualizados

### 2. **Horários Individuais por Barbeiro**
Agora cada barbeiro tem seus próprios horários de trabalho configuráveis:

- **Seleção de Barbeiro**: Escolha o barbeiro para configurar seus horários
- **Dias da Semana**: Marque quais dias o barbeiro trabalha
- **Horários**: Configure início e fim para cada dia
- **Intervalo de Almoço**: Configure o intervalo de almoço específico de cada dia
- **Flexibilidade**: Cada barbeiro pode ter horários diferentes em dias diferentes

### 3. **Horários Especiais Atualizados**
Os horários especiais agora suportam:
- **Todos os Barbeiros**: Configure um horário especial que afeta todos
- **Barbeiro Específico**: Configure horário especial apenas para um barbeiro
- **Exemplo**: "Feriado" pode afetar todos, mas "Dia de folga" pode ser individual

### 4. **Banco de Dados**

#### Nova Tabela: `horarios_barbeiros`
- `barbeiro_id`: ID do barbeiro
- `dia_semana`: 0=Domingo, 1=Segunda, ..., 6=Sábado
- `horario_inicio`: Horário de início (ex: "09:00")
- `horario_fim`: Horário de fim (ex: "18:00")
- `intervalo_almoco_inicio`: Início do almoço (opcional)
- `intervalo_almoco_fim`: Fim do almoço (opcional)
- `ativo`: Se o horário está ativo

#### Tabela Atualizada: `horarios_especiais`
- **Novo campo**: `barbeiro_id` (pode ser NULL para "todos")
- Agora mostra o nome do barbeiro na listagem

### 5. **Lógica de Horários Disponíveis**
O sistema agora:
1. Verifica horários especiais específicos do barbeiro
2. Se não houver, verifica horários especiais para todos
3. Se não houver, usa os horários configurados do barbeiro
4. Retorna lista vazia se o barbeiro não trabalha naquele dia

### 6. **Migração Automática**
- ✅ Script `migrar_horarios_barbeiros.py` executado
- ✅ Horários padrão criados para todos os barbeiros existentes
- ✅ Baseado nas configurações globais anteriores

## Como Usar

### Configurar Horários de um Barbeiro:
1. Acesse o painel admin
2. Clique em "Horários" no menu lateral
3. Selecione um barbeiro no dropdown
4. Marque os dias que ele trabalha
5. Configure os horários para cada dia
6. Configure intervalos de almoço (opcional)
7. Clique em "Salvar Horários"

### Adicionar Horário Especial:
1. Na seção "Horários Especiais"
2. Selecione um barbeiro ou deixe em branco para "Todos"
3. Escolha a data
4. Adicione uma descrição (ex: "Feriado", "Horário Reduzido")
5. Configure horários de abertura e fechamento
6. Configure almoço (opcional)
7. Clique em "Adicionar"

## Exemplos de Uso

### Exemplo 1: Barbeiro com Horários Diferentes
```
Bryan - Segunda a Sexta: 09:00-19:00 (Almoço: 12:00-13:00)
Bryan - Sábado: 08:00-14:00 (Sem almoço)
Bryan - Domingo: Não trabalha
```

### Exemplo 2: Horário Especial Individual
```
Data: 25/12/2025
Barbeiro: Felipe
Descrição: Natal - Trabalhando meio período
Horário: 08:00-12:00
```

### Exemplo 3: Horário Especial para Todos
```
Data: 01/01/2026
Barbeiro: (Todos os Barbeiros)
Descrição: Ano Novo - Fechado
(Não adicione horários de abertura/fechamento para dia fechado)
```

## Notas Técnicas

### Endpoints Criados:
- `GET /admin/horarios-barbeiro/<barbeiro_id>` - Retorna horários do barbeiro
- `POST /admin/horarios-barbeiro/<barbeiro_id>` - Salva horários do barbeiro

### Endpoints Atualizados:
- `POST /admin/horarios-especiais` - Agora aceita `barbeiro_id`
- `GET /admin/horarios-especiais` - Retorna `barbeiro_nome` nos resultados

### Compatibilidade:
- ✅ Sistema anterior de configuração global mantido no banco
- ✅ Agendamentos existentes não são afetados
- ✅ Horários especiais antigos continuam funcionando

## Próximos Passos Recomendados

1. **Configure os horários de cada barbeiro** no painel admin
2. **Teste o agendamento** no site principal
3. **Ajuste conforme necessário** os horários e intervalos
4. **Configure horários especiais** para feriados futuros
