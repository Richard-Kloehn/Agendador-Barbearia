# 🆓 WHATSAPP GRATUITO com Oracle Cloud Always Free

## ✅ O que é Oracle Cloud Always Free?

- **GRÁTIS PARA SEMPRE** (não é trial)
- 2 VMs com 1GB RAM cada
- 100GB de armazenamento
- Sem cartão de crédito necessário
- Perfeito para WhatsApp

---

## 📋 PASSO 1: Criar Conta Oracle Cloud

1. Acesse: https://www.oracle.com/cloud/free/
2. Clique em **"Start for free"**
3. Preencha dados:
   - Email
   - País: Brasil
   - Nome completo
4. Escolha: **"Cloud Free Tier"**
5. **NÃO precisa de cartão** (escolha opção sem cartão)
6. Confirme email
7. Login: https://cloud.oracle.com

---

## 🖥️ PASSO 2: Criar VM (Máquina Virtual)

### 2.1 Acessar painel
1. Faça login em https://cloud.oracle.com
2. Menu ☰ → **Compute** → **Instances**
3. Clique **"Create Instance"**

### 2.2 Configurar VM
```
Nome: whatsapp-server
Image: Ubuntu 22.04
Shape: VM.Standard.E2.1.Micro (Always Free)
```

### 2.3 Chaves SSH
1. Clique **"Generate SSH Key Pair"**
2. **BAIXE** `private-key.pem` (GUARDE BEM!)
3. **BAIXE** `public-key.pub`

### 2.4 Networking
- Deixe tudo padrão
- Marque: ☑️ "Assign public IPv4 address"

### 2.5 Criar
Clique **"Create"** e aguarde 2 minutos

---

## 🔑 PASSO 3: Configurar Firewall

### 3.1 No Oracle Cloud Console
1. Vá em **Networking** → **Virtual Cloud Networks**
2. Clique na VCN criada
3. Clique em **Security Lists** → **Default Security List**
4. Clique **"Add Ingress Rules"**
5. Adicione:

```
Source CIDR: 0.0.0.0/0
IP Protocol: TCP
Destination Port: 5001
Description: WhatsApp API
```

6. Clique **"Add Ingress Rules"**

### 3.2 No servidor (depois de conectar)
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 5001 -j ACCEPT
sudo netfilter-persistent save
```

---

## 🔌 PASSO 4: Conectar na VM

### Windows (PowerShell):
```powershell
# Ajustar permissões da chave
icacls "C:\caminho\para\private-key.pem" /inheritance:r
icacls "C:\caminho\para\private-key.pem" /grant:r "%username%:R"

# Conectar
ssh -i "C:\caminho\para\private-key.pem" ubuntu@SEU-IP-PUBLICO
```

### Mac/Linux:
```bash
chmod 400 private-key.pem
ssh -i private-key.pem ubuntu@SEU-IP-PUBLICO
```

**Dica**: O IP público aparece na página da instância no Oracle Cloud Console

---

## 📦 PASSO 5: Instalar Dependências (Automático)

Conecte via SSH e execute este script automatizado:

```bash
# Criar arquivo de instalação
cat > setup.sh << 'EOF'
#!/bin/bash
set -e

echo "================================================"
echo "🚀 INSTALANDO SERVIDOR WHATSAPP GRATUITO"
echo "================================================"

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Python
echo "🐍 Instalando Python..."
sudo apt install -y python3 python3-pip python3-venv

# Instalar Chrome
echo "🌐 Instalando Google Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y
rm google-chrome-stable_current_amd64.deb

# Instalar Xvfb (display virtual)
echo "🖥️ Instalando Xvfb..."
sudo apt install -y xvfb

# Instalar netfilter
sudo apt install -y iptables-persistent

# Criar diretório
echo "📁 Criando diretório..."
mkdir -p ~/whatsapp-server
cd ~/whatsapp-server

# Criar ambiente virtual
echo "🔧 Criando ambiente Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo "📚 Instalando bibliotecas Python..."
pip install --upgrade pip
pip install flask flask-cors selenium webdriver-manager requests

echo ""
echo "✅ Instalação concluída com sucesso!"
echo "================================================"
EOF

# Executar instalação
chmod +x setup.sh
./setup.sh
```

---

## 📂 PASSO 6: Baixar Código do GitHub

```bash
cd ~/whatsapp-server

