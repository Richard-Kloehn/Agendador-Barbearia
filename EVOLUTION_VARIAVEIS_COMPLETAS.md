## VARIÁVEIS NECESSÁRIAS PARA EVOLUTION API v2.2.3

Verifique se TODAS essas variáveis estão configuradas no Railway (evolution-api service):

### OBRIGATÓRIAS:
```
AUTHENTICATION_API_KEY=Barber2026ApiKeySecret
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=postgresql://postgres:senha@postgres.railway.internal:5432/railway
```

### CACHE/REDIS:
```
CACHE_REDIS_ENABLED=true
CACHE_REDIS_URI=rediss://default:senha@vast-duckling-21251.upstash.io:6379
CACHE_REDIS_PREFIX_KEY=evolution
CACHE_REDIS_SAVE_INSTANCES=false
```

### CONFIGURAÇÕES IMPORTANTES (podem estar faltando):
```
SERVER_TYPE=http
SERVER_PORT=8080
DEL_INSTANCE=false
QRCODE_LIMIT=30
QRCODE_COLOR=#198754
```

### PROVIDER STORE (importante para QR Code):
```
PROVIDER_ENABLED=false
```
OU se quiser salvar arquivos:
```
PROVIDER_ENABLED=true
PROVIDER_NAME=local
```

### WEBHOOK (opcional mas recomendado):
```
WEBHOOK_GLOBAL_ENABLED=false
```

---

## TESTE:

Adicione essas variáveis que podem estar faltando:
1. `QRCODE_LIMIT=30`
2. `DEL_INSTANCE=false`
3. `PROVIDER_ENABLED=false`

Depois faça redeploy e teste novamente.
