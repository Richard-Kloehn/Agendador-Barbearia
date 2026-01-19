# 🚀 GUIA RÁPIDO DE TESTE - WhatsApp

## ✅ Sistema Pronto!

Todos os telefones foram alterados para: **47991557386**

## 📝 Como Testar Agora

### 1️⃣ Inicie o Sistema

```bash
python app.py
```

### 2️⃣ Na Primeira Execução

- O Chrome abrirá automaticamente
- Escaneie o QR Code do WhatsApp Web com seu celular
- A sessão ficará salva (não precisa escanear novamente)

### 3️⃣ Criar Agendamentos de Teste

Acesse: `http://localhost:5000`

**Crie um agendamento para AMANHÃ no mesmo horário** (ou próximo)

Exemplo:
- Se agora são 14:30 do dia 18/01
- Crie para dia 19/01 às 14:30

Isso fará o sistema enviar o lembrete em ~1 hora!

### 4️⃣ Aguarde o Envio

O sistema verifica **a cada 1 hora** e envia para agendamentos que faltam 23-24h

**Quer testar IMEDIATAMENTE?** Veja a seção "Teste Imediato" abaixo.

## ⚡ TESTE IMEDIATO (Opcional)

Se quiser testar AGORA sem esperar:

### Opção 1: Script de Teste Manual

```bash
python test_whatsapp_automation.py
```

Escolha opção 1, digite seu número e uma mensagem de teste.

### Opção 2: Forçar Envio no Sistema

Crie um arquivo `testar_envio_agora.py`:

```python
from app import app
from database import db
from models import Agendamento
from services.whatsapp_service import enviar_lembrete_whatsapp

with app.app_context():
    # Pega o primeiro agendamento
    agendamento = Agendamento.query.first()
    
    if agendamento:
        print(f"Enviando teste para: {agendamento.nome_cliente}")
        sucesso = enviar_lembrete_whatsapp(agendamento)
        
        if sucesso:
            print("✅ Mensagem enviada com sucesso!")
        else:
            print("❌ Falha ao enviar")
    else:
        print("Nenhum agendamento encontrado")
```

Execute: `python testar_envio_agora.py`

## 📊 Monitorar

### Ver Logs em Tempo Real

```bash
# PowerShell
Get-Content whatsapp_automation.log -Wait -Tail 20
```

### Verificar Status

- ✅ Mensagem enviada: Aparece no log
- ✅ Você recebe no WhatsApp
- ✅ Arquivo `whatsapp_automation.log` registra tudo

## 🎯 O que Esperar

### Primeira Mensagem

Pode demorar ~30 segundos:
1. Inicializa o navegador
2. Faz login no WhatsApp Web
3. Envia a mensagem

### Próximas Mensagens

Mais rápido: ~10 segundos por mensagem

### Limites Ativos

- ✅ Máximo 15 mensagens/hora
- ✅ 8 segundos entre mensagens
- ✅ 60 segundos para o mesmo número

## ⚠️ Problemas Comuns

### "Navegador fecha sozinho"

Normal! O sistema fecha após enviar. Para manter aberto, edite:

```python
# Em whatsapp_service_automation.py
# Comente a linha:
# servico.fechar()
```

### "QR Code não aparece"

1. Delete a pasta `whatsapp_session/`
2. Execute novamente
3. Escaneie o QR Code

### "Mensagem não chega"

1. Verifique o log: `whatsapp_automation.log`
2. Certifique-se que o WhatsApp do celular está online
3. Verifique se o número está correto (47991557386)

## 📱 Teste Completo Recomendado

1. ✅ **Dia 1**: Teste envio manual (`test_whatsapp_automation.py`)
2. ✅ **Dia 2**: Crie agendamento para 24h depois
3. ✅ **Dia 3**: Verifique se o lembrete chegou automaticamente
4. ✅ **Dia 4-7**: Crie vários agendamentos espaçados
5. ✅ **Dia 8+**: Se tudo OK, considere usar com clientes reais

## 🎉 Está Funcionando?

Se recebeu a mensagem personalizada no WhatsApp:

```
Boa tarde, [seu nome]! ✂️

📅 Confirmação de Agendamento

Você tem um horário marcado:
...
```

**🎊 PARABÉNS! Sistema 100% funcional!**

---

**Próximo passo**: Documente por 1 semana para garantir estabilidade antes de usar com clientes reais.
