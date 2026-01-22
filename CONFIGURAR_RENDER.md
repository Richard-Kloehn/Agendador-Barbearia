# 🚀 Como Configurar WhatsApp no Render

## Problema Identificado

A API do WhatsApp não está funcionando no Render porque as **variáveis de ambiente** não estão configuradas corretamente.

## ✅ Solução: Configurar Variáveis de Ambiente

### Passo 1: Acessar o Dashboard do Render

1. Acesse [https://dashboard.render.com](https://dashboard.render.com)
2. Faça login na sua conta
3. Selecione seu serviço (Web Service da barbearia)

### Passo 2: Adicionar Variáveis de Ambiente

1. No menu lateral, clique em **"Environment"**
2. Role até a seção **"Environment Variables"**
3. Adicione as seguintes variáveis (clique em **"Add Environment Variable"** para cada uma):

#### Variáveis Obrigatórias:

```
WHAPI_API_TOKEN=seu-token-do-whapi-cloud
WHAPI_API_URL=https://gate.whapi.cloud
DATABASE_URL=sua-url-do-banco-postgresql
SECRET_KEY=sua-chave-secreta-min-32-caracteres
```

### Passo 3: Obter Token do whapi.cloud

Se você ainda não tem o token:

1. Acesse [https://whapi.cloud](https://whapi.cloud)
2. Faça login ou crie uma conta
3. Vá em **"Channels"** → **"Add Channel"**
4. Conecte seu WhatsApp via QR Code
5. Copie o **API Token** gerado
6. Cole no Render como valor de `WHAPI_API_TOKEN`

### Passo 4: Salvar e Reiniciar

1. Depois de adicionar todas as variáveis, clique em **"Save Changes"**
2. O Render vai **reiniciar automaticamente** o serviço
3. Aguarde alguns minutos para o deploy completar

## 🔍 Como Verificar se Está Funcionando

### 1. Verificar Logs no Render

1. No dashboard do Render, clique em **"Logs"**
2. Procure por mensagens como:
   ```
   ✅ WHAPI configurado (Token: ABC12345...XYZ)
   ✅ Scheduler de lembretes iniciado
   ```

### 2. Fazer um Teste de Agendamento

1. Acesse seu site hospedado
2. Faça um agendamento **para daqui a 1 ou 2 horas** (menos de 24h)
3. O sistema vai enviar o lembrete **imediatamente**
4. Verifique os logs para confirmar:
   ```
   ⚡ Agendamento em menos de 24h - Enviando lembrete imediato
   ✅ Lembrete imediato enviado com sucesso
   ```

### 3. Se Houver Erro

Se você ver mensagens de erro como:
```
❌ Erro whapi.cloud (401): Unauthorized
```

**Soluções:**
- Verifique se o token está correto (sem espaços extras)
- Confirme que o canal WhatsApp está ativo no whapi.cloud
- Certifique-se de que o token não expirou

## 📋 Checklist de Configuração

- [ ] Variável `WHAPI_API_TOKEN` configurada
- [ ] Variável `WHAPI_API_URL` configurada (https://gate.whapi.cloud)
- [ ] Variável `DATABASE_URL` configurada
- [ ] Variável `SECRET_KEY` configurada
- [ ] Serviço reiniciado no Render
- [ ] Logs verificados (sem erros de configuração)
- [ ] Teste de agendamento realizado

## 🎯 Funcionalidades Implementadas

### ✅ Envio Automático Inteligente

O sistema agora detecta automaticamente quando fazer o envio:

1. **Agendamento > 24h de antecedência:**
   - Lembrete será enviado automaticamente 24h antes
   - Processado pelo scheduler a cada hora

2. **Agendamento < 24h de antecedência:**
   - Lembrete enviado **IMEDIATAMENTE** após confirmação
   - Cliente recebe na hora

### ✅ Textos Atualizados

- Removido: "Você receberá confirmação e lembrete"
- Atualizado: "Você receberá um lembrete 24h antes"
- Mais claro e direto para o cliente

## 🆘 Precisa de Ajuda?

Se após seguir todos os passos ainda houver problemas:

1. Verifique os logs do Render em tempo real
2. Teste manualmente a API do whapi.cloud:
   ```bash
   curl -X POST https://gate.whapi.cloud/messages/text \
     -H "Authorization: Bearer SEU_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "to": "5511999999999",
       "body": "Teste"
     }'
   ```

3. Confira se seu plano do whapi.cloud está ativo

---

**Desenvolvido para Navalha's Barber Club** ✂️💈
