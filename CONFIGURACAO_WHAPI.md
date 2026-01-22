# 📱 Guia Completo: Automação WhatsApp com whapi.cloud

## 🎯 Visão Geral

Este sistema agora está integrado com **whapi.cloud**, uma solução profissional de API para WhatsApp que:
- ✅ **Não requer servidor VPS adicional**
- ✅ **Funciona em qualquer hospedagem** (Render, Heroku, Vercel, etc.)
- ✅ **Conexão estável e confiável**
- ✅ **Fácil configuração**
- ✅ **Custos a partir de $0 (plano gratuito)**

---

## 📋 Índice

1. [Criar Conta no whapi.cloud](#1-criar-conta-no-whapicloud)
2. [Configurar Canal WhatsApp](#2-configurar-canal-whatsapp)
3. [Obter Credenciais](#3-obter-credenciais)
4. [Configurar Aplicação](#4-configurar-aplicação)
5. [Testar Integração](#5-testar-integração)
6. [Deploy em Produção](#6-deploy-em-produção)
7. [Solução de Problemas](#7-solução-de-problemas)

---

## 1. 🆕 Criar Conta no whapi.cloud

### Passo 1: Acessar o Site
1. Acesse: https://whapi.cloud/pt/price
2. Escolha um plano:
   - **Free**: Até 100 mensagens/mês (ótimo para testes)
   - **Starter**: R$ 29/mês - 1000 mensagens
   - **Business**: R$ 99/mês - 5000 mensagens

### Passo 2: Criar Conta
1. Clique em **"Começar Agora"** ou **"Sign Up"**
2. Preencha seus dados:
   - Email
   - Senha
   - Nome da empresa
3. Confirme seu email

---

## 2. 📱 Configurar Canal WhatsApp

### Passo 1: Acessar Dashboard
1. Faça login em: https://panel.whapi.cloud
2. Você verá o painel principal

### Passo 2: Criar Novo Canal
1. Clique em **"+ New Channel"** ou **"Criar Canal"**
2. Escolha o tipo: **"WhatsApp Personal"** ou **"WhatsApp Business"**
3. Dê um nome ao canal (ex: "Barbearia - Automação")

### Passo 3: Conectar WhatsApp
1. Um QR Code aparecerá na tela
2. Abra o WhatsApp no seu celular
3. Vá em:
   - **Android**: Menu (3 pontos) → Aparelhos conectados → Conectar aparelho
   - **iPhone**: Configurações → Aparelhos conectados → Conectar aparelho
4. Escaneie o QR Code
5. Aguarde a conexão (geralmente 10-30 segundos)

### ✅ Confirmação
- Quando conectado, você verá: **"Connected"** ou **"Conectado"**
- O status ficará verde

---

## 3. 🔑 Obter Credenciais

### Passo 1: Token da API
1. No painel do whapi.cloud, clique no seu canal
2. Vá em **"Settings"** ou **"Configurações"**
3. Procure por **"API Token"**
4. Clique em **"Show"** ou **"Mostrar"**
5. **Copie o token** (algo como: `MwL8BYl9c3xT4xK5...`)

### Passo 2: Phone ID
1. Na mesma tela de Settings
2. Procure por **"Channel ID"** ou **"Phone ID"**
3. **Copie o ID** (algo como: `5511987654321@c.us`)

### 📝 Anote em um lugar seguro:
```
WHAPI_API_TOKEN=MwL8BYl9c3xT4xK5... (seu token)
WHAPI_PHONE_ID=5511987654321@c.us (seu phone ID)
```

---

## 4. ⚙️ Configurar Aplicação

### Opção A: Arquivo .env (Desenvolvimento Local)

1. Crie um arquivo `.env` na raiz do projeto
2. Cole e preencha:

```env
# WhatsApp via whapi.cloud
WHAPI_API_TOKEN=cole-seu-token-aqui
WHAPI_PHONE_ID=cole-seu-phone-id-aqui
WHAPI_API_URL=https://gate.whapi.cloud

# Banco de Dados (ajuste conforme necessário)
DATABASE_URL=postgresql://usuario:senha@localhost/barbearia

# Segurança
SECRET_KEY=sua-chave-secreta-aqui
```

### Opção B: Variáveis de Ambiente (Produção)

Se você for hospedar em **Render, Heroku, Railway**, etc:

1. Acesse o painel da plataforma
2. Vá em **Environment Variables** ou **Config Vars**
3. Adicione:

| Nome | Valor |
|------|-------|
| `WHAPI_API_TOKEN` | Seu token do whapi.cloud |
| `WHAPI_PHONE_ID` | Seu phone ID |
| `WHAPI_API_URL` | `https://gate.whapi.cloud` |
| `DATABASE_URL` | URL do seu banco de dados |
| `SECRET_KEY` | Chave secreta (mínimo 32 caracteres) |

---

## 5. 🧪 Testar Integração

### Teste 1: Verificar Configuração

Crie um arquivo `testar_whapi.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Verificando configuração...")
print(f"✅ WHAPI_API_TOKEN: {'Configurado' if os.getenv('WHAPI_API_TOKEN') else '❌ NÃO configurado'}")
print(f"✅ WHAPI_PHONE_ID: {'Configurado' if os.getenv('WHAPI_PHONE_ID') else '❌ NÃO configurado'}")
print(f"✅ WHAPI_API_URL: {os.getenv('WHAPI_API_URL', 'https://gate.whapi.cloud')}")
```

Execute:
```bash
python testar_whapi.py
```

### Teste 2: Enviar Mensagem de Teste

Crie `testar_envio_whapi.py`:

```python
from services.whapi_service import WhapiService

# Criar instância do serviço
whapi = WhapiService()

# Verificar se está configurado
if not whapi.esta_configurado():
    print("❌ whapi.cloud não está configurado!")
    print("Configure WHAPI_API_TOKEN e WHAPI_PHONE_ID")
    exit(1)

# Enviar mensagem de teste
numero = input("Digite seu número (com DDD, ex: 11987654321): ")
mensagem = "🧪 Teste de integração whapi.cloud\n\nSe você recebeu esta mensagem, a integração está funcionando! ✅"

print(f"\n📤 Enviando mensagem de teste para {numero}...")
sucesso = whapi.enviar_mensagem(numero, mensagem)

if sucesso:
    print("\n✅ SUCESSO! Verifique seu WhatsApp.")
else:
    print("\n❌ Falha ao enviar. Verifique os logs acima.")
```

Execute:
```bash
python testar_envio_whapi.py
```

### Teste 3: Testar com Agendamento

```python
from app import app, db
from models import Agendamento
from services.whapi_service import enviar_confirmacao_agendamento

with app.app_context():
    # Buscar um agendamento recente
    agendamento = Agendamento.query.order_by(Agendamento.id.desc()).first()
    
    if agendamento:
        print(f"📋 Testando com agendamento #{agendamento.id}")
        print(f"Cliente: {agendamento.nome_cliente}")
        print(f"Telefone: {agendamento.telefone}")
        
        sucesso = enviar_confirmacao_agendamento(agendamento)
        
        if sucesso:
            print("✅ Mensagem enviada com sucesso!")
        else:
            print("❌ Falha ao enviar mensagem")
    else:
        print("❌ Nenhum agendamento encontrado no banco")
```

---

## 6. 🚀 Deploy em Produção

### Render (Recomendado)

1. **Criar Web Service**:
   - Acesse https://dashboard.render.com
   - Clique em **"New +"** → **"Web Service"**
   - Conecte seu repositório GitHub

2. **Configurar Build**:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

3. **Adicionar Variáveis de Ambiente**:
   - Clique em **"Environment"**
   - Adicione as variáveis (WHAPI_API_TOKEN, WHAPI_PHONE_ID, etc.)

4. **Deploy**:
   - Clique em **"Create Web Service"**
   - Aguarde o deploy (3-5 minutos)

### Heroku

```bash
# Login
heroku login

# Criar app
heroku create minha-barbearia

# Configurar variáveis
heroku config:set WHAPI_API_TOKEN=seu-token
heroku config:set WHAPI_PHONE_ID=seu-phone-id
heroku config:set SECRET_KEY=sua-chave

# Deploy
git push heroku main
```

### Railway

1. Conecte seu repositório
2. Adicione variáveis de ambiente
3. Deploy automático

---

## 7. ❓ Solução de Problemas

### Problema: "API não configurada"

**Causa**: Variáveis de ambiente não definidas

**Solução**:
1. Verifique se `.env` existe e está preenchido
2. Execute `python testar_whapi.py`
3. Em produção, verifique as variáveis na plataforma

### Problema: "Erro 401 - Unauthorized"

**Causa**: Token inválido ou expirado

**Solução**:
1. Acesse o painel do whapi.cloud
2. Gere um novo token
3. Atualize a variável `WHAPI_API_TOKEN`

### Problema: "Erro 404 - Channel not found"

**Causa**: Phone ID incorreto

**Solução**:
1. Verifique o Phone ID no painel
2. Certifique-se de copiar exatamente como mostrado
3. Inclua o sufixo `@c.us` se necessário

### Problema: "Timeout ao enviar"

**Causa**: Conexão instável ou canal desconectado

**Solução**:
1. Acesse o painel do whapi.cloud
2. Verifique se o canal está **"Connected"**
3. Se desconectado, escaneie o QR Code novamente

### Problema: Mensagens não chegam

**Causa**: Número formatado incorretamente

**Solução**:
- Use formato internacional: `5511987654321`
- Inclua código do país (55) + DDD + número
- Remova espaços, parênteses e hífens

### Verificar Logs

```python
# No seu código, adicione:
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

## 📊 Comparação com Solução Anterior

| Aspecto | Solução Antiga (VPS) | Nova Solução (whapi.cloud) |
|---------|---------------------|---------------------------|
| Servidor adicional | ✅ Necessário | ❌ Não necessário |
| Complexidade | 🔴 Alta | 🟢 Baixa |
| Estabilidade | 🟡 Média | 🟢 Alta |
| Custo mensal | ~R$ 50 (VPS) | A partir de R$ 0 |
| Configuração | 1-2 horas | 10-15 minutos |
| Manutenção | 🔴 Frequente | 🟢 Mínima |

---

## 🎉 Pronto!

Agora seu sistema envia mensagens automaticamente quando:
- ✅ Cliente faz um agendamento (confirmação imediata)
- ✅ 24h antes do horário (lembrete)
- ✅ 2h antes do horário (lembrete urgente) - opcional

---

## 📞 Suporte

- **Documentação whapi.cloud**: https://whapi.cloud/pt/docs
- **Status do serviço**: https://status.whapi.cloud
- **Suporte whapi**: support@whapi.cloud

---

## 🔗 Links Úteis

- 🌐 Site whapi.cloud: https://whapi.cloud
- 📱 Painel: https://panel.whapi.cloud
- 📚 API Docs: https://whapi.cloud/pt/docs
- 💰 Preços: https://whapi.cloud/pt/price

---

**Data de criação**: 21/01/2026  
**Última atualização**: 21/01/2026
