# 🎨 Guia de Personalização

Este guia mostra como personalizar o visual e funcionalidades do sistema.

---

## 🎨 Personalizando Cores

### Método 1: Cores do Gradiente Principal

Abra `templates/index.html` e localize:

```css
.gradient-bg {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

**Opções de cores sugeridas:**

```css
/* Azul Moderno */
background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);

/* Verde Profissional */
background: linear-gradient(135deg, #10b981 0%, #047857 100%);

/* Vermelho Elegante */
background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%);

/* Laranja Vibrante */
background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);

/* Roxo/Rosa */
background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);

/* Dourado/Amarelo */
background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
```

### Método 2: Botões e Elementos

Localize `.btn-primary`:

```css
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

Use a mesma cor do gradiente principal para consistência.

---

## 🏪 Personalizando Textos

### Nome da Barbearia

**No HTML (templates/index.html):**
```html
<h1 class="text-4xl md:text-5xl font-bold mb-2">
    <i class="fas fa-cut mr-3"></i>Barbearia Style  <!-- MUDE AQUI -->
</h1>
```

**Ou configure pelo Painel Admin:**
1. Acesse `/admin-dashboard`
2. Vá em "Configurações"
3. Altere "Nome da Barbearia"

### Slogan/Descrição

```html
<p class="text-lg opacity-90">Agende seu horário de forma rápida e fácil</p>
<!-- Mude para: -->
<p class="text-lg opacity-90">O melhor corte da cidade</p>
```

---

## ⏰ Configurando Horários

### Pelo Painel Admin (Recomendado)

1. Acesse `/admin-dashboard`
2. Clique em "Configurações"
3. Configure:
   - Horário de abertura (ex: 08:00)
   - Horário de fechamento (ex: 20:00)
   - Duração do atendimento (ex: 30 minutos)
   - Intervalo de almoço (opcional)

### Direto no Código (models.py)

Abra `models.py` e modifique os valores padrão:

```python
config = ConfiguracaoBarbearia(
    nome_barbearia="Barbearia Style",
    horario_abertura="09:00",  # MUDE AQUI
    horario_fechamento="19:00",  # MUDE AQUI
    duracao_atendimento=30,  # Minutos por atendimento
    intervalo_almoco_inicio="12:00",  # OPCIONAL
    intervalo_almoco_fim="13:00",  # OPCIONAL
    dias_funcionamento="0,1,2,3,4,5"  # 0=seg, 6=dom
)
```

**Dias de Funcionamento:**
- `"0,1,2,3,4,5"` = Segunda a Sábado
- `"0,1,2,3,4,5,6"` = Segunda a Domingo
- `"0,1,2,3,4"` = Segunda a Sexta
- `"1,3,5"` = Terça, Quinta e Sábado

---

## 🎭 Mudando Ícones

O sistema usa Font Awesome. Veja opções em: https://fontawesome.com/icons

### Exemplo: Mudar ícone da tesoura

```html
<!-- Atual -->
<i class="fas fa-cut mr-3"></i>

<!-- Alternativas para barbearia -->
<i class="fas fa-scissors mr-3"></i>
<i class="fas fa-shaving-razor mr-3"></i>
<i class="fas fa-mustache mr-3"></i>
```

---

## 📱 Personalizando Mensagens do WhatsApp

Abra `services/whatsapp_service.py`:

### Mensagem de Lembrete

```python
mensagem = f"""
Olá {agendamento.nome_cliente}! 👋

Este é um lembrete do seu agendamento na barbearia:

📅 Data: {data_formatada}

Por favor, confirme sua presença acessando:
{url_confirmacao}

Se não puder comparecer, cancele pelo mesmo link.

Obrigado! ✂️
""".strip()
```

**Personalize como preferir:**

```python
mensagem = f"""
E aí, {agendamento.nome_cliente}! 😎

Seu horário tá chegando:
🗓️ {data_formatada}

Confirma aí: {url_confirmacao}

Tmj! 🔥
""".strip()
```

### Mensagem de Confirmação

Localize a função `enviar_confirmacao_agendamento` e personalize:

```python
mensagem = f"""
✅ Tudo certo!

Seu horário está marcado:
📅 {data_formatada}

Te esperamos! ✂️
""".strip()
```

