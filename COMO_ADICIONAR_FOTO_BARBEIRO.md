# Como Adicionar Foto do Barbeiro

## 🎯 Existem 2 formas de adicionar foto do barbeiro:

### 📤 Método 1: Upload de Arquivo (Recomendado)

1. **Acesse o Painel Admin**
   - Faça login no painel administrativo
   - Clique em "Barbeiros" no menu lateral

2. **Adicionar/Editar Barbeiro**
   - Clique em "Novo Barbeiro" ou no ícone de editar de um barbeiro existente
   - No formulário, você verá uma seção "Foto do Barbeiro"

3. **Selecionar a Foto**
   - Clique no botão "Selecionar Foto" (área com ícone de upload)
   - Escolha uma imagem do seu computador
   - Você verá um preview da foto instantaneamente

4. **Formatos Aceitos**
   - JPG, JPEG, PNG, GIF, WEBP
   - Tamanho máximo: 5MB
   - Recomendado: fotos quadradas (500x500px ou maior)

5. **Salvar**
   - Preencha os outros campos (nome, serviços, etc.)
   - Clique em "Salvar"
   - A foto será automaticamente enviada para: `static/img/barbeiros/`

### 🔗 Método 2: URL de Imagem Online

Se você tem a foto hospedada online (ex: Imgur, Google Drive público, etc.):

1. No mesmo formulário de barbeiro
2. Cole a URL completa da imagem no campo abaixo de "OU"
   - Exemplo: `https://exemplo.com/foto-barbeiro.jpg`
3. A imagem será carregada diretamente da URL

### ✅ Dicas para Melhores Resultados

1. **Qualidade da Foto**
   - Use fotos de boa qualidade
   - Fundo neutro ou desfocado
   - Boa iluminação
   - Foto recente do barbeiro

2. **Proporção**
   - Fotos quadradas funcionam melhor (1:1)
   - Evite fotos muito alongadas

3. **Tamanho do Arquivo**
   - Não precisa ser muito grande (recomendado: 200KB - 1MB)
   - Imagens muito grandes deixam o site mais lento

4. **Preview**
   - Sempre verifique o preview antes de salvar
   - Se não gostar, pode escolher outra foto

### 📁 Onde as Fotos Ficam Armazenadas?

As fotos enviadas ficam salvas em:
```
static/img/barbeiros/
```

O sistema nomeia automaticamente com timestamp para evitar conflitos:
- Exemplo: `barbeiro_20260118_143522.jpg`

### 🔄 Alterar Foto Existente

Para trocar a foto de um barbeiro:

1. Clique no ícone de editar do barbeiro
2. Selecione uma nova foto
3. Clique em "Salvar"
4. A foto antiga permanece no servidor (para não quebrar links antigos)
5. A nova foto substitui a antiga na exibição

### ⚠️ Importante

- **Backup**: As fotos ficam apenas no servidor. Faça backup regular da pasta `static/img/barbeiros/`
- **URLs Externas**: Se usar URL externa, certifique-se que o link é permanente
- **Privacidade**: Use apenas fotos com autorização do barbeiro

### 🎨 Exemplo de Fluxo Completo

```
1. Login no painel admin
   ↓
2. Barbeiros > Novo Barbeiro
   ↓
3. Nome: "João Silva"
   ↓
4. Clicar em "Selecionar Foto"
   ↓
5. Escolher arquivo: joao.jpg
   ↓
6. Ver preview redondo da foto
   ↓
7. Selecionar serviços (corte, barba, etc.)
   ↓
8. Salvar
   ↓
9. Foto aparece no card do barbeiro!
```

### 🐛 Problemas Comuns

**Erro: "Arquivo muito grande"**
- Solução: Reduza o tamanho da imagem usando um editor online (TinyPNG, Squoosh)

**Erro: "Formato não permitido"**
- Solução: Use JPG, PNG ou GIF. Converta se necessário.

**Foto não aparece**
- Verifique se o upload foi concluído
- Tente recarregar a página (F5)
- Verifique permissões da pasta `static/img/barbeiros/`

**Preview não funciona**
- Verifique se está usando um navegador moderno
- Limpe o cache do navegador

### 📞 Suporte

Se tiver problemas, verifique:
1. Logs do servidor no terminal
2. Console do navegador (F12)
3. Permissões de escrita na pasta `static/`
