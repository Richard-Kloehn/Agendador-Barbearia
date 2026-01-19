## 🚀 CONFIGURAÇÃO: WhatsApp em Produção com VPS

Este guia explica como configurar o sistema de WhatsApp para funcionar em produção usando um servidor VPS separado.

---

## 📋 Arquitetura

```
┌─────────────────┐         HTTP          ┌─────────────────┐
│   RENDER.COM    │ ─────────────────────>│  VPS (Contabo/  │
│   (Site Web)    │  Envia requisições    │   DigitalOcean) │
│                 │                       │                 │
│  - Agendamentos │                       │  - Chrome       │
│  - Interface    │                       │  - Selenium     │
│  - Banco Dados  │                       │  - WhatsApp     │
└─────────────────┘                       └─────────────────┘
```

**Site (Render)**: Chama API HTTP quando precisa enviar WhatsApp  
**VPS**: Recebe requisição e envia mensagem via automação Selenium

---

## 🛠️ PASSO 1: Configurar VPS

### Opções de VPS (escolha uma):
- **Contabo** (€4-8/mês) - Recomendado
- **DigitalOcean** ($6/mês)
- **Vultr** ($6/mês)
- **Amazon Lightsail** ($5/mês)

### Requisitos Mínimos:
- **RAM**: 2GB
- **CPU**: 1 core
- **OS**: Ubuntu 22.04 LTS
- **Disco**: 20GB

---

## 📦 PASSO 2: Instalar Dependências no VPS

Conecte no VPS via SSH e execute:

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e pip
sudo apt install python3 python3-pip python3-venv -y

# Instalar Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y

# Instalar Xvfb (servidor virtual de display)
sudo apt install xvfb -y

# Criar diretório do projeto
mkdir ~/whatsapp-server
cd ~/whatsapp-server

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
pip install flask flask-cors selenium webdriver-manager requests
```

---

## 📂 PASSO 3: Enviar Arquivos para VPS

### Opção A: Git (Recomendado)
```bash
cd ~/whatsapp-server
git clone https://github.com/SEU-USUARIO/Agendador-Barbearia.git .
```

### Opção B: SCP (Manual)
Na sua máquina local:
```bash
scp -r services/ usuario@seu-vps-ip:~/whatsapp-server/
scp whatsapp_api_server.py usuario@seu-vps-ip:~/whatsapp-server/
scp models.py database.py usuario@seu-vps-ip:~/whatsapp-server/
```

---

## 🔑 PASSO 4: Configurar Token de Segurança

No VPS, crie arquivo `.env`:

```bash
cd ~/whatsapp-server
nano .env
```

Adicione:
```env
WHATSAPP_API_TOKEN=sua-senha-super-secreta-aqui-123456
PORT=5001
```

**IMPORTANTE**: Use uma senha forte e única!

---

## 🚀 PASSO 5: Iniciar Servidor WhatsApp no VPS

### Primeira Vez (Escanear QR Code):

```bash
cd ~/whatsapp-server
source venv/bin/activate

# Iniciar com display virtual
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

python3 whatsapp_api_server.py
```

### Escanear QR Code via HTTP:

1. Acesse da sua máquina: `http://SEU-VPS-IP:5001`
2. Faça requisição POST para `/iniciar`:
   ```bash
   curl -X POST http://SEU-VPS-IP:5001/iniciar \
     -H "Authorization: Bearer sua-senha-super-secreta-aqui-123456"
   ```

3. **No VPS**, conecte via SSH com X11 forwarding para ver o Chrome:
   ```bash
   ssh -X usuario@seu-vps-ip
   ```

4. Ou use VNC Viewer para acessar interface gráfica do VPS

5. Escaneie o QR Code com seu WhatsApp

---

## 🔄 PASSO 6: Manter Servidor Rodando (systemd)

Criar serviço systemd para rodar automaticamente:

```bash
sudo nano /etc/systemd/system/whatsapp-api.service
```

