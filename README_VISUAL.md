# 💈 Sistema de Agendamento - Barbearia

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Pronto-success?style=for-the-badge)

**Sistema completo e profissional para agendamento online de horários**

[🚀 Começar](#-instalação-rápida) • [📚 Documentação](#-documentação) • [🌐 Deploy](#-deploy) • [🎨 Personalizar](#-personalização)

</div>

---

## 📸 Demonstração

### 🌐 Página do Cliente
```
┌─────────────────────────────────────────────────┐
│  💈 BARBEARIA STYLE                            │
│  Agende seu horário de forma rápida e fácil   │
│                                                 │
│  [1] Seus Dados                                │
│     👤 Nome: _________________                 │
│     📱 WhatsApp: (__) _____-____               │
│                                                 │
│  [2] Escolha a Data                            │
│     📅 Data: [Calendário]                      │
│     🕐 Horários: [09:00] [10:00] [11:00]...   │
│                                                 │
│  [3] Confirmar ✅                              │
└─────────────────────────────────────────────────┘
```

### 🔐 Painel Administrativo
```
┌─────────────────────────────────────────────────┐
│  Dashboard  |  Agendamentos  |  Configurações   │
├─────────────────────────────────────────────────┤
│  📊 Estatísticas                                │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐              │
│  │ 150 │ │  8  │ │ 120 │ │ 15  │              │
│  │Total│ │Hoje │ │Conf.│ │Pend.│              │
│  └─────┘ └─────┘ └─────┘ └─────┘              │
│                                                 │
│  📋 Agendamentos de Hoje                       │
│  10:00 - João Silva      [Confirmado]          │
│  11:00 - Maria Santos    [Pendente]            │
│  14:00 - Pedro Costa     [Confirmado]          │
└─────────────────────────────────────────────────┘
```

---

## ✨ Funcionalidades

### Para Clientes
- ✅ Agendamento online intuitivo em 3 passos
- 📅 Visualização de horários disponíveis em tempo real
- 📱 Lembretes automáticos via WhatsApp 24h antes
- ✔️ Confirmação/cancelamento via link único
- 💬 Interface moderna, bonita e responsiva

### Para Administradores
- 📊 Dashboard com estatísticas em tempo real
- 📋 Gerenciamento completo de agendamentos
- ⚙️ Configuração flexível de horários
- 🔧 Controle de duração de atendimentos
- 📈 Filtros avançados e visualização detalhada

---

## 🚀 Instalação Rápida

### Windows (Automático)

```bash
# 1. Clone ou baixe o projeto
cd "App Barbearia VS"

# 2. Execute o instalador
setup.bat

# 3. Execute o servidor
run.bat
```

### Manual (Todas as plataformas)

```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar ambiente
copy .env.example .env  # Windows
# ou
cp .env.example .env    # Linux/Mac

# 5. Inicializar banco
python init_db.py

# 6. Executar
python app.py
```

**✅ Pronto!** Acesse: http://localhost:5000

---

## 📋 Requisitos

- Python 3.8 ou superior
- Conta Twilio (opcional, para WhatsApp)
- Navegador moderno

---

## 🔧 Configuração

### 1. Variáveis de Ambiente

Edite o arquivo `.env`:

```bash
# Obrigatório
SECRET_KEY=sua-chave-secreta-segura

# Banco de dados
DATABASE_URL=sqlite:///barbearia.db

# WhatsApp (opcional para testes)
TWILIO_ACCOUNT_SID=seu_account_sid
TWILIO_AUTH_TOKEN=seu_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# URL base
BASE_URL=http://localhost:5000
```

### 2. Configurar Twilio (Opcional)

1. Crie conta em [Twilio](https://www.twilio.com)
2. Ative WhatsApp Sandbox
3. Copie credenciais para `.env`
4. Reinicie o servidor

**Nota:** O sistema funciona perfeitamente sem WhatsApp para testes locais.

---

## 🌐 Deploy

### Render.com (Recomendado - Gratuito)

1. Crie conta em [Render](https://render.com)
2. New Web Service → Conecte GitHub
3. Configurações:
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `gunicorn app:app`
4. Adicione PostgreSQL (gratuito)
5. Configure variáveis de ambiente
6. Deploy!

### Railway.app

1. Crie conta em [Railway](https://railway.app)
2. Deploy from GitHub
3. Add PostgreSQL
4. Configure variáveis
5. Deploy!

**Ambos oferecem planos gratuitos!**

Instruções detalhadas no [README.md](README.md)

---

## 📚 Documentação

| Arquivo | Descrição |
|---------|-----------|
| [INICIO.md](INICIO.md) | 👋 Comece por aqui - Visão geral |
| [README.md](README.md) | 📖 Documentação técnica completa |
| [INSTALACAO.md](INSTALACAO.md) | 🚀 Guia de instalação em 5 minutos |
| [TESTES.md](TESTES.md) | 🧪 Roteiro completo de testes |
| [PERSONALIZACAO.md](PERSONALIZACAO.md) | 🎨 Como customizar tudo |
| [VISAO_GERAL.txt](VISAO_GERAL.txt) | 📊 Arquitetura visual do sistema |

---

## 🎨 Personalização

### Mudar Cores

Edite `templates/index.html`:

```css
.gradient-bg {
    /* Cores atuais */
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    
    /* Exemplos: */
    /* Azul: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); */
    /* Verde: linear-gradient(135deg, #10b981 0%, #047857 100%); */
    /* Vermelho: linear-gradient(135deg, #ef4444 0%, #991b1b 100%); */
}
```

### Configurar Horários

**Pelo Painel Admin (Fácil):**
1. Acesse `/admin-dashboard`
2. Vá em "Configurações"
3. Altere todos os horários visualmente

**Veja mais em:** [PERSONALIZACAO.md](PERSONALIZACAO.md)

---

## 📊 Estrutura do Projeto

```
App Barbearia VS/
├── app.py                  # Aplicação principal
├── models.py              # Modelos do banco
├── routes.py              # Rotas da API
├── requirements.txt       # Dependências
├── .env                   # Configurações (não commitar)
│
├── services/              # Serviços
│   └── whatsapp_service.py
│
├── templates/             # Templates HTML
│   ├── index.html         # Página do cliente
│   ├── admin.html         # Painel admin
│   └── confirmar.html     # Confirmação
│
├── setup.bat             # Instalador (Windows)
├── run.bat               # Executar (Windows)
└── init_db.py            # Inicializar banco
```

---

## 🛠️ Tecnologias

<div align="center">

| Backend | Frontend | Banco | Outros |
|---------|----------|-------|--------|
| Python 3.8+ | HTML5 | SQLite | Twilio API |
| Flask 3.0 | CSS3 | PostgreSQL | APScheduler |
| SQLAlchemy | JavaScript | | Gunicorn |
| | Tailwind CSS | | |

</div>

---

## 🔒 Segurança

- ✅ Tokens únicos e seguros
- ✅ Validação de dados robusta
- ✅ Proteção contra SQL Injection
- ✅ CORS configurado
- ✅ Variáveis de ambiente
- ✅ Senhas não armazenadas em texto

---

## 🧪 Testes

Execute o roteiro completo em [TESTES.md](TESTES.md)

**Quick Test:**

```bash
# 1. Iniciar servidor
python app.py

# 2. Acessar
http://localhost:5000

# 3. Criar agendamento
- Nome: Teste
- Telefone: (11) 99999-9999
- Data: Amanhã
- Horário: 10:00

# 4. Verificar admin
http://localhost:5000/admin-dashboard
```

---

## 📈 Roadmap

- [ ] Sistema de múltiplos barbeiros
- [ ] Escolha de serviços (Corte/Barba/etc)
- [ ] Integração com Google Calendar
- [ ] Pagamento online
- [ ] Sistema de fidelidade
- [ ] App mobile nativo
- [ ] Relatórios avançados

---

## 🤝 Contribuindo

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📞 Suporte

### Problemas?

1. 📚 Consulte a [documentação](README.md)
2. 🐛 Abra uma [issue](https://github.com/seu-usuario/seu-repo/issues)
3. 💬 Entre em contato

### FAQ

**P: Funciona sem WhatsApp?**
R: Sim! Ideal para testes locais.

**P: É gratuito para uso comercial?**
R: Sim, totalmente gratuito!

**P: Preciso saber programar para usar?**
R: Não! Basta seguir o guia de instalação.

**P: Posso customizar as cores?**
R: Sim! Veja [PERSONALIZACAO.md](PERSONALIZACAO.md)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.

Você pode usar, modificar e distribuir livremente, inclusive para fins comerciais.

---

## ⭐ Apoie o Projeto

Se este projeto te ajudou:

- ⭐ Dê uma estrela no GitHub
- 🐛 Reporte bugs
- 💡 Sugira melhorias
- 📢 Compartilhe com outros
- ☕ [Compre um café](https://www.buymeacoffee.com/seu-usuario)

---

## 📬 Contato

- 📧 Email: seu-email@exemplo.com
- 🐙 GitHub: [@seu-usuario](https://github.com/seu-usuario)
- 💼 LinkedIn: [Seu Nome](https://linkedin.com/in/seu-perfil)

---

<div align="center">

**💈 Sistema de Agendamento para Barbearia 💈**

Desenvolvido com ❤️ usando Python + Flask

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Powered by Flask](https://img.shields.io/badge/Powered%20by-Flask-green?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)

**[⬆ Voltar ao topo](#-sistema-de-agendamento---barbearia)**

</div>
