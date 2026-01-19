# 📱 CONFIGURAÇÃO WHATSAPP - SCRIPT DE AUTOMAÇÃO

## ✅ Sistema Configurado

Seu sistema está configurado para usar **automação com Selenium** ao invés do Twilio.

## 🎯 Como Funciona

### Localmente (Seu Computador)
- ✅ WhatsApp funciona perfeitamente
- ✅ Usa seu WhatsApp pessoal através do Chrome
- ✅ Envia mensagens automaticamente após agendamentos
- ✅ Envia lembretes 24h antes

### Em Produção (Servidor Render)
- ⚠️ WhatsApp **NÃO funciona** (sem navegador no servidor)
- ✅ Sistema continua funcionando normalmente
- ✅ Agendamentos são salvos corretamente
- ❌ Mensagens não são enviadas automaticamente

## 🚀 Como Usar Localmente

### 1. Primeira Vez (Escanear QR Code)
```bash
python app.py
```
- O Chrome abrirá automaticamente
- Escaneie o QR Code com seu WhatsApp
- Aguarde até aparecer "✅ Login realizado com sucesso!"
- A sessão fica salva para próximos usos

### 2. Próximas Execuções (Automático)
```bash
python app.py
```
- O Chrome abre em modo invisível (headless)
- Usa a sessão já salva
- Envia mensagens automaticamente

## 📋 Recursos Disponíveis

### ✅ Funcionam Automaticamente
- Confirmação de agendamento (ao criar)
- Lembrete 24h antes do horário
- Proteção contra bloqueio (limites de envio)
- Intervalos de segurança entre mensagens

### ⚙️ Configurações de Segurança
```python
MAX_MENSAGENS_POR_HORA = 15      # Máximo 15 mensagens/hora
INTERVALO_ENTRE_MENSAGENS = 8    # 8 segundos entre mensagens
INTERVALO_MESMA_CONVERSA = 60    # 1 minuto para mesmo número
```

## 🔄 Scripts Disponíveis

### Testar Envio Manual
```bash
python test_whatsapp_automation.py
```

### Enviar Lembrete Agora (Teste)
```bash
python testar_envio_agora.py
```

### Verificar Números Cadastrados
```bash
python restaurar_numeros_reais.py
```

## ⚠️ Importante

### NÃO funciona em:
- ❌ Servidores (Render, Heroku, Railway)
- ❌ Docker sem interface gráfica
- ❌ Ambientes headless sem Chrome

### SIM funciona em:
- ✅ Seu computador (Windows/Mac/Linux)
- ✅ Servidor VPS com interface gráfica
- ✅ Windows Server com Chrome instalado

## 💡 Alternativas para Produção

Se precisar de WhatsApp em produção, considere:

1. **Twilio API** (Pago)
   - Funciona em qualquer servidor
   - Custo: ~$0.005 por mensagem
   - Requer número dedicado

2. **WhatsApp Business API** (Oficial)
   - Versão oficial do WhatsApp
   - Mais caro, mas profissional
   - Requer aprovação

3. **Servidor VPS com Interface**
   - Instalar Chrome no servidor
   - Mais complexo de configurar
   - Manter sessão ativa

## 📞 Suporte

Para qualquer dúvida sobre o sistema de automação, consulte:
- `COMO_TESTAR_WHATSAPP.md`
- `IMPLEMENTACAO_WHATSAPP.md`
- `ENVIO_INTELIGENTE.md`
