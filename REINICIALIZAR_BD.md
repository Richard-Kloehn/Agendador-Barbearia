# 🔄 Como Reinicializar o Banco de Dados

## ⚠️ Importante
Este processo irá **apagar todos os dados** do banco atual, incluindo agendamentos, clientes e configurações.

## Passos para Reinicializar

### 1. Parar o Servidor
Se o servidor estiver rodando, pare-o pressionando `Ctrl+C` no terminal.

### 2. Deletar o Banco de Dados Atual (Opcional)
Para garantir uma inicialização limpa:

**No Windows (PowerShell):**
```powershell
Remove-Item -Path "instance\barbearia.db" -Force
```

**No terminal CMD:**
```cmd
del instance\barbearia.db
```

### 3. Executar o Script de Inicialização
```bash
python init_db.py
```

Você verá:
```
==================================================
🏪 INICIALIZAÇÃO DO SISTEMA DE BARBEARIA
==================================================
🔧 Criando tabelas do banco de dados...
✅ Tabelas criadas!
📝 Criando configuração padrão...
✅ Configuração criada com sucesso!
👨‍💼 Criando barbeiros e serviços...
✅ 3 barbeiros criados!
✅ 5 serviços criados!
✅ Serviços associados aos barbeiros!

❓ Deseja criar agendamentos de exemplo? (s/n):
```

### 4. Criar Agendamentos de Exemplo (Opcional)
- Digite **s** para criar 3 agendamentos de exemplo
- Digite **n** para pular (recomendado em produção)

### 5. Iniciar o Servidor
```bash
python app.py
```

## 📋 Dados Criados Automaticamente

### Configuração da Barbearia
- Nome: Navalha's Barber Club
- Horário: 09:00 - 19:00
- Intervalo almoço: 12:00 - 13:00
- Duração padrão: 30 minutos
- Dias de funcionamento: Segunda a Sábado

### Barbeiros (3)
1. **Bryan Victor Felippi**
   - Foto: Placeholder (substitua pela foto real)
   - Ordem: 1
   - Status: Ativo

2. **Fabricio**
   - Foto: Placeholder (substitua pela foto real)
   - Ordem: 2
   - Status: Ativo

3. **Felipe Soares Santana**
   - Foto: Placeholder (substitua pela foto real)
   - Ordem: 3
   - Status: Ativo

### Serviços (5)
1. **Corte de Cabelo** - R$ 45,00 (30 min)
2. **Barba** - R$ 45,00 (30 min)
3. **Combo (Cabelo + Barba)** - R$ 95,00 (45 min)
4. **Sobrancelha** - R$ 25,00 (15 min)
5. **Pézinho** - R$ 20,00 (15 min)

**Nota:** Todos os serviços são associados a todos os barbeiros por padrão.

## 🎨 Personalizando os Dados

### Alterar Fotos dos Barbeiros
Edite o arquivo `init_db.py` nas linhas 54-73:

```python
barbeiros = [
    Barbeiro(
        nome="Bryan Victor Felippi",
        foto_url="/static/img/bryan.jpg",  # ← Altere aqui
        ativo=True,
        ordem=1
    ),
    # ...
]
```

Coloque as fotos em: `static/img/`

### Alterar Serviços e Preços
Edite o arquivo `init_db.py` nas linhas 81-111:

```python
servicos = [
    Servico(
        nome="Corte de Cabelo",
        descricao="Corte masculino profissional",
        duracao=30,     # ← minutos
        preco=45.00,    # ← reais
        ativo=True
    ),
    # ...
]
```

### Associar Serviços Específicos a Barbeiros
Por padrão, todos os barbeiros fazem todos os serviços. Para personalizar, adicione no final do `init_db.py`:

```python
# Exemplo: Bryan só faz corte e barba
bryan = Barbeiro.query.filter_by(nome="Bryan Victor Felippi").first()
servicos_bryan = Servico.query.filter(
    Servico.nome.in_(['Corte de Cabelo', 'Barba'])
).all()
bryan.servicos = servicos_bryan
db.session.commit()
```

## 🔍 Verificar se Funcionou

### 1. Acessar o Sistema
Abra: http://localhost:5000

### 2. Testar o Fluxo de Agendamento
1. Preencha os dados do cliente
2. Escolha uma data
3. **Deve aparecer os 3 barbeiros**
4. Clique em um barbeiro
5. **Deve aparecer os serviços dele**
6. Clique em um serviço
7. **Deve aparecer os horários disponíveis**

### 3. Verificar o Admin
Acesse: http://localhost:5000/admin-login
- Senha: **123**
- Você deve ver a lista de agendamentos (se criou exemplos)

## 🆘 Problemas Comuns

### Erro: "No such table: barbeiros"
**Solução:** O banco não foi criado. Execute:
```bash
python init_db.py
```

### Erro: "UNIQUE constraint failed"
**Solução:** Já existem dados. Delete o banco antes:
```bash
Remove-Item -Path "instance\barbearia.db" -Force
python init_db.py
```

### Não aparecem barbeiros no site
**Soluções:**
1. Verifique se executou `init_db.py`
2. Abra o console do navegador (F12) e veja se há erros
3. Verifique se o servidor está rodando
4. Teste a API diretamente: http://localhost:5000/api/barbeiros

### Fotos não aparecem
**Soluções:**
1. Se usar URL externa, verifique se está acessível
2. Se usar arquivo local, coloque em `static/img/`
3. Use o caminho correto: `/static/img/nome.jpg`

## 📞 Testando com Agendamento Real

Após reinicializar:

1. Acesse http://localhost:5000
2. Faça um agendamento completo
3. Verifique no admin se aparece:
   - Nome do cliente
   - Barbeiro escolhido
   - Serviço escolhido
   - Horário

## 🔄 Migração de Dados Antigos

Se você já tinha agendamentos e quer mantê-los:

### NÃO delete o banco!

Em vez disso, crie um script de migração:

```python
from app import app
from database import db
from models import Agendamento, Barbeiro, Servico

with app.app_context():
    # Criar barbeiros e serviços (sem apagar nada)
    if Barbeiro.query.count() == 0:
        # ... código de criação
        pass
    
    # Atualizar agendamentos antigos com barbeiro/serviço padrão
    agendamentos_sem_barbeiro = Agendamento.query.filter_by(barbeiro_id=None).all()
    barbeiro_padrao = Barbeiro.query.first()
    servico_padrao = Servico.query.first()
    
    for ag in agendamentos_sem_barbeiro:
        ag.barbeiro_id = barbeiro_padrao.id
        ag.servico_id = servico_padrao.id
    
    db.session.commit()
    print(f"✅ {len(agendamentos_sem_barbeiro)} agendamentos migrados!")
```

Salve como `migrar_agendamentos.py` e execute:
```bash
python migrar_agendamentos.py
```