---

## 🌐 Adicionando Logo

### 1. Adicione a imagem do logo

Crie uma pasta `static` e coloque sua logo:
```
static/
  └─ img/
      └─ logo.png
```

### 2. No HTML

Substitua o ícone por uma imagem em `templates/index.html`:

```html
<!-- Antes -->
<h1 class="text-4xl md:text-5xl font-bold mb-2">
    <i class="fas fa-cut mr-3"></i>Barbearia Style
</h1>

<!-- Depois -->
<div class="flex items-center justify-center mb-2">
    <img src="/static/img/logo.png" alt="Logo" class="h-16 mr-3">
    <h1 class="text-4xl md:text-5xl font-bold">Barbearia Style</h1>
</div>
```

### 3. Configure a rota estática

No `app.py`, adicione (já está configurado):

```python
app = Flask(__name__, static_folder='static')
```

---

## 🎯 Adicionando Favicon

Crie `static/favicon.ico` e adicione no `<head>` de todos os templates:

```html
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
```

---

## 🔧 Customizações Avançadas

### Adicionar Campo de Serviço

1. **Atualize o modelo (models.py):**

```python
class Agendamento(db.Model):
    # ... campos existentes ...
    tipo_servico = db.Column(db.String(50), default='corte')  # NOVO
```

2. **Adicione no formulário (templates/index.html):**

```html
<div>
    <label class="block text-sm font-semibold text-gray-700 mb-2">
        <i class="fas fa-scissors mr-2 text-purple-600"></i>Serviço
    </label>
    <select id="servico" 
        class="w-full px-4 py-3 rounded-xl border-2 border-gray-200">
        <option value="corte">Corte de Cabelo</option>
        <option value="barba">Barba</option>
        <option value="corte_barba">Corte + Barba</option>
        <option value="outros">Outros</option>
    </select>
</div>
```

3. **Atualize a função de agendamento no JavaScript:**

```javascript
tipo_servico: document.getElementById('servico').value
```

4. **Recrie o banco:**

```bash
# Backup do banco atual
copy barbearia.db barbearia_backup.db

# Delete e recrie
del barbearia.db
python init_db.py
```

### Adicionar Múltiplos Barbeiros

Similar ao processo acima, adicione:

```python
class Barbeiro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    ativo = db.Column(db.Boolean, default=True)

class Agendamento(db.Model):
    # ... campos existentes ...
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiro.id'))
```

---

## 🎨 Temas Prontos

### Tema Escuro

Adicione ao CSS (dentro da tag `<style>`):

```css
body.dark-mode {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

body.dark-mode .glass-effect {
    background: rgba(30, 30, 46, 0.95);
    color: white;
}

body.dark-mode input,
body.dark-mode select {
    background: #2a2a3e;
    color: white;
    border-color: #444;
}
```

Adicione botão de toggle no header:

```html
<button onclick="toggleDarkMode()" class="...">
    <i class="fas fa-moon"></i>
</button>

<script>
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', 
        document.body.classList.contains('dark-mode')
    );
}

// Carregar preferência
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}
</script>
```

---

## 📝 Checklist de Personalização

- [ ] Alterar nome da barbearia
- [ ] Mudar cores do tema
- [ ] Configurar horários de funcionamento
- [ ] Personalizar mensagens do WhatsApp
- [ ] Adicionar logo (opcional)
- [ ] Adicionar favicon (opcional)
- [ ] Configurar dias de funcionamento
- [ ] Definir duração dos atendimentos
- [ ] Personalizar textos e slogans
- [ ] Testar em dispositivos móveis

---

## 💡 Dicas de Design

1. **Consistência**: Use as mesmas cores em todos os elementos
2. **Contraste**: Garanta boa legibilidade
3. **Simplicidade**: Menos é mais, não sobrecarregue
4. **Responsividade**: Teste em celular e desktop
5. **Velocidade**: Evite muitas imagens pesadas

---

## 🆘 Precisa de Ajuda?

Se precisar de mais personalizações complexas:
1. Consulte o README.md
2. Abra uma issue no GitHub
3. Entre em contato por email

**Boa personalização! 🎨**
