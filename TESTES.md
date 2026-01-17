# ✅ Guia de Testes - Sistema de Barbearia

## 🧪 Testando o Sistema Localmente

### 1️⃣ Instalação Rápida (Primeiro Uso)

```bash
# Execute o instalador automático
setup.bat
```

Isso irá:
- ✅ Criar ambiente virtual
- ✅ Instalar dependências
- ✅ Criar arquivo .env
- ✅ Inicializar banco de dados

### 2️⃣ Iniciar o Servidor

```bash
# Execute o servidor
run.bat
```

Ou manualmente:
```bash
venv\Scripts\activate
python app.py
```

---

## 🔍 Roteiro de Testes

### TESTE 1: Página Inicial
1. Acesse: `http://localhost:5000`
2. ✅ Verificar: Interface carrega corretamente
3. ✅ Verificar: Design responsivo (redimensione a janela)
4. ✅ Verificar: Todos os ícones aparecem

### TESTE 2: Criar Agendamento

**Passo 1 - Dados do Cliente:**
1. Nome: `João Silva`
2. Telefone: `(11) 99999-8888`
3. Clique em "Continuar"
4. ✅ Validação: Campos obrigatórios funcionam
5. ✅ Máscara: Telefone formata automaticamente

**Passo 2 - Escolher Data:**
1. Selecione uma data futura (amanhã ou depois)
2. ✅ Verificar: Horários aparecem
3. ✅ Verificar: Não permite datas passadas
4. Selecione um horário (ex: 10:00)
5. Clique em "Continuar"

**Passo 3 - Confirmação:**
1. ✅ Verificar: Resumo exibe dados corretos
2. Adicione observação (opcional): `Cliente regular`
3. Clique em "Confirmar Agendamento"
4. ✅ Aguardar: Página de sucesso

**Resultado Esperado:**
- ✅ Mensagem de sucesso
- ✅ Opção de fazer novo agendamento

### TESTE 3: Painel Administrativo

1. Acesse: `http://localhost:5000/admin-dashboard`
2. ✅ Dashboard carrega
3. ✅ Estatísticas aparecem

**Testar Dashboard:**
- ✅ Conta total de agendamentos
- ✅ Agendamentos de hoje aparecem
- ✅ Cards de estatísticas

**Testar Gerenciar Agendamentos:**
1. Clique em "Agendamentos" no menu lateral
2. ✅ Tabela com todos os agendamentos
3. Teste filtros:
   - Filtrar por data
   - Filtrar por status
4. Altere status de um agendamento:
   - Selecione "Confirmar" no dropdown
5. ✅ Status atualiza

**Testar Configurações:**
1. Clique em "Configurações"
2. ✅ Formulário carrega com dados atuais
3. Altere:
   - Nome: `Minha Barbearia`
   - Horário abertura: `08:00`
   - Horário fechamento: `20:00`
   - Duração: `45` minutos
4. Clique em "Salvar"
5. ✅ Mensagem de sucesso

### TESTE 4: Horários Dinâmicos

1. Volte para página inicial: `http://localhost:5000`
2. Crie outro agendamento
3. Selecione mesma data do teste anterior
4. ✅ Verificar: Horário anterior NÃO aparece mais
5. ✅ Sistema bloqueia horários ocupados

### TESTE 5: Confirmação por Link

1. Acesse o banco de dados:
   - Abra `barbearia.db` com DB Browser for SQLite
   - Ou consulte via Python

2. Pegue um token de confirmação:
```bash
python
>>> from app import app, db
>>> from models import Agendamento
>>> with app.app_context():
...     ag = Agendamento.query.first()
...     print(ag.token_confirmacao)
```

3. Acesse: `http://localhost:5000/confirmar/[TOKEN]`
4. ✅ Página de confirmação carrega
5. Clique em "Confirmar Presença"
6. ✅ Mensagem de sucesso

---

## 🧪 Testes Avançados

### TESTE 6: Validações

**Data Passada:**
1. Tente selecionar ontem
2. ✅ Sistema não permite

**Horário Ocupado:**
1. Crie agendamento para 14:00
2. Tente criar outro para 14:00
3. ✅ Sistema retorna erro

**Dados Inválidos:**
1. Nome vazio → ✅ Erro
2. Telefone incompleto → ✅ Erro

### TESTE 7: Múltiplos Agendamentos

Crie 5 agendamentos diferentes:
```
1. João Silva - Amanhã 10:00
2. Maria Santos - Amanhã 11:00
3. Pedro Costa - Amanhã 14:00
4. Ana Lima - Depois de amanhã 09:00
5. Carlos Souza - Depois de amanhã 15:00
```

**Verificar:**
- ✅ Todos aparecem no admin
- ✅ Dashboard atualiza estatísticas
- ✅ Filtros funcionam corretamente