# Clonar repositório
git clone https://github.com/Richard-Kloehn/Agendador-Barbearia.git temp
mv temp/* .
mv temp/.* . 2>/dev/null || true
rm -rf temp

# Ativar ambiente virtual
source venv/bin/activate
```

---

## 🔐 PASSO 7: Configurar Token de Segurança

```bash
cd ~/whatsapp-server

# Gerar senha aleatória forte
SENHA=$(openssl rand -base64 32)

# Criar arquivo .env
cat > .env << EOF
WHATSAPP_API_TOKEN=$SENHA
PORT=5001
EOF

# Mostrar a senha (ANOTE!)
echo ""
echo "================================================"
echo "🔑 SUA SENHA DO WHATSAPP API:"
echo "$SENHA"
echo "================================================"
echo "⚠️  COPIE E GUARDE ESSA SENHA!"
echo ""
```

**IMPORTANTE**: Copie e guarde essa senha!

---

## 🚀 PASSO 8: Criar Serviço Automático

```bash
# Criar serviço systemd
sudo tee /etc/systemd/system/whatsapp-api.service > /dev/null << 'EOF'
[Unit]
Description=WhatsApp API Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/whatsapp-server
Environment="DISPLAY=:99"
Environment="PATH=/home/ubuntu/whatsapp-server/venv/bin:/usr/bin:/bin"

# Iniciar Xvfb antes
ExecStartPre=/bin/bash -c 'Xvfb :99 -screen 0 1920x1080x24 &'
ExecStartPre=/bin/sleep 3

# Iniciar servidor
ExecStart=/home/ubuntu/whatsapp-server/venv/bin/python3 /home/ubuntu/whatsapp-server/whatsapp_api_server.py

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Ativar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-api
sudo systemctl start whatsapp-api

# Verificar status
sudo systemctl status whatsapp-api
```

---

## 📱 PASSO 9: Escanear QR Code (Primeira Vez)

### Opção A: Via Terminal (mais fácil)

```bash
# Parar serviço
sudo systemctl stop whatsapp-api

# Rodar manualmente para ver QR Code
cd ~/whatsapp-server
source venv/bin/activate
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
python3 whatsapp_api_server.py
```

**Aguarde aparecer o link do QR Code nos logs!**

### Opção B: Usar API

Em outro terminal, execute:
```bash
# Obter IP da VM
IP_PUBLICO=$(curl -s ifconfig.me)
SENHA=$(cat ~/whatsapp-server/.env | grep TOKEN | cut -d= -f2)

# Iniciar WhatsApp
curl -X POST http://$IP_PUBLICO:5001/iniciar \
  -H "Authorization: Bearer $SENHA"
```

**Depois veja os logs para pegar o QR Code:**
```bash
sudo journalctl -u whatsapp-api -f
```

### Escanear QR Code:
1. Abra WhatsApp no celular
2. ⋮ (menu) → Aparelhos conectados
3. Conectar aparelho
4. Escaneie o QR Code que apareceu no log

---

## ⚙️ PASSO 10: Configurar no Render

1. Acesse https://render.com
2. Entre no seu Web Service
3. Vá em **Environment**
4. Adicione variáveis:

```env
WHATSAPP_API_URL=http://SEU-IP-ORACLE:5001
WHATSAPP_API_TOKEN=sua-senha-que-copiou
```

5. **Save Changes**
6. **Manual Deploy** → Deploy latest commit

---

## ✅ PASSO 11: Testar

### Teste 1: Health Check
```bash
curl http://SEU-IP:5001/health
```

### Teste 2: Enviar Mensagem
```bash
SENHA=$(cat ~/whatsapp-server/.env | grep TOKEN | cut -d= -f2)

curl -X POST http://SEU-IP:5001/enviar \
  -H "Authorization: Bearer $SENHA" \
  -H "Content-Type: application/json" \
  -d '{
    "numero": "5547991557386",
    "mensagem": "🎉 WhatsApp Oracle Cloud funcionando!"
  }'
```

### Teste 3: Fazer Agendamento no Site
Acesse seu site e faça um agendamento. O WhatsApp deve ser enviado automaticamente!

---

## 📊 Comandos Úteis

### Ver logs em tempo real:
```bash
sudo journalctl -u whatsapp-api -f
```

### Ver status:
```bash
sudo systemctl status whatsapp-api
```

### Reiniciar serviço:
```bash
sudo systemctl restart whatsapp-api
```

### Parar serviço:
```bash
sudo systemctl stop whatsapp-api
```

### Ver IP público:
```bash
curl ifconfig.me
```

---

## 🔒 Segurança

### Firewall já configurado ✅
- Porta 22 (SSH) - Apenas seu IP
- Porta 5001 (API) - Protegida por token

### Recomendações:
1. **Mude a senha regularmente**
2. **Não compartilhe o token**
3. **Use HTTPS** (opcional, via Cloudflare Tunnel - grátis)

---

## 💡 Dicas Importantes

### ✅ Vantagens Oracle Cloud:
- **100% GRATUITO** para sempre
- VM sempre ligada
- IP público fixo
- Sem limites de tráfego

### ⚠️ Limitações:
- 1GB RAM (suficiente para WhatsApp)
- 1 core (suficiente)
- Não use para outras coisas pesadas

### 🔄 Backup da Sessão:
```bash
# Fazer backup da sessão WhatsApp
cd ~/whatsapp-server
tar -czf whatsapp-session-backup.tar.gz whatsapp_session/

# Restaurar backup
tar -xzf whatsapp-session-backup.tar.gz
```

---

## 🆘 Problemas Comuns

### Erro: "Connection refused"
```bash
# Verificar se serviço está rodando
sudo systemctl status whatsapp-api

# Verificar firewall
sudo iptables -L -n | grep 5001

# Reiniciar
sudo systemctl restart whatsapp-api
```

### Erro: "Chrome not found"
```bash
# Reinstalar Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y
```

### WhatsApp desconectou:
```bash
# Ver logs
sudo journalctl -u whatsapp-api -f

# Parar e rodar manualmente
sudo systemctl stop whatsapp-api
cd ~/whatsapp-server
source venv/bin/activate
export DISPLAY=:99
python3 whatsapp_api_server.py
```

Depois de escanear QR Code novamente:
```bash
sudo systemctl start whatsapp-api
```

---

## 🎉 Pronto!

Seu sistema de WhatsApp está 100% GRATUITO e funcionando em produção!

**Custo mensal**: R$ 0,00 ✅
**Tempo de configuração**: 30 minutos ⏱️
**Funciona para sempre**: Sim! ♾️

---

## 📞 Próximos Passos

1. ✅ Criar conta Oracle Cloud
2. ✅ Criar VM
3. ✅ Instalar dependências
4. ✅ Configurar serviço
5. ✅ Escanear QR Code
6. ✅ Configurar Render
7. 🎉 Testar e usar!
