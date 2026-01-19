# 🚀 SETUP COMPLETO - COPIE E COLE

Este arquivo tem todos os comandos prontos para copiar e executar.

---

## ✅ CHECKLIST RÁPIDO

- [ ] Criar conta Oracle Cloud
- [ ] Criar VM Ubuntu 22.04
- [ ] Conectar via SSH
- [ ] Executar script de instalação
- [ ] Criar conta Supabase
- [ ] Copiar credenciais Supabase
- [ ] Colar .env na VM
- [ ] Testar conexão
- [ ] Migrar dados
- [ ] Configurar Render

---

## 1️⃣ SCRIPT DE INSTALAÇÃO ORACLE (Copie e Cole na VM)

```bash
cat > setup.sh << 'EOF'
#!/bin/bash
set -e

echo "================================================"
echo "🚀 INSTALANDO SERVIDOR COMPLETO"
echo "================================================"

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Python
echo "🐍 Instalando Python..."
sudo apt install -y python3 python3-pip python3-venv git

# Instalar Chrome
echo "🌐 Instalando Google Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y
rm google-chrome-stable_current_amd64.deb

# Instalar Xvfb
echo "🖥️ Instalando Xvfb..."
sudo apt install -y xvfb

# Instalar netfilter
sudo apt install -y iptables-persistent

# Criar diretório
mkdir -p ~/whatsapp-server
cd ~/whatsapp-server

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
pip install --upgrade pip
pip install flask flask-cors selenium webdriver-manager requests psycopg2-binary SQLAlchemy python-dotenv

echo "✅ Instalação concluída!"
EOF

chmod +x setup.sh
./setup.sh
```

---

## 2️⃣ ARQUIVO .env (Crie na VM após copiar credenciais)

**Substitua os `XXX` pelas suas credenciais Supabase!**

```bash
cat > ~/.env << 'EOF'
# WhatsApp API
WHATSAPP_API_TOKEN=sua-senha-aleatoria-de-32-caracteres
PORT=5001

# Banco de Dados Supabase
DATABASE_URL=postgresql://postgres:SUA-SENHA-SUPABASE@xxxxx.supabase.co:5432/postgres
SUPABASE_HOST=xxxxx.supabase.co
SUPABASE_PASSWORD=SUA-SENHA-SUPABASE

# Flask
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-flask
EOF
```

**Copie para o diretório certo:**
```bash
cp ~/.env ~/whatsapp-server/.env
```

---

## 3️⃣ SCRIPT SQL SUPABASE (Execute no SQL Editor Supabase)

Copie TUDO isso e execute no **SQL Editor** do Supabase:

```sql
-- Tabela de Barbeiros
CREATE TABLE IF NOT EXISTS barbeiros (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  telefone VARCHAR(20) NOT NULL UNIQUE,
  email VARCHAR(100),
  data_criacao TIMESTAMP DEFAULT NOW()
);

-- Tabela de Serviços
CREATE TABLE IF NOT EXISTS servicos (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  duracao_minutos INTEGER DEFAULT 30,
  preco DECIMAL(10,2),
  data_criacao TIMESTAMP DEFAULT NOW()
);

-- Tabela de Agendamentos
CREATE TABLE IF NOT EXISTS agendamentos (
  id SERIAL PRIMARY KEY,
  barbeiro_id INTEGER REFERENCES barbeiros(id),
  cliente_nome VARCHAR(100),
  cliente_telefone VARCHAR(20),
  data_agendamento TIMESTAMP,
  servico_id INTEGER REFERENCES servicos(id),
  status VARCHAR(20) DEFAULT 'pendente',
  data_criacao TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_agendamentos_data ON agendamentos(data_agendamento);
CREATE INDEX IF NOT EXISTS idx_agendamentos_barbeiro ON agendamentos(barbeiro_id);

-- Inserir dados de exemplo
INSERT INTO barbeiros (nome, telefone, email) VALUES
  ('João Silva', '5547991234567', 'joao@email.com'),
  ('Carlos Santos', '5547991234568', 'carlos@email.com');

INSERT INTO servicos (nome, duracao_minutos, preco) VALUES
  ('Corte de cabelo', 30, 50.00),
  ('Barba', 20, 30.00),
  ('Pacote Completo', 50, 70.00);

SELECT 'Tabelas criadas com sucesso!' as status;
```

---

## 4️⃣ SCRIPT DE MIGRAÇÃO DE DADOS (Execute na VM)

Se você já tem dados no SQLite:

