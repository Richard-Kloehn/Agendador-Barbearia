# Sistema de Agendamento para Barbearia 💈

Sistema web completo e profissional para agendamento de horários em barbearias, desenvolvido com Python/Flask e interface moderna.

## 🚀 Funcionalidades

### Para Clientes
- ✅ Agendamento online intuitivo e responsivo
- 📅 Visualização de horários disponíveis em tempo real
- 📱 Lembretes automáticos por WhatsApp 24h antes
- ✔️ Sistema de confirmação/cancelamento via WhatsApp
- 💬 Interface moderna e fácil de usar

### Para Administradores
- 📊 Dashboard com estatísticas em tempo real
- 📋 Gerenciamento completo de agendamentos
- ⚙️ Configuração de horários de funcionamento
- 🔧 Controle de duração de atendimentos
- 📈 Visualização de todos os agendamentos

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.8+ com Flask
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **WhatsApp**: Twilio API
- **Scheduler**: APScheduler para envio automático de lembretes

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta Twilio (para envio de mensagens WhatsApp)
- Git (opcional)

## 🔧 Instalação e Configuração Local

### 1. Clone ou baixe o projeto

```bash
git clone <seu-repositorio>
cd "App Barbearia VS"
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
copy .env.example .env  # Windows
# ou
cp .env.example .env    # Linux/Mac
```

Edite o arquivo `.env` com suas credenciais:

```env
SECRET_KEY=sua-chave-secreta-segura
TWILIO_ACCOUNT_SID=seu_account_sid
TWILIO_AUTH_TOKEN=seu_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
BASE_URL=http://localhost:5000
DATABASE_URL=sqlite:///barbearia.db
PORT=5000
```

### 5. Configure o Twilio (WhatsApp)

1. Crie uma conta em [https://www.twilio.com](https://www.twilio.com)
2. Acesse o Console e copie:
   - **Account SID**
   - **Auth Token**
3. Configure o WhatsApp Sandbox:
   - Acesse "Messaging" > "Try it out" > "Send a WhatsApp message"
   - Siga as instruções para conectar seu WhatsApp de teste
4. Para produção, você precisará de um número Twilio com WhatsApp habilitado

### 6. Execute o aplicativo

```bash
python app.py
```

O sistema estará disponível em: **http://localhost:5000**

- **Site do Cliente**: http://localhost:5000
- **Painel Admin**: http://localhost:5000/admin-dashboard

## 🌐 Deploy para Produção

### Opção 1: Render.com (Recomendado - Gratuito)

1. **Crie uma conta no Render**: [https://render.com](https://render.com)

2. **Crie um novo Web Service**:
   - Conecte seu repositório GitHub
   - Configurações:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Python Version**: 3.11

3. **Configure as variáveis de ambiente** no painel do Render:
   ```
   SECRET_KEY=sua-chave-secreta
   TWILIO_ACCOUNT_SID=seu_sid
   TWILIO_AUTH_TOKEN=seu_token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   BASE_URL=https://seu-app.onrender.com
   DATABASE_URL=sua_url_postgresql
   ```

4. **Adicione um banco PostgreSQL** (gratuito no Render):
   - Crie um PostgreSQL database
   - Copie a URL de conexão para `DATABASE_URL`

### Opção 2: Railway.app

1. **Crie uma conta no Railway**: [https://railway.app](https://railway.app)

2. **Deploy pelo GitHub**:
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Escolha seu repositório

3. **Adicione PostgreSQL**:
   - Clique em "New" > "Database" > "PostgreSQL"
   - Railway irá configurar automaticamente

4. **Configure as variáveis de ambiente**:
   - Acesse "Variables"
   - Adicione as mesmas variáveis do Render

### Opção 3: Heroku

```bash
# Instale o Heroku CLI
# Login
heroku login

# Crie um novo app
heroku create nome-da-sua-barbearia

# Adicione PostgreSQL
heroku addons:create heroku-postgresql:mini

# Configure as variáveis
heroku config:set SECRET_KEY=sua-chave
heroku config:set TWILIO_ACCOUNT_SID=seu_sid
heroku config:set TWILIO_AUTH_TOKEN=seu_token
heroku config:set BASE_URL=https://seu-app.herokuapp.com

# Deploy
git push heroku main
```

### Arquivo Procfile (necessário para Heroku)

Crie um arquivo `Procfile` na raiz:

```
web: gunicorn app:app
```

## 📱 Como Funciona o Sistema de WhatsApp

1. **Agendamento**: Cliente agenda um horário no site
2. **Confirmação Imediata**: Recebe uma mensagem de confirmação
3. **Lembrete Automático**: 24h antes, recebe um lembrete com link
4. **Confirmação Final**: Cliente pode confirmar ou cancelar pelo link
5. **Auto-confirmação**: Se não responder, o horário é confirmado automaticamente

## ⚙️ Configurações do Sistema

Acesse o **Painel Admin** para configurar:

- Nome da barbearia
- Horários de funcionamento
- Duração dos atendimentos
- Intervalo de almoço
- Dias de funcionamento

## 🔒 Segurança

- ✅ Tokens únicos para cada confirmação
- ✅ Validação de dados
- ✅ Variáveis de ambiente para credenciais
- ✅ CORS configurado

## 📊 Estrutura do Projeto

```
App Barbearia VS/
│
├── app.py                  # Aplicação principal
├── models.py              # Modelos do banco de dados
├── routes.py              # Rotas da API
├── requirements.txt       # Dependências
├── .env                   # Variáveis de ambiente (não commitar)
├── .env.example          # Exemplo de configuração
│
├── services/
│   ├── __init__.py
│   └── whatsapp_service.py  # Integração com Twilio
│
└── templates/
    ├── index.html         # Página do cliente
    ├── admin.html         # Painel administrativo
    └── confirmar.html     # Página de confirmação
```

## 🐛 Solução de Problemas

### Erro ao enviar WhatsApp

- Verifique se as credenciais Twilio estão corretas
- Confirme que o número está no formato correto: `+5511999999999`
- Teste no WhatsApp Sandbox antes de usar em produção

### Horários não aparecem

- Verifique a configuração de horários no painel admin
- Confirme que a data selecionada não está no passado
- Verifique se o dia da semana está nos dias de funcionamento

### Erro de banco de dados

- Para SQLite, certifique-se que o arquivo tem permissões de escrita
- Para PostgreSQL, verifique a string de conexão

## 📝 Customização

### Alterar cores do tema

Edite as classes CSS no arquivo HTML (gradientes estão em `gradient-bg` e `btn-primary`)

### Adicionar novos serviços

Modifique o modelo `Agendamento` em `models.py` para adicionar campos como tipo de serviço

### Mudar duração padrão

Acesse o painel admin e configure em "Configurações"

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto é de código aberto para fins educacionais e comerciais.

## 💬 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Entre em contato através do email: [seu-email]

## 🎉 Próximas Funcionalidades

- [ ] Sistema de múltiplos barbeiros
- [ ] Integração com Google Calendar
- [ ] Pagamento online
- [ ] Sistema de avaliações
- [ ] App mobile nativo
- [ ] Relatórios financeiros

---

**Desenvolvido com ❤️ usando Python e Flask**

🚀 **Pronto para usar!** Basta seguir as instruções de instalação e configuração.
