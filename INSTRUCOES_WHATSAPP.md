# Instruções - Automação WhatsApp Web

## 📋 Pré-requisitos

1. **Python 3.7 ou superior** instalado
2. **Google Chrome** instalado
3. **ChromeDriver** compatível com sua versão do Chrome

## 🚀 Instalação

### Passo 1: Instalar as dependências

```bash
pip install -r requirements_whatsapp.txt
```

Ou instale manualmente:

```bash
pip install selenium==4.16.0 webdriver-manager==4.0.1
```

### Passo 2: Verificar ChromeDriver

O script tentará usar o ChromeDriver do sistema. Se não funcionar:

1. Verifique sua versão do Chrome: `chrome://settings/help`
2. Baixe o ChromeDriver compatível: https://chromedriver.chromium.org/downloads
3. Adicione o ChromeDriver ao PATH do sistema

**Alternativa mais fácil**: O script pode usar `webdriver-manager` que baixa automaticamente o driver correto.

## 🧪 Como Testar

### Teste Simples (Uma Mensagem)

```bash
python test_whatsapp_automation.py
```

Escolha a opção **1** e siga as instruções:

1. O navegador Chrome abrirá automaticamente
2. Se for a primeira vez, escaneie o QR Code com seu WhatsApp
3. Digite o número de destino (com DDD)
4. Digite a mensagem
5. A mensagem será enviada automaticamente

### Teste em Lote (Múltiplas Mensagens)

Escolha a opção **2**:

1. Edite o arquivo `test_whatsapp_automation.py`
2. Modifique a lista `contatos` na função `teste_envio_lote()`
3. Execute o script
4. As mensagens serão enviadas sequencialmente

## 📝 Exemplo de Uso no Código

```python
from test_whatsapp_automation import WhatsAppAutomation

# Criar instância
whatsapp = WhatsAppAutomation(headless=False)

# Iniciar navegador
whatsapp.iniciar_navegador()

# Abrir WhatsApp Web
whatsapp.abrir_whatsapp_web()

# Enviar mensagem
whatsapp.enviar_mensagem(
    numero='5511999999999',
    mensagem='Olá! Seu agendamento foi confirmado.'
)

# Fechar
whatsapp.fechar()
```

## 🔧 Configurações Importantes

### Sessão Persistente

O script salva a sessão do WhatsApp na pasta `whatsapp_session/`. Isso significa que você só precisa escanear o QR Code uma vez. Nas próximas execuções, ele usará a sessão salva.

### Logs

Todos os eventos são registrados em `whatsapp_automation.log` para facilitar a depuração.

### Formato do Número

- **Com código do país**: `5511999999999`
- **Sem código do país**: `11999999999` (será adicionado automaticamente)
- DDD + Número: `11999999999`

## ⚠️ Cuidados e Limitações

1. **Limite de Mensagens**: O WhatsApp pode bloquear contas que enviam muitas mensagens em curto período
2. **Intervalo entre Envios**: Recomendado 3-5 segundos entre cada mensagem
3. **Horário de Envio**: Evite enviar mensagens em horários inapropriados
4. **Sessão Ativa**: Mantenha o WhatsApp do celular conectado à internet
5. **Política do WhatsApp**: Use apenas para comunicações legítimas e autorizadas

## 🐛 Solução de Problemas

### Erro: ChromeDriver não encontrado

**Solução**: Instale o webdriver-manager ou baixe manualmente o ChromeDriver

### Erro: Timeout ao fazer login

**Solução**: Aumente o tempo de espera ou escaneie o QR Code mais rapidamente

### Erro: Elemento não encontrado

**Solução**: O WhatsApp Web pode ter mudado sua interface. Verifique se há atualizações do script

### Mensagem não é enviada

**Soluções possíveis**:
- Verifique se o número está correto e inclui DDD
- Certifique-se de que o contato existe no WhatsApp
- Verifique sua conexão com internet

## 📊 Logs e Monitoramento

O arquivo `whatsapp_automation.log` registra:
- Horário de cada operação
- Sucesso/falha de envios
- Erros e exceções
- Números contatados

## 🔐 Segurança

- **Não compartilhe** a pasta `whatsapp_session/` (contém dados de login)
- **Adicione ao .gitignore**:
  ```
  whatsapp_session/
  whatsapp_automation.log
  ```

## 📞 Próximos Passos

Após testar e validar o funcionamento:

1. O script pode ser integrado ao sistema da barbearia
2. Substituir o serviço Twilio pelo script de automação
3. Adaptar o `whatsapp_service.py` para usar esta implementação
4. Implementar fila de mensagens para maior controle

## 💡 Dicas de Uso

- **Primeira execução**: Deixe o navegador aberto (headless=False) para escanear o QR Code
- **Produção**: Depois de configurado, pode usar headless=True para execução em background
- **Testes**: Sempre teste com seu próprio número antes de enviar para clientes
- **Backup**: Faça backup da pasta `whatsapp_session/` periodicamente
