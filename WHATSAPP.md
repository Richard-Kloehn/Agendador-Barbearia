# 📱 Como Funciona o Sistema de WhatsApp

## 🔄 Fluxo Completo do WhatsApp

### 1️⃣ AGENDAMENTO INICIAL
Quando um cliente faz um agendamento no site:
```
Cliente agenda → Sistema salva no banco → (Opcional) Envia confirmação imediata
```

**Mensagem de Confirmação Imediata (Opcional):**
```
✅ Agendamento confirmado!

Olá [Nome do Cliente],

Seu horário foi agendado com sucesso:

📅 [Data e Hora]

Você receberá um lembrete 24 horas antes.

Obrigado! ✂️
```

---

### 2️⃣ LEMBRETE AUTOMÁTICO (24h Antes)

O sistema possui um **scheduler** (APScheduler) que:
- Roda automaticamente **a cada 1 hora**
- Verifica agendamentos para o **dia seguinte**
- Envia lembretes para quem ainda **não recebeu**

**Mensagem de Lembrete:**
```
Olá [Nome]! 👋

Este é um lembrete do seu agendamento na Navalha's Barber Club:

📅 Data: [DD/MM/YYYY às HH:MM]

Por favor, confirme sua presença acessando:
[Link Único de Confirmação]

Se não puder comparecer, cancele pelo mesmo link para liberar o horário.

Caso não responda, seu horário será automaticamente confirmado.

Obrigado! ✂️
```

---

### 3️⃣ CONFIRMAÇÃO PELO CLIENTE

O cliente clica no link e vê uma página com 2 botões:

**Opção A: CONFIRMAR ✅**
```
Status muda para: "confirmado"
confirmado_cliente = True
```

**Opção B: CANCELAR ❌**
```
Status muda para: "cancelado"
Horário fica disponível para outros
```

**Opção C: NÃO RESPONDE ⏰**
```
Após timeout (você define), automaticamente:
Status: "confirmado"
```

---

## ⚙️ CONFIGURAÇÃO DO TWILIO

### Passo 1: Criar Conta Twilio

1. Acesse: https://www.twilio.com/try-twilio
2. Crie uma conta gratuita
3. Você ganha **crédito grátis** para testes!

### Passo 2: Configurar WhatsApp Sandbox (GRÁTIS para Testes)

1. No Twilio Console, vá em:
   ```
   Messaging → Try it out → Send a WhatsApp message
   ```

2. Você verá um número e uma mensagem como:
   ```
   join [código-único]
   ```

3. **Envie essa mensagem do seu WhatsApp** para o número mostrado

4. Pronto! Seu WhatsApp está conectado ao sandbox

### Passo 3: Pegar as Credenciais

No Twilio Console, copie:

```
Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Auth Token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Passo 4: Configurar no Sistema

Edite o arquivo `.env`:

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
BASE_URL=http://localhost:5000
```

**⚠️ IMPORTANTE:** Para produção, use sua URL real:
```bash
BASE_URL=https://seu-site.com
```

### Passo 5: Reiniciar o Servidor

```bash
# Pare o servidor (Ctrl+C)
# Execute novamente:
python app.py
```

---

## 🧪 TESTAR O WHATSAPP

### Teste 1: Sandbox (Desenvolvimento)

**Limitações do Sandbox:**
- ✅ Grátis
- ✅ Ideal para testes
- ❌ Só envia para números previamente aprovados
- ❌ Cada pessoa precisa enviar "join código"
- ❌ Aparece "via Twilio Sandbox" nas mensagens

**Como testar:**
1. Configure conforme acima
2. Envie "join código" do seu WhatsApp
3. Crie um agendamento para amanhã
4. Aguarde ou force o envio (modifique o scheduler)

### Teste 2: Forçar Envio Imediato (Para Testes)

Edite temporariamente `app.py` para testar agora:

```python
# Linha ~35, mude de:
amanha = datetime.now() + timedelta(days=1)

# Para:
amanha = datetime.now()  # Envia para agendamentos de hoje
```

---

## 💰 PRODUÇÃO (Número Real)

### Opção 1: Número Twilio com WhatsApp

**Custos aproximados:**
- Número dos EUA: ~$1/mês
- Cada mensagem: ~$0.005 USD
- Exemplo: 1000 mensagens/mês = ~$6 USD

