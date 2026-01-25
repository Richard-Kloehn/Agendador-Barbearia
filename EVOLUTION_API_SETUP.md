# Guia de Configuração - Evolution API

## O que é Evolution API?

Evolution API é uma API REST gratuita e open source para WhatsApp, baseada em Baileys. É mais estável e segura que Selenium.

## Passos para Configurar

### Opção 1: Hospedar no Railway (Recomendado)

1. **Acesse**: https://railway.app
2. **Faça login** com GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Use este template**: https://github.com/EvolutionAPI/evolution-api
5. **Configure as variáveis de ambiente**:

```env
AUTHENTICATION_API_KEY=seu_api_key_secreto_aqui
```

6. **Deploy** - Railway vai gerar uma URL tipo: `https://evolution-api-production-xxxx.up.railway.app`

### Opção 2: Hospedar no Render

1. **Acesse**: https://render.com
2. **New** → **Web Service**
3. **Connect** ao repositório: https://github.com/EvolutionAPI/evolution-api
4. **Configure**:
   - **Name**: evolution-api-barbearia
   - **Environment**: Docker
   - **Instance Type**: Free
5. **Add Environment Variable**:
```
AUTHENTICATION_API_KEY=seu_api_key_secreto_aqui
```
6. **Deploy**

### Opção 3: Docker Local (Para testes)

```bash
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=seu_api_key_aqui \
  atendai/evolution-api
```

## Configurar no seu App

Depois de hospedar, adicione no arquivo `.env`:

```env
# Evolution API Configuration
EVOLUTION_API_URL=https://sua-url-evolution-api.railway.app
EVOLUTION_API_KEY=seu_api_key_secreto_aqui
EVOLUTION_INSTANCE_NAME=barbearia
```

## Conectar o WhatsApp

1. **Criar instância** (primeira vez):
```bash
curl -X POST https://sua-url/instance/create \
  -H "apikey: seu_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "barbearia",
    "qrcode": true
  }'
```

2. **Obter QR Code**:
```bash
curl https://sua-url/instance/connect/barbearia \
  -H "apikey: seu_api_key"
```

3. **Escanear o QR Code** com o WhatsApp da barbearia

4. **Verificar conexão**:
```bash
curl https://sua-url/instance/connectionState/barbearia \
  -H "apikey: seu_api_key"
```

## Atualizar o Código do App

No arquivo `routes.py`, troque a importação:

```python
# ANTES (WHAPI):
from services.whapi_service import enviar_confirmacao_agendamento, enviar_lembrete_whatsapp

# DEPOIS (Evolution API):
from services.evolution_api_service import enviar_confirmacao_agendamento, enviar_lembrete_whatsapp
```

No arquivo `app.py`, faça a mesma mudança:

```python
# ANTES:
from services.whapi_service import enviar_lembrete_whatsapp

# DEPOIS:
from services.evolution_api_service import enviar_lembrete_whatsapp
```

## Vantagens

✅ **Gratuito** - 100% open source
✅ **Sem limites** - Envie para quantos números quiser
✅ **Mais estável** - Não depende de navegador
✅ **Mais rápido** - Conexão direta WebSocket
✅ **Mais seguro** - Usa protocolo oficial do WhatsApp Web
✅ **Auto-hospedado** - Você controla seus dados

## Links Úteis

- **Repositório**: https://github.com/EvolutionAPI/evolution-api
- **Documentação**: https://doc.evolution-api.com
- **Postman Collection**: https://github.com/EvolutionAPI/evolution-api/tree/main/postman

## Suporte

Se tiver problemas:
1. Verifique os logs do Railway/Render
2. Teste a conexão com curl
3. Verifique se o QR Code foi escaneado
4. Confirme que as variáveis de ambiente estão corretas