### TESTE 8: Horário de Almoço

1. Configure intervalo de almoço: 12:00 - 13:00
2. Tente agendar às 12:00 ou 12:30
3. ✅ Horários não aparecem como disponíveis

### TESTE 9: Dias de Funcionamento

1. Configure dias: Segunda a Sexta (0,1,2,3,4)
2. Tente selecionar um sábado ou domingo
3. ✅ Mensagem: "Barbearia fechada neste dia"

---

## 🔒 Testes de Segurança

### Token Único
1. Cada agendamento tem token diferente
2. ✅ Token não é previsível
3. ✅ Não aceita tokens inválidos

### Validação de Inputs
1. ✅ SQL Injection protegido (SQLAlchemy)
2. ✅ XSS protegido (templates Jinja2)
3. ✅ CORS configurado

---

## 📱 Testes Responsivos

### Desktop
1. Abra em navegador normal
2. ✅ Layout completo
3. ✅ Sidebar visível no admin

### Tablet
1. Redimensione para ~768px
2. ✅ Layout adapta
3. ✅ Grade de horários reorganiza

### Mobile
1. Abra em celular ou DevTools (F12)
2. ✅ Menu funciona
3. ✅ Botões clicáveis
4. ✅ Formulários usáveis
5. ✅ Grade de horários em 3 colunas

---

## 🚀 Testes de Performance

### Carga de Horários
1. Configure duração de 15 minutos
2. Horário: 08:00 - 20:00
3. ✅ Carrega rapidamente (< 1 segundo)

### Muitos Agendamentos
1. Crie 100+ agendamentos (script Python)
2. ✅ Admin continua responsivo
3. ✅ Filtros funcionam

---

## 📊 Checklist Completo

### Funcionalidades Básicas
- [ ] Página inicial carrega
- [ ] Formulário de agendamento funciona
- [ ] Validações funcionam
- [ ] Horários dinâmicos aparecem
- [ ] Confirmação de agendamento

### Painel Admin
- [ ] Dashboard carrega
- [ ] Estatísticas corretas
- [ ] Listar agendamentos
- [ ] Filtrar agendamentos
- [ ] Alterar status
- [ ] Configurações salvam

### Sistema de Confirmação
- [ ] Link de confirmação funciona
- [ ] Confirmar agendamento
- [ ] Cancelar agendamento
- [ ] Token seguro

### Responsividade
- [ ] Desktop OK
- [ ] Tablet OK
- [ ] Mobile OK

### Validações
- [ ] Dados obrigatórios
- [ ] Formato de telefone
- [ ] Data não passada
- [ ] Horário não duplicado
- [ ] Horário de almoço respeitado
- [ ] Dias de funcionamento

---

## 🐛 Problemas Comuns e Soluções

### "Nenhum horário disponível"
**Causa:** Todos os horários já agendados ou fora do horário de funcionamento
**Solução:** 
- Verificar configurações de horário
- Escolher outra data
- Limpar agendamentos antigos

### Estatísticas zeradas
**Causa:** Banco vazio
**Solução:** 
```bash
python init_db.py
# Escolha "s" para criar agendamentos de exemplo
```

### Admin não carrega agendamentos
**Causa:** Erro no JavaScript
**Solução:**
- Abra console do navegador (F12)
- Verifique erros
- Limpe cache (Ctrl+Shift+R)

### Erro ao salvar configuração
**Causa:** Formato de horário inválido
**Solução:** Use formato HH:MM (ex: 09:00)

---

## 🧪 Teste Automatizado (Opcional)

Crie `test_app.py`:

```python
import unittest
from app import app, db
from models import Agendamento
from datetime import datetime, timedelta

class TestBarbearia(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_criar_agendamento(self):
        amanha = datetime.now() + timedelta(days=1)
        data_hora = amanha.replace(hour=10, minute=0).isoformat()
        
        response = self.client.post('/api/agendar', json={
            'nome_cliente': 'Teste',
            'telefone': '11999999999',
            'data_hora': data_hora
        })
        
        self.assertEqual(response.status_code, 201)
    
    def test_horarios_disponiveis(self):
        amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(f'/api/horarios-disponiveis?data={amanha}')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

Execute:
```bash
python test_app.py
```

---

## ✅ Testes Concluídos!

Se todos os testes passaram, seu sistema está funcionando perfeitamente! 🎉

**Próximos Passos:**
1. Configure WhatsApp (opcional)
2. Personalize visual
3. Faça deploy online

**Precisa de ajuda?** Consulte:
- README.md - Documentação completa
- INSTALACAO.md - Guia de instalação
- PERSONALIZACAO.md - Customização

---

**BOA SORTE COM SUA BARBEARIA! 💈✨**