```bash
cd ~/whatsapp-server
source venv/bin/activate

cat > migrar_dados.py << 'EOF'
import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    # Conexão SQLite (origem)
    sqlite_conn = sqlite3.connect('instance/barbearia.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Conexão PostgreSQL (destino)
    pg_conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    pg_cursor = pg_conn.cursor()
    
    print("🔄 Iniciando migração de dados...")
    
    # Barbeiros
    try:
        sqlite_cursor.execute("SELECT id, nome, telefone, email FROM barbeiros")
        barbeiros = sqlite_cursor.fetchall()
        for b in barbeiros:
            pg_cursor.execute(
                "INSERT INTO barbeiros (id, nome, telefone, email) VALUES (%s, %s, %s, %s) ON CONFLICT(id) DO NOTHING",
                b
            )
        pg_conn.commit()
        print(f"✅ {len(barbeiros)} barbeiros migrados!")
    except Exception as e:
        print(f"⚠️ Barbeiros: {e}")
    
    # Serviços
    try:
        sqlite_cursor.execute("SELECT id, nome, duracao_minutos, preco FROM servicos")
        servicos = sqlite_cursor.fetchall()
        for s in servicos:
            pg_cursor.execute(
                "INSERT INTO servicos (id, nome, duracao_minutos, preco) VALUES (%s, %s, %s, %s) ON CONFLICT(id) DO NOTHING",
                s
            )
        pg_conn.commit()
        print(f"✅ {len(servicos)} serviços migrados!")
    except Exception as e:
        print(f"⚠️ Serviços: {e}")
    
    # Agendamentos
    try:
        sqlite_cursor.execute("""
            SELECT id, barbeiro_id, cliente_nome, cliente_telefone, 
                   data_agendamento, servico_id, status 
            FROM agendamentos
        """)
        agendamentos = sqlite_cursor.fetchall()
        for a in agendamentos:
            pg_cursor.execute(
                """INSERT INTO agendamentos (id, barbeiro_id, cliente_nome, 
                   cliente_telefone, data_agendamento, servico_id, status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT(id) DO NOTHING""",
                a
            )
        pg_conn.commit()
        print(f"✅ {len(agendamentos)} agendamentos migrados!")
    except Exception as e:
        print(f"⚠️ Agendamentos: {e}")
    
    sqlite_conn.close()
    pg_conn.close()
    print("\n🎉 Migração concluída com sucesso!")
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
EOF

python3 migrar_dados.py
```

---

## 5️⃣ TESTE DE CONEXÃO (Execute na VM)

```bash
cd ~/whatsapp-server
source venv/bin/activate

cat > testar_bd.py << 'EOF'
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testando conexão com Supabase...")

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    # Teste 1: Conexão
    cursor.execute("SELECT NOW()")
    print(f"✅ Conectado! Hora do servidor: {cursor.fetchone()[0]}")
    
    # Teste 2: Contar barbeiros
    cursor.execute("SELECT COUNT(*) FROM barbeiros")
    count = cursor.fetchone()[0]
    print(f"✅ Barbeiros no banco: {count}")
    
    # Teste 3: Listar barbeiros
    cursor.execute("SELECT nome, telefone FROM barbeiros")
    for nome, tel in cursor.fetchall():
        print(f"  - {nome}: {tel}")
    
    conn.close()
    print("\n🎉 Tudo funcionando!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\n⚠️ Verifique:")
    print("  1. DATABASE_URL está correto no .env?")
    print("  2. Criou as tabelas no Supabase?")
    print("  3. Aguardou a criação da VM terminar?")
EOF

python3 testar_bd.py
```

---

## 6️⃣ CONFIGURAR FIREWALL ORACLE

```bash
# No console Oracle Cloud:
# Networking → Virtual Cloud Networks → VCN → Security Lists
# Add Ingress Rules para:

# Porta 5000 (Site)
# Source CIDR: 0.0.0.0/0
# Protocol: TCP
# Port: 5000

# Porta 5001 (WhatsApp API)
# Source CIDR: 0.0.0.0/0
# Protocol: TCP
# Port: 5001

# Depois execute na VM:
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 5000 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 5001 -j ACCEPT
sudo netfilter-persistent save
```

---

## 7️⃣ VARIÁVEIS PARA RENDER

Copie isso e cale em **Environment** do seu Web Service no Render:

```env
WHATSAPP_API_URL=http://SEU-IP-ORACLE-AQUI:5001
WHATSAPP_API_TOKEN=SENHA-QUE-VOCE-COPIOU
DATABASE_URL=postgresql://postgres:SUA-SENHA@xxxxx.supabase.co:5432/postgres
```

---

## 📝 INFORMAÇÕES IMPORTANTES

### Aonde encontrar cada informação:

**Oracle Cloud:**
- IP público: Menu ☰ → Compute → Instances → (seu nome) → "Primary VNIC public IP"
- Conectar SSH: `ssh -i chave.pem ubuntu@IP-PUBLICO`

**Supabase:**
- Credenciais: Project Settings → Database → Connection String
- Região: Escolher São Paulo para melhor latência
- URL: `https://xxxxx.supabase.co`

**Render:**
- Acessar em: https://render.com/dashboard
- Environment: Web Service → Settings → Environment

---

## 🆘 TROUBLESHOOTING

### Erro: "Connection refused" ao conectar no banco
```bash
# Verifique se as credenciais estão corretas
cat ~/whatsapp-server/.env

# Teste a conexão
cd ~/whatsapp-server && source venv/bin/activate && python3 testar_bd.py
```

### Chrome não acha display
```bash
# Reinicie o serviço
sudo systemctl restart whatsapp-api

# Veja logs
sudo journalctl -u whatsapp-api -f
```

### VM caiu
```bash
# Reconecte
ssh -i chave.pem ubuntu@IP-PUBLICO

# Reinicie serviço
sudo systemctl restart whatsapp-api
```

---

## ✅ CHECKLIST FINAL

- [ ] Oracle Cloud criado
- [ ] VM rodando
- [ ] Python/Chrome instalados
- [ ] Supabase criado
- [ ] Tabelas criadas
- [ ] .env configurado
- [ ] Conexão testada ✅
- [ ] Dados migrados ✅
- [ ] Firewall configurado
- [ ] Render configurado
- [ ] Agendamento feito com sucesso ✅
- [ ] WhatsApp enviado automaticamente ✅

🎉 **Pronto! Seu sistema está em produção!**
