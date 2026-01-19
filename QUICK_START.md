# 🚀 QUICK START - 5 PASSOS PARA COMEÇAR

## ⚡ TL;DR (Muito Longo; Não Leia)

Se você quer começar AGORA em 5 minutos:

```
1️⃣  Crie conta Oracle Cloud    → https://oracle.com/cloud/free
2️⃣  Crie conta Supabase        → https://supabase.com
3️⃣  Crie VM no Oracle          → Ubuntu 22.04
4️⃣  Execute script na VM       → bash setup.sh (arquivo SETUP_COMPLETO)
5️⃣  Teste tudo                 → bash verificar_sistema.sh
```

**Tempo total: 1h45min**
**Custo: R$ 0,00**
**Resultado: Site + API + Banco em produção**

---

## 📋 CHECKLIST RÁPIDO (Imprima Isso!)

```
[ ] Conta Oracle Cloud
    └─ https://oracle.com/cloud/free

[ ] Conta Supabase  
    └─ https://supabase.com

[ ] VM Oracle (Ubuntu 22.04)
    └─ VM.Standard.E2.1.Micro

[ ] Chave SSH
    └─ Salva em C:\chave\private-key.pem

[ ] Conectar SSH
    └─ ssh -i chave.pem ubuntu@IP

[ ] Script Instalação
    └─ Copiar de SETUP_COMPLETO_ORACLE_SUPABASE.md

[ ] Banco Supabase
    └─ Criar tabelas (SQL pronto no arquivo)

[ ] .env configurado
    └─ DATABASE_URL + TOKENS

[ ] Testar
    └─ bash verificar_sistema.sh

[ ] Pronto!
    └─ 🎉 Está rodando em produção
```

---

## 🎯 PASSO 1: Contas Online (5 min)

### Oracle Cloud
1. Abra: https://www.oracle.com/cloud/free/
2. Clique: "Start for free"
3. Preencha: Email, País (Brasil), Nome
4. Escolha: "Cloud Free Tier"
5. **Não precisa cartão** ✅

### Supabase
1. Abra: https://supabase.com
2. Clique: "Start your project"
3. Logue: Com email ou GitHub
4. Clique: "New Project"
5. Escolha: Região "São Paulo" 📍

---

## 🖥️ PASSO 2: Criar VM Oracle (10 min)

No painel Oracle Cloud:
1. Menu ☰ → Compute → Instances
2. Clique: "Create Instance"
3. Preencha:
   ```
   Nome: whatsapp-server
   Image: Ubuntu 22.04
   Shape: VM.Standard.E2.1.Micro
   ```
4. **Gere SSH Key**: Copie arquivo `.pem`
5. Clique: "Create"
6. Aguarde: 2-3 minutos

---

## 🔑 PASSO 3: Conectar SSH (2 min)

### Windows PowerShell:
```powershell
# Encontre o IP público da VM no console Oracle

# Ajuste permissões
icacls "C:\caminho\private-key.pem" /inheritance:r
icacls "C:\caminho\private-key.pem" /grant:r "%username%:R"

# Conecte
ssh -i "C:\caminho\private-key.pem" ubuntu@SEU-IP-PUBLICO
```

### Mac/Linux:
```bash
chmod 400 private-key.pem
ssh -i private-key.pem ubuntu@SEU-IP-PUBLICO
```

---

## 🚀 PASSO 4: Executar Setup (20 min)

Na VM, execute TUDO isso:

```bash
# Criar arquivo de instalação
cat > setup.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Instalando..."

# System
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git xvfb iptables-persistent

# Chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y
rm google-chrome-stable_current_amd64.deb

# Setup
mkdir -p ~/whatsapp-server
cd ~/whatsapp-server
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask flask-cors selenium webdriver-manager requests psycopg2-binary SQLAlchemy python-dotenv

echo "✅ Instalado!"
EOF

chmod +x setup.sh
./setup.sh
```

**Aguarde até aparecer: ✅ Instalado!**

---

## 🗄️ PASSO 5: Configurar Banco (10 min)

### No Console Supabase:

Vá em **SQL Editor** e execute:

