# 🚀 GUIA RÁPIDO DE INSTALAÇÃO - Melhorias v2.0

## ⚡ Instalação Rápida (5 minutos)

### 1️⃣ Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2️⃣ Configurar Variáveis de Ambiente
Crie/edite o arquivo `.env` na raiz do projeto:

```env
# OBRIGATÓRIO - Configure estas variáveis
SECRET_KEY=cole-aqui-uma-chave-aleatoria-muito-longa-e-complexa-12345678
ADMIN_PASSWORD=SuaSenhaForteAqui123!

# Configurações de política
PRAZO_MINIMO_CANCELAMENTO_HORAS=2
PRAZO_MINIMO_REAGENDAMENTO_HORAS=2

# Banco de dados
DATABASE_URL=sqlite:///barbearia.db
```

**💡 Dica**: Para gerar uma SECRET_KEY forte:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3️⃣ Atualizar Banco de Dados
```bash
python atualizar_banco.py
```

### 4️⃣ Iniciar Aplicação
```bash
# Desenvolvimento
python app.py

# Produção
gunicorn app:app
```

---

## ✅ Checklist de Verificação

Antes de colocar em produção, confirme:

- [ ] Arquivo `.env` criado e configurado
- [ ] `SECRET_KEY` é uma string longa e aleatória (não use a de exemplo!)
- [ ] `ADMIN_PASSWORD` é forte (mínimo 8 caracteres, com números/símbolos)
- [ ] Script `atualizar_banco.py` foi executado sem erros
- [ ] Dependências instaladas com sucesso
- [ ] Aplicação inicia sem erros
- [ ] Login admin funciona com nova senha
- [ ] Favicon aparece na aba do navegador

---

## 🆕 O Que Mudou?

### Novas Funcionalidades Disponíveis:
✨ **Lista de Espera** - Cliente pode entrar na fila  
✨ **Avaliação** - Cliente avalia após o serviço  
✨ **Reagendamento** - Mudar data sem cancelar  
✨ **Galeria** - Fotos dos trabalhos  

### Melhorias de Segurança:
🔐 **Proteção CSRF** - Previne ataques  
🔐 **Rate Limiting** - Limita requisições  
🔐 **Validação** - Dados sempre validados  
🔐 **Senha Segura** - Agora via variável de ambiente  

### Melhorias de UX:
💅 **Validação em Tempo Real** - Erros mostrados ao digitar  
💅 **Loading States** - Feedback visual durante processamento  
💅 **Favicon** - Logo personalizado na aba  

---

## ⚠️ IMPORTANTE

### Não faça isso em produção:
❌ Usar `SECRET_KEY` padrão ou fraca  
❌ Usar senha `123` para admin  
❌ Deixar `.env` no repositório Git (já está no .gitignore)  
❌ Pular a execução do `atualizar_banco.py`  

### Sempre faça:
✅ Backup do banco antes de atualizar  
✅ Teste em ambiente local primeiro  
✅ Use senhas fortes  
✅ Mantenha `.env` privado  

---

## 🐛 Problemas Comuns

### "ModuleNotFoundError: No module named 'flask_wtf'"
**Solução**: Execute `pip install -r requirements.txt`

### "Admin login não funciona"
**Solução**: Verifique se `ADMIN_PASSWORD` está configurado no `.env`

### "Tabelas não encontradas"
**Solução**: Execute `python atualizar_banco.py`

### "SECRET_KEY warnings"
**Solução**: Configure uma SECRET_KEY forte no `.env`

---

## 📞 Suporte

Documentação completa: `MELHORIAS_IMPLEMENTADAS.md`

**Tudo pronto! Sua barbearia agora está mais profissional! 🎉**
