# 🌐 COLOCAR EM PRODUÇÃO

## Pré-requisitos Checklist

- [ ] Servidor Oracle Cloud (ou outro host)
- [ ] Python 3.8+
- [ ] PostgreSQL ou SQLite
- [ ] Conexão HTTPS (opcional mas recomendado)

---

## 1️⃣ Preparar Arquivo de Configuração

Crie `.env` na raiz do projeto:

```bash
# Banco de Dados
DATABASE_URL=postgresql://user:password@host:5432/barbearia
# ou para SQLite:
DATABASE_URL=sqlite:///barbearia.db

# Flask
FLASK_ENV=production
SECRET_KEY=seu-segredo-super-seguro-aqui-trocar-em-producao
ADMIN_PASSWORD=123  # TROCAR EM PRODUÇÃO!

# WhatsApp (opcional)
TWILIO_ACCOUNT_SID=seu-account-sid
TWILIO_AUTH_TOKEN=seu-auth-token
TWILIO_PHONE_NUMBER=+55...

# API Security
WHATSAPP_API_TOKEN=gerar-um-token-aleatorio-seguro
```

---

## 2️⃣ Instalar Dependências

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate

# Instalar pacotes
pip install -r requirements.txt
```

---

## 3️⃣ Configurar Banco de Dados

```bash
# Em produção, recomendamos PostgreSQL + Supabase
# https://supabase.com (500MB grátis)

# Copiar URL do Supabase para .env:
DATABASE_URL=postgresql://postgres:senha@host.supabase.co:5432/postgres
```

---

## 4️⃣ Inicializar Horários (Primeira Vez)

```bash
python init_db.py
```

Saída esperada:
```
✅ Horários criados para os barbeiros!
```

---

## 5️⃣ Rodar Testes

```bash
python teste_performance.py
```

Todos os 4 testes devem passar com ✅

---

## 6️⃣ Executar em Produção

### Opção A: Gunicorn (Recomendado)

```bash
# Instalar gunicorn (já no requirements.txt)
pip install gunicorn

# Rodar com 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Com configurações avançadas
gunicorn \
  -w 4 \
  -b 0.0.0.0:5000 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  app:app
```

### Opção B: Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=postgresql://...
ENV SECRET_KEY=...

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Executar:
```bash
docker build -t barbearia-app .
docker run -e DATABASE_URL=... -p 5000:5000 barbearia-app
```

### Opção C: Systemd Service (Linux)

Criar arquivo `/etc/systemd/system/barbearia.service`:

```ini
[Unit]
Description=Barbearia App
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/app/barbearia
ExecStart=/home/app/barbearia/venv/bin/gunicorn \
  -w 4 \
  -b 127.0.0.1:5000 \
  app:app

Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ativar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable barbearia
sudo systemctl start barbearia
sudo systemctl status barbearia
```

---

## 7️⃣ Configurar Nginx (Proxy Reverso)

Arquivo: `/etc/nginx/sites-available/barbearia`

```nginx
upstream barbearia {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name seu-dominio.com;
    
    # Redirecionar HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com;
    
    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://barbearia;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Cache estática
    location /static {
        alias /home/app/barbearia/static;
        expires 30d;
    }
}
```

Ativar:
```bash
sudo ln -s /etc/nginx/sites-available/barbearia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 8️⃣ SSL com Let's Encrypt

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot certonly --standalone -d seu-dominio.com

# Renovação automática
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## 9️⃣ Monitoramento

### Ver Logs
```bash
# Systemd
sudo journalctl -u barbearia -f

# Gunicorn direct
tail -f logs/gunicorn.log
```

### Health Check
```bash
# Script para monitorar
curl https://seu-dominio.com/api/barbeiros
```

### Métricas
```bash
# Performance
watch -n 1 'curl -s https://seu-dominio.com/api/datas-disponiveis | jq .'
```

---

## 🔟 Backup do Banco

### PostgreSQL/Supabase
```bash
# Backup completo
pg_dump -h host.supabase.co -U postgres -d postgres > backup.sql

# Restaurar
psql -h host.supabase.co -U postgres -d postgres < backup.sql
```

### Automático (Cron)
```bash
0 2 * * * /home/app/barbearia/backup.sh
```

Arquivo `backup.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > \
  /backups/barbearia_$DATE.sql
gzip /backups/barbearia_$DATE.sql

# Manter últimos 30 dias
find /backups -mtime +30 -delete
```

---

## ⚠️ Checklist de Segurança

- [ ] Alterar `ADMIN_PASSWORD` em `.env`
- [ ] Usar HTTPS em produção
- [ ] Configurar firewall (porta 443 aberta)
- [ ] Criar backup do banco regularmente
- [ ] Usar variáveis de ambiente para secrets
- [ ] Manter dependências atualizadas: `pip list --outdated`
- [ ] Monitorar logs de erro regularmente
- [ ] Configurar rate limiting no Nginx
- [ ] Desabilitar debug mode: `FLASK_ENV=production`

---

## 🔐 Exemplo de Firewall (UFW)

```bash
# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP
sudo ufw allow 80/tcp

# Permitir HTTPS
sudo ufw allow 443/tcp

# Rejeitar tudo mais
sudo ufw default deny incoming
sudo ufw enable
```

---

## 📊 Performance em Produção

Métricas esperadas:

| Métrica | Valor |
|---------|-------|
| Tempo resposta API | 4-15ms |
| CPU por requisição | <5% |
| Memória base | ~50MB |
| Memória por worker | ~100MB |
| Max requisições/seg | 100+ |
| Cache hit rate | 99% |

---

## 🚨 Troubleshooting

### Erro de Conexão ao BD
```bash
# Verificar conexão
psql -h host.supabase.co -U postgres

# Verificar .env
cat .env | grep DATABASE_URL
```

### Site Lento
```bash
# Rodar testes
python teste_performance.py

# Aumentar workers
gunicorn -w 8 app:app
```

### Erro 502 Bad Gateway
```bash
# Verificar logs
sudo journalctl -u barbearia -n 50

# Reiniciar
sudo systemctl restart barbearia
```

---

## 📞 Suporte Remoto

Para acessar servidor:

```bash
# SSH
ssh user@seu-dominio.com

# Copiar arquivo
scp arquivo.txt user@seu-dominio.com:/app/

# Ver logs em tempo real
ssh user@seu-dominio.com 'tail -f /var/log/syslog'
```

---

## ✅ Validação Final

```bash
# Após deploy, testar:
curl https://seu-dominio.com/api/barbeiros
curl https://seu-dominio.com/api/barbeiro/1/horarios
curl https://seu-dominio.com/api/datas-disponiveis

# Todos devem retornar 200
```

---

**Pronto!** Seu site agora está em produção com performance otimizada! 🚀

---

**Data**: 19 de Janeiro de 2026
**Status**: ✅ Pronto para Deploy
**Performance**: ⚡ Otimizada