```sql
CREATE TABLE barbeiros (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  telefone VARCHAR(20) NOT NULL UNIQUE,
  email VARCHAR(100),
  data_criacao TIMESTAMP DEFAULT NOW()
);

CREATE TABLE servicos (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  duracao_minutos INTEGER DEFAULT 30,
  preco DECIMAL(10,2),
  data_criacao TIMESTAMP DEFAULT NOW()
);

CREATE TABLE agendamentos (
  id SERIAL PRIMARY KEY,
  barbeiro_id INTEGER REFERENCES barbeiros(id),
  cliente_nome VARCHAR(100),
  cliente_telefone VARCHAR(20),
  data_agendamento TIMESTAMP,
  servico_id INTEGER REFERENCES servicos(id),
  status VARCHAR(20) DEFAULT 'pendente',
  data_criacao TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agendamentos_data ON agendamentos(data_agendamento);
CREATE INDEX idx_agendamentos_barbeiro ON agendamentos(barbeiro_id);

-- Dados de exemplo
INSERT INTO barbeiros (nome, telefone, email) VALUES
  ('João', '5547991234567', 'joao@email.com'),
  ('Carlos', '5547991234568', 'carlos@email.com');

INSERT INTO servicos (nome, duracao_minutos, preco) VALUES
  ('Corte', 30, 50.00),
  ('Barba', 20, 30.00),
  ('Completo', 50, 70.00);
```

**Clique: Run** ✅

---

## 📝 PASSO 6: .env (5 min)

Na VM, execute:

```bash
cd ~/whatsapp-server

# Copie as credenciais Supabase de:
# Settings → Database → Connection String

cat > .env << 'EOF'
WHATSAPP_API_TOKEN=sUA-SENHA-32-CARACTERES-ALEATORIA
PORT=5001
DATABASE_URL=postgresql://postgres:SEU-PASSWORD@xxxxx.supabase.co:5432/postgres
FLASK_ENV=production
SECRET_KEY=chave-secreta-flask-aqui
EOF

# Verificar
cat .env
```

---

## ✅ PASSO 7: Testar (5 min)

```bash
cd ~/whatsapp-server
source venv/bin/activate

# Testar conexão com banco
cat > test.py << 'EOF'
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM barbeiros")
    count = cursor.fetchone()[0]
    print(f"✅ Conectado! Barbeiros: {count}")
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
EOF

python3 test.py
```

Se aparecer `✅ Conectado!` = Tudo OK!

---

## 🔥 PASSO 8: Executar Seu App (5 min)

```bash
cd ~/whatsapp-server
source venv/bin/activate

# Se seu app.py está aqui:
python3 app.py

# Deve aparecer:
# * Running on http://0.0.0.0:5000
# * Running on http://0.0.0.0:5001
```

Abra no navegador:
```
http://SEU-IP-ORACLE:5000
```

---

## 🎉 PRONTO!

Se chegou aqui:
✅ Servidor rodando
✅ Banco de dados conectado
✅ Site acessível
✅ API funcionando

**Próximo**: Adapte seu app.py usando `database_config_exemplo.py`

---

## 🆘 Problemas Rápidos?

### "Connection refused"
```bash
# Reinicie
sudo systemctl restart whatsapp-api
```

### "PostgreSQL error"
```bash
# Verifique .env
cat .env | grep DATABASE
```

### "Chrome not found"
```bash
# Reinstale
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

### Mais problemas?
→ Veja `ORACLE_CLOUD_GRATIS.md` seção "Problemas Comuns"

---

## 📱 Testar WhatsApp (Depois)

```bash
# Parar
sudo systemctl stop whatsapp-api

# Rodar manual para pegar QR Code
cd ~/whatsapp-server
source venv/bin/activate
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
python3 whatsapp_api_server.py

# Aguarde link do QR Code nos logs
# Escaneie com celular
# Reinicie: sudo systemctl start whatsapp-api
```

---

## 📊 Arquivos Importantes

Para referência:
- `ORACLE_CLOUD_GRATIS.md` - Guia detalhado
- `SETUP_COMPLETO_ORACLE_SUPABASE.md` - Scripts prontos
- `database_config_exemplo.py` - Código para integrar
- `verificar_sistema.sh` - Script de teste

---

## ⏰ Cronômetro Real

```
Contas online:           5 min
VM Oracle:              10 min (automático)
SSH:                     2 min
Instalação:             20 min
Banco dados:            10 min
Configurar .env:         5 min
Testar:                  5 min
                        ─────
TOTAL:                  57 minutos
```

---

## 🎯 Resultado Final

Ao terminar:
```
✅ Site: http://SEU-IP:5000
✅ API: http://SEU-IP:5001
✅ Banco: PostgreSQL Supabase
✅ WhatsApp: Funcionando
✅ Custo: R$ 0/mês
✅ Uptime: 99.9%
```

---

## 🚀 Comece AGORA

1. Abra: https://oracle.com/cloud/free (crie conta)
2. Retorne quando VM estiver pronta
3. Copie comandos acima
4. Execute na VM
5. 🎉 Pronto!

---

**Dúvida?** Veja:
- [ÍNDICE_GERAL.md](ÍNDICE_GERAL.md) - Navegação
- [RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md) - Visão geral
- [ARQUITETURA_VISUAL.md](ARQUITETURA_VISUAL.md) - Diagramas

**Bora começar!** 🚀