Conteúdo:
```ini
[Unit]
Description=WhatsApp API Server
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/home/seu-usuario/whatsapp-server
Environment="DISPLAY=:99"
Environment="PATH=/home/seu-usuario/whatsapp-server/venv/bin"
ExecStartPre=/bin/sleep 5
ExecStartPre=/usr/bin/Xvfb :99 -screen 0 1920x1080x24
ExecStart=/home/seu-usuario/whatsapp-server/venv/bin/python3 whatsapp_api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ativar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-api
sudo systemctl start whatsapp-api
sudo systemctl status whatsapp-api
```

---

## ⚙️ PASSO 7: Configurar Site no Render

No painel do Render, adicione variáveis de ambiente:

1. Acesse seu Web Service
2. Vá em **Environment**
3. Adicione:

```env
WHATSAPP_API_URL=http://SEU-VPS-IP:5001
WHATSAPP_API_TOKEN=sua-senha-super-secreta-aqui-123456
```

4. Clique em **Save Changes**
5. Faça **Manual Deploy**

---

## ✅ PASSO 8: Testar

### Teste 1: Health Check
```bash
curl http://SEU-VPS-IP:5001/health
```

Resposta esperada:
```json
{
  "status": "online",
  "whatsapp_ativo": true
}
```

### Teste 2: Enviar Mensagem
```bash
curl -X POST http://SEU-VPS-IP:5001/enviar \
  -H "Authorization: Bearer sua-senha" \
  -H "Content-Type: application/json" \
  -d '{"numero": "5547991557386", "mensagem": "Teste de WhatsApp!"}'
```

### Teste 3: Criar Agendamento no Site
1. Acesse seu site no Render
2. Faça um agendamento de teste
3. Verifique se o WhatsApp foi enviado

---

## 🔒 Segurança

### 1. Firewall (UFW)
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 5001/tcp  # API WhatsApp
sudo ufw enable
```

### 2. HTTPS (Opcional mas Recomendado)
Instalar Nginx como proxy reverso com SSL:

```bash
sudo apt install nginx certbot python3-certbot-nginx -y

# Configurar domínio
sudo nano /etc/nginx/sites-available/whatsapp-api

# Adicionar:
server {
    listen 80;
    server_name api-whatsapp.seudominio.com;
    
    location / {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Ativar
sudo ln -s /etc/nginx/sites-available/whatsapp-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Obter certificado SSL
sudo certbot --nginx -d api-whatsapp.seudominio.com
```

Depois atualize no Render:
```env
WHATSAPP_API_URL=https://api-whatsapp.seudominio.com
```

---

## 📊 Monitoramento

### Ver logs:
```bash
# Logs do serviço
sudo journalctl -u whatsapp-api -f

# Logs da aplicação
tail -f ~/whatsapp-server/whatsapp_automation.log
```

### Verificar status:
```bash
sudo systemctl status whatsapp-api
```

### Reiniciar se necessário:
```bash
sudo systemctl restart whatsapp-api
```

---

## 💰 Custos Estimados

- **VPS Contabo**: €4-8/mês (~R$ 25-50/mês)
- **Domínio** (opcional): R$ 40/ano
- **Total**: ~R$ 25-50/mês

**Mais barato que Twilio** se enviar mais de 50 mensagens/mês!

---

## 🆘 Troubleshooting

### Erro: "Chrome not found"
```bash
google-chrome --version  # Verificar se instalou
which google-chrome      # Verificar localização
```

### Erro: "Display not found"
```bash
ps aux | grep Xvfb      # Verificar se Xvfb está rodando
export DISPLAY=:99       # Setar display
```

### WhatsApp desconecta
- Manter VPS ligado 24/7
- Verificar se sessão não expirou
- Reiniciar serviço: `sudo systemctl restart whatsapp-api`

### Mensagens não chegam
1. Verificar logs: `sudo journalctl -u whatsapp-api -f`
2. Testar API diretamente com curl
3. Verificar token de autenticação
4. Verificar firewall do VPS

---

## 📚 Próximos Passos

1. ✅ Configurar VPS
2. ✅ Instalar dependências
3. ✅ Subir servidor WhatsApp
4. ✅ Configurar variáveis no Render
5. ✅ Testar integração
6. 🔄 Monitorar e ajustar

Pronto! Seu sistema de WhatsApp está funcionando em produção! 🎉
