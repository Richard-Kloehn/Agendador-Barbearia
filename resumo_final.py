import requests

WHAPI_TOKEN = "OxR8uL8Hjf5Usq7KzCdbE84xgEuT2Ibr"
WHAPI_URL = "https://gate.whapi.cloud"

headers = {
    "Authorization": f"Bearer {WHAPI_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("TESTE COM NÚMERO REAL DA BARBEARIA")
print("=" * 70)
print("\nSe você puder fornecer um número de WhatsApp REAL e ATIVO,")
print("posso testar o envio corretamente.")
print("\nBaseado nas regras do WHAPI:")
print("  • DDD 47 (Santa Catarina) NÃO está na lista (11-19, 21, 22, 24, 27, 28)")
print("  • Portanto, o formato correto é 55 + DDD + 9 + 8 dígitos")
print("  • Exemplo: (47) 99155-7386 → 5547991557386")

print("\n" + "=" * 70)
print("VERIFICANDO CONFIGURAÇÃO ATUAL DO WHAPI")
print("=" * 70)

# Obter informações da conta
response = requests.get(f"{WHAPI_URL}/settings", headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ Conta WHAPI conectada:")
    print(f"   Número: {data.get('wid', 'N/A')}")
    print(f"   Nome: {data.get('pushname', 'N/A')}")
    print(f"   Status: {data.get('status', 'N/A')}")
    print(f"   Conectado: {data.get('connected', False)}")
else:
    print(f"❌ Erro ao obter configurações: {response.text}")

print("\n" + "=" * 70)
print("RESUMO DOS TESTES")
print("=" * 70)

print("\n✅ Formato correto identificado: 5547991557386 (13 dígitos)")
print("✅ API aceita o envio (retorna 200 OK)")
print("✅ Status da mensagem: 'sent' ou 'pending'")
print("❌ Problema: Números de teste não têm WhatsApp ativo")
print("❌ Resultado: Mensagens ficam em 1 tick (não entregues)")

print("\n💡 SOLUÇÃO:")
print("   1. Use um número de WhatsApp REAL e ATIVO para teste")
print("   2. O formato está correto: 55 + DDD + número com 9")
print("   3. Para DDD 47: 5547 + 9 dígitos (ex: 5547991557386)")
print("   4. A função formatar_numero() já foi atualizada com as regras")

print("\n📊 Limites atuais da trial:")
print("   • 136/150 mensagens restantes")
print("   • 5/5 chats usados (limite atingido)")
print("   • Expira em: 27/01/2026")
print("   • Para testar com novos números, considere o upgrade")

print("\n" + "=" * 70)
