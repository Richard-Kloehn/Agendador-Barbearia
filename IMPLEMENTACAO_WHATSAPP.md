# 📱 Implementação do WhatsApp - Sistema de Barbearia

## ✅ O que foi implementado

### 1. **Novo Serviço de WhatsApp** (`whatsapp_service_automation.py`)

Sistema profissional de automação do WhatsApp Web com:

#### 🛡️ Proteções Contra Bloqueio

- **Limite de 15 mensagens por hora** (muito conservador)
- **Intervalo de 8 segundos entre mensagens** (seguro)
- **Intervalo de 60 segundos entre mensagens para o mesmo número**
- **Sistema de fila inteligente**
- **Monitoramento de limites em tempo real**

#### 📝 Mensagens Personalizadas

Cada mensagem é única e contém:
- ✅ Saudação personalizada (Bom dia/Boa tarde/Boa noite)
- ✅ Nome do cliente
- ✅ Nome do barbeiro
- ✅ Serviço contratado
- ✅ Data completa (dia da semana + data formatada)
- ✅ Horário do agendamento
- ✅ Link do site para cancelamento
- ✅ Aviso que é mensagem automática

**Exemplo de mensagem:**
```
Boa tarde, João Silva! ✂️

📅 *Confirmação de Agendamento*

Você tem um horário marcado:

• *Barbeiro:* Carlos
• *Serviço:* Corte + Barba
• *Data:* Segunda-feira, 20/01/2026
• *Horário:* 14:30

⚠️ *Caso precise cancelar*, acesse o site e faça o cancelamento:
http://seusite.com

✅ *Importante:* Esta é uma mensagem automática. Não é necessário responder.

Aguardamos você! 💈
```

### 2. **Envio de Lembretes 24h Antes**

- Mensagens são enviadas entre 23-24 horas antes do agendamento
- Sistema já existente no `app.py` continua funcionando
- Agora usa o novo serviço de automação

### 3. **Script de Teste de Telefones**

Arquivo: `alterar_telefones_teste.py`

- Altera todos os telefones do banco para o seu número (47991557386)
- Permite testar sem enviar para clientes reais
- Inclui avisos de segurança

## 🚀 Como Usar

### Passo 1: Alterar Telefones para Teste

```bash
python alterar_telefones_teste.py
```

Digite `SIM` quando solicitado para confirmar.

### Passo 2: Iniciar o Sistema

```bash
python app.py
```

### Passo 3: Login no WhatsApp Web

Na **primeira execução**:
1. O sistema abrirá o Chrome automaticamente
2. Aguarde a página do WhatsApp Web carregar
3. Escaneie o QR Code com seu celular
4. A sessão ficará salva para próximas execuções

### Passo 4: Testar

- Crie alguns agendamentos para 24h à frente
- O sistema enviará mensagens automaticamente para o seu número
- Monitore os logs no arquivo `whatsapp_automation.log`

## ⚠️ Limites e Cuidados

### Limites Configurados (Muito Seguros)

| Limite | Valor | Motivo |
|--------|-------|--------|
| Mensagens/hora | 15 | Muito conservador para evitar bloqueio |
| Intervalo entre mensagens | 8 segundos | Parecer natural |
| Intervalo mesmo número | 60 segundos | Evitar spam ao mesmo contato |

### Horário de Envio

O sistema verifica agendamentos **a cada 1 hora** e envia lembretes para:
- Agendamentos que faltam entre 23-24 horas
- Horário comercial (melhor prática)

### O que NÃO fazer

❌ **Não envie mais de 20 mensagens por hora**  
❌ **Não envie mensagens idênticas** (o sistema já personaliza)  
❌ **Não envie para números que não conhecem você**  
❌ **Não force envios se o sistema avisar sobre limites**

## 📊 Monitoramento

### Logs

Todos os eventos são registrados em:
- **Terminal**: Saída em tempo real
- **Arquivo**: `whatsapp_automation.log`

Exemplo de logs:
```
2026-01-18 14:30:00 - INFO - Enviando mensagem para 5547991557386...
2026-01-18 14:30:08 - INFO - ✅ Mensagem enviada para 5547991557386!
2026-01-18 14:30:08 - INFO - ✅ Lembrete enviado para João Silva
```

### Verificar Limites

O sistema automaticamente:
- ✅ Conta mensagens enviadas na última hora
- ✅ Impede envio se atingir o limite
- ✅ Aguarda automaticamente os intervalos necessários
- ✅ Registra tudo nos logs

## 🔧 Ajustes de Limites (Se Necessário)

Se quiser ajustar os limites (arquivo `whatsapp_service_automation.py`):

```python
class WhatsAppService:
    # Ajuste aqui se necessário (após testar)
    MAX_MENSAGENS_POR_HORA = 15  # Pode aumentar para 20 gradualmente
    INTERVALO_ENTRE_MENSAGENS = 8  # Mantenha entre 5-10 segundos
    INTERVALO_MINIMO_MESMA_CONVERSA = 60  # Mantenha em 60
```

## 🎯 Fluxo Completo

```mermaid
1. Cliente agenda → Sistema salva no banco
2. A cada 1 hora → Sistema verifica agendamentos
3. Encontra agendamentos 23-24h à frente → Prepara mensagem
4. Verifica limites de segurança → OK para enviar?
5. Personaliza mensagem → Adiciona nome, horário, etc
6. Abre WhatsApp Web → Envia mensagem
7. Aguarda 8 segundos → Pronto para próxima
8. Registra nos logs → Cliente recebe lembrete!
```

## 📱 Quando Colocar em Produção

### Antes de usar com clientes reais:

1. ✅ Teste por pelo menos 1 semana com seu número
2. ✅ Verifique se nenhuma mensagem foi bloqueada
3. ✅ Confirme que as mensagens estão chegando corretamente
4. ✅ Faça backup do banco de dados
5. ✅ Restaure os números reais dos clientes

### Para restaurar números reais:

❌ **Não use o script de alteração novamente!**

✅ **Opção 1**: Restaure um backup do banco de dados  
✅ **Opção 2**: Re-cadastre os telefones corretos no painel admin

## 🆘 Solução de Problemas

### "Navegador não inicia"
```bash
pip install --upgrade selenium webdriver-manager
```

### "QR Code não aparece"
- Delete a pasta `whatsapp_session/`
- Execute novamente

### "Mensagem não é enviada"
- Verifique os logs em `whatsapp_automation.log`
- Certifique-se de que o WhatsApp do celular está conectado
- Verifique se o número é válido

### "Muitas mensagens/limite atingido"
- O sistema aguarda automaticamente
- Verifique os logs para detalhes
- Considere aumentar o intervalo de verificação no scheduler

## 📈 Estatísticas Esperadas

Com os limites atuais:

- **Máximo diário**: ~360 mensagens (15/hora x 24h)
- **Máximo seguro recomendado**: ~200 mensagens/dia
- **Ideal para começar**: 100-150 mensagens/dia

## ✅ Checklist Final

- [x] Serviço de WhatsApp implementado
- [x] Proteções contra bloqueio ativadas
- [x] Mensagens personalizadas
- [x] Sistema de fila e limites
- [x] Logs detalhados
- [x] Script de teste criado
- [x] Documentação completa

## 🎉 Pronto!

O sistema está completamente implementado e pronto para testes!

Execute: `python alterar_telefones_teste.py` e depois `python app.py`

Todas as mensagens serão enviadas para: **47991557386**