**Como configurar:**
1. Compre um número no Twilio
2. Ative WhatsApp Business API
3. Aguarde aprovação (1-2 dias)
4. Use o novo número no `.env`

### Opção 2: Alternativas Mais Baratas

**Zenvia (Brasil):**
- Planos a partir de R$ 50/mês
- Melhor suporte em português
- https://www.zenvia.com

**TotalVoice:**
- Plataforma brasileira
- Preços competitivos
- https://www.totalvoice.com.br

---

## 🔧 PERSONALIZAR MENSAGENS

Edite `services/whatsapp_service.py`:

```python
# Mensagem de lembrete (linha ~25)
mensagem = f"""
Fala, {agendamento.nome_cliente}! 😎

Lembra do seu horário na Navalha's? 💈

📅 {data_formatada}

Confirma aí: {url_confirmacao}

Tmj! 🔥
""".strip()
```

---

## 📊 COMO O SCHEDULER FUNCIONA

### Código no app.py (linhas 30-55):

```python
scheduler = BackgroundScheduler()

def enviar_lembretes():
    # Busca agendamentos para amanhã
    amanha = datetime.now() + timedelta(days=1)
    
    # Filtra: amanhã + não enviou + confirmado
    agendamentos = Agendamento.query.filter(
        data para amanhã,
        lembrete_enviado == False,
        status == 'confirmado'
    ).all()
    
    # Envia para cada um
    for agendamento in agendamentos:
        enviar_lembrete_whatsapp(agendamento)
        agendamento.lembrete_enviado = True
        db.session.commit()

# Roda a cada 1 hora
scheduler.add_job(func=enviar_lembretes, trigger="interval", hours=1)
scheduler.start()
```

**O que acontece:**
1. ⏰ A cada hora, o sistema acorda
2. 🔍 Busca agendamentos para amanhã
3. 📱 Envia WhatsApp para quem ainda não recebeu
4. ✅ Marca como "lembrete_enviado = True"
5. 💤 Volta a dormir por 1 hora

---

## 🚀 MODO PRODUÇÃO

### Deploy no Render/Railway:

O scheduler funciona automaticamente! Apenas configure:

**Variáveis de Ambiente no Render:**
```
TWILIO_ACCOUNT_SID=seu_sid
TWILIO_AUTH_TOKEN=seu_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+seu_numero
BASE_URL=https://seu-app.onrender.com
```

---

## ❓ FAQ WhatsApp

### P: Preciso pagar para testar?
**R:** Não! O Sandbox é 100% grátis.

### P: Quantos números posso testar no Sandbox?
**R:** Ilimitados, mas cada um precisa enviar "join código".

### P: O cliente precisa ter o Twilio?
**R:** Não! O cliente só usa o WhatsApp normal dele.

### P: Funciona com WhatsApp Business?
**R:** Sim, funciona perfeitamente!

### P: E se eu não configurar o Twilio?
**R:** O sistema funciona normalmente, só não envia mensagens. Você verá avisos no console.

### P: Posso usar meu número pessoal?
**R:** Não diretamente. Precisa de um número Twilio ou serviço similar.

### P: Existe alternativa gratuita?
**R:** Para produção, não. Mas pode usar API do WhatsApp Business (complexo) ou Telegram (mais simples).

---

## 🎯 RESUMO RÁPIDO

### Para Testar (GRÁTIS):
1. Criar conta Twilio
2. Ativar WhatsApp Sandbox
3. Enviar "join código" do seu WhatsApp
4. Configurar .env
5. Reiniciar app
6. Testar!

### Para Produção:
1. Comprar número Twilio (~$1/mês)
2. Ativar WhatsApp Business API
3. Configurar número no .env
4. Deploy no Render/Railway
5. Funciona! 🎉

---

## 📞 SUPORTE

**Dúvidas sobre Twilio:**
- Docs: https://www.twilio.com/docs/whatsapp
- Suporte: https://support.twilio.com

**Problemas no código:**
- Verifique logs do app
- Cheque credenciais no .env
- Teste com curl/Postman primeiro

---

**💡 DICA PROFISSIONAL:**

Para começar, **não ative o WhatsApp**. Use o sistema sem ele:
- ✅ Salva todos os agendamentos
- ✅ Clientes agendam normalmente
- ✅ Você controla tudo no admin
- 📱 Depois ativa o WhatsApp quando sentir necessidade

**O sistema é completo e funcional mesmo sem WhatsApp!** 🎉
