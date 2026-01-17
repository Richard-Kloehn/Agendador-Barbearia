# 🚀 Guia Rápido de Instalação

## Instalação em 5 Minutos

### 1. Instalar Python
- Baixe Python 3.8+ em: https://www.python.org/downloads/
- Durante a instalação, marque "Add Python to PATH"

### 2. Abrir Terminal no Projeto
```bash
cd "D:\Dados pessoais\Desktop\App Barbearia VS"
```

### 3. Criar Ambiente Virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar Variáveis
```bash
copy .env.example .env
```

**Edite o arquivo .env** e adicione uma chave secreta:
```
SECRET_KEY=minha-chave-super-secreta-12345
```

### 6. Executar
```bash
python app.py
```

✅ **Pronto!** Acesse: http://localhost:5000

---

## 🧪 Testando sem WhatsApp

O sistema funciona completamente mesmo sem configurar o Twilio. Você verá avisos no console, mas todos os agendamentos funcionarão normalmente.

Para testar:
1. Acesse http://localhost:5000
2. Preencha nome e telefone (pode ser qualquer)
3. Escolha data e horário
4. Confirme o agendamento
5. Acesse http://localhost:5000/admin-dashboard para ver o painel admin

---

## 📱 Configurar WhatsApp (Opcional)

### Método 1: Twilio Sandbox (Gratuito para Testes)

1. Crie conta em: https://www.twilio.com/try-twilio
2. Vá para Console > Messaging > Try it out > Send a WhatsApp message
3. Envie a mensagem de ativação do seu WhatsApp para o número Twilio
4. Copie suas credenciais:
   - **Account SID**
   - **Auth Token**
5. Adicione ao arquivo `.env`:
   ```
   TWILIO_ACCOUNT_SID=seu_account_sid_aqui
   TWILIO_AUTH_TOKEN=seu_auth_token_aqui
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```
6. Reinicie o app

**Limitações do Sandbox:**
- Apenas números previamente aprovados podem receber mensagens
- Cada número precisa enviar a mensagem de ativação
- Ideal para testes

### Método 2: Número Twilio Real (Pago)

Para uso em produção:
1. Compre um número Twilio com WhatsApp
2. Configure as mesmas variáveis no `.env`
3. Envie para qualquer número sem restrições

---

## 🌐 Deploy Online (Gratuito)

### Render.com (Mais Fácil)

1. **Criar conta**: https://render.com
2. **Novo Web Service**: 
   - Connect GitHub (faça upload do projeto primeiro)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
3. **Adicionar PostgreSQL**: 
   - New > Database > PostgreSQL
   - Copie a "Internal Database URL"
4. **Variáveis de Ambiente**:
   ```
   SECRET_KEY=sua-chave-segura
   DATABASE_URL=cole-a-url-do-postgres
   BASE_URL=https://seu-app.onrender.com
   TWILIO_ACCOUNT_SID=seu_sid (se configurou)
   TWILIO_AUTH_TOKEN=seu_token (se configurou)
   ```
5. **Deploy automático!**

### Railway.app (Alternativa)

1. **Criar conta**: https://railway.app
2. **New Project** > Deploy from GitHub
3. **Add PostgreSQL**: New > Database > PostgreSQL
4. **Variáveis**: Adicionar as mesmas do Render
5. **Deploy automático!**

**Ambos oferecem planos gratuitos suficientes para começar!**

---

## ❓ Problemas Comuns

### "python não é reconhecido"
- Reinstale Python marcando "Add to PATH"
- Ou use `py` ao invés de `python`

### "pip não é reconhecido"
```bash
py -m pip install -r requirements.txt
```

### Porta 5000 já em uso
Edite `.env` e mude:
```
PORT=8000
```

### Erro ao criar banco
- Certifique-se que tem permissão de escrita na pasta
- Execute como administrador

---

## 📞 Suporte

Precisa de ajuda? Abra uma issue no GitHub!

**Dica**: Comece sem o WhatsApp configurado. Configure depois se necessário!
