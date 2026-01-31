# 📍 Onde Configurar Redes Sociais, Contatos e Endereço

## 🎯 Localização no Sistema

As informações de **contato, redes sociais e endereço** da barbearia estão em **2 lugares**:

---

## 1️⃣ PAINEL ADMINISTRATIVO (Recomendado) ⚙️

### Como acessar:
1. Acesse: `http://127.0.0.1:5000/admin-login`
2. Senha: `123`
3. Menu lateral → **"Contato/Redes"** (ícone de cartão)

### O que pode configurar:
✅ **Contato:**
- Telefone
- WhatsApp (número com DDI, ex: 5511999999999)
- Email

✅ **Redes Sociais:**
- Instagram
- Facebook
- TikTok (opcional)

✅ **Endereço:**
- Rua/Avenida
- Bairro
- Cidade
- CEP
- Link do Google Maps

✅ **Horários de Funcionamento:**
- Segunda a Sexta
- Sábado
- Domingo
- Feriados

### Botões:
- **Salvar Informações**: Grava no banco de dados
- **Resetar**: Volta aos valores padrão

---

## 2️⃣ SITE CLIENTE (Visualização) 👀

### Onde aparece:
- **Footer (Rodapé)** do site: `http://127.0.0.1:5000/`
- Rola a página até o final

### O que é exibido:
📞 **Coluna 1 - Contato:**
- Telefone (clicável para ligar)
- WhatsApp (clicável para abrir conversa)
- Email (clicável para enviar email)

📱 **Coluna 2 - Redes Sociais:**
- Botões redondos com ícones:
  - Instagram (roxo/rosa)
  - Facebook (azul)
  - WhatsApp (verde)
- Mensagem: "Siga-nos nas redes sociais!"

📍 **Coluna 3 - Endereço:**
- Rua, Bairro, Cidade, CEP
- Link "Ver no mapa" (abre Google Maps)

⏰ **Horários de Funcionamento:**
- Grid com 4 colunas:
  - Segunda a Sexta
  - Sábado
  - Domingo
  - Feriados

📝 **Copyright:**
- "© 2026 Barbearia. Todos os direitos reservados."

---

## 📂 Arquivos Envolvidos

### Frontend:
**`templates/index.html`** (linhas 458-569):
```html
<footer class="bg-gradient-to-r from-gray-900 to-gray-800 text-white py-8 mt-12">
    <!-- Contato, Redes Sociais, Endereço, Horários -->
</footer>
```

**`templates/admin.html`** (nova seção):
```html
<section id="secao-contato" class="secao hidden">
    <!-- Formulário de configuração -->
</section>
```

### Backend (A implementar):
**`routes.py`** - Criar rotas:
- `GET /api/configuracoes/contato` - Busca informações salvas
- `POST /api/configuracoes/contato` - Salva informações

**`models.py`** - Já existe modelo `ConfiguracaoGeral`:
- Salvar como pares chave-valor:
  - `contato_telefone` → `(11) 99999-9999`
  - `contato_whatsapp` → `5511999999999`
  - `contato_email` → `contato@barbearia.com`
  - `redes_instagram` → `https://instagram.com/...`
  - etc.

---

## 🚀 Como Usar

### Passo a Passo:

1. **Acesse o Admin:**
   ```
   http://127.0.0.1:5000/admin-login
   ```

2. **Faça login:**
   - Senha: `123`

3. **Clique em "Contato/Redes"** no menu lateral

4. **Preencha os campos:**
   - Telefone: `(11) 91234-5678`
   - WhatsApp: `5511912345678`
   - Email: `seuemail@barbearia.com`
   - Instagram: `https://instagram.com/suabarbearia`
   - Facebook: `https://facebook.com/suabarbearia`
   - Endereço completo
   - Horários de funcionamento

5. **Clique em "Salvar Informações"**

6. **Verifique no site:**
   ```
   http://127.0.0.1:5000/
   ```
   - Role até o footer
   - Veja as informações atualizadas

---

## ⚡ Funcionalidades Extras

### Links Clicáveis:
- **Telefone**: Abre app de ligação no celular
- **WhatsApp**: Abre conversa no WhatsApp Web
- **Email**: Abre cliente de email
- **Google Maps**: Abre localização no Google Maps

### Responsivo:
- **Desktop**: 3 colunas lado a lado
- **Mobile**: 1 coluna (empilhado)

### Visual:
- Fundo degradê cinza escuro
- Texto branco
- Ícones Font Awesome
- Botões de redes sociais coloridos com hover scale

---

## 🎨 Cores dos Botões de Redes Sociais

| Rede Social | Cor | Classe CSS |
|------------|-----|------------|
| Instagram | Roxo/Rosa Gradiente | `from-purple-600 to-pink-600` |
| Facebook | Azul | `bg-blue-600` |
| WhatsApp | Verde | `bg-green-500` |

---

## 📝 Valores Padrão (Exemplo)

Se você não configurar, aparece:

**Contato:**
- Telefone: `(11) 99999-9999`
- WhatsApp: `5511999999999`
- Email: `contato@barbearia.com`

**Redes:**
- Instagram: `https://instagram.com/suabarbearia`
- Facebook: `https://facebook.com/suabarbearia`

**Endereço:**
- `Rua Exemplo, 123`
- `Bairro Centro`
- `São Paulo - SP`
- `CEP: 01234-567`

**Horários:**
- Segunda a Sexta: `09:00 - 19:00`
- Sábado: `09:00 - 17:00`
- Domingo: `Fechado`
- Feriados: `Consulte`

---

## ✅ Resumo

**Para CONFIGURAR:**
👉 Painel Admin → Menu "Contato/Redes"

**Para VISUALIZAR:**
👉 Site Cliente → Role até o Footer (rodapé)

**Dados salvos em:**
👉 Banco de dados (`configuracao_geral`)

**Aparece em:**
👉 Rodapé de TODAS as páginas do site cliente

---

## 🔧 Próximos Passos (Opcional)

Se quiser adicionar mais funcionalidades:

1. **Google Analytics**: ID de rastreamento
2. **Pixel do Facebook**: ID do pixel
3. **Messenger/Chat**: Link do Facebook Messenger
4. **YouTube**: Link do canal
5. **Twitter/X**: Link do perfil

Basta adicionar mais campos no formulário admin e no footer!
