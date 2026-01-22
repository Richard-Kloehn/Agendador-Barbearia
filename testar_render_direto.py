"""
Teste direto da API no Render com headers de navegador
"""
import requests
import json

URL = "https://agendador-barbearia.onrender.com/api/barbeiros?data=2026-01-22"

print("=" * 60)
print("🧪 TESTE DIRETO DA API NO RENDER")
print("=" * 60)
print(f"\n📍 URL: {URL}")

# Headers simulando navegador
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
}

try:
    print("\n🔄 Fazendo requisição...")
    response = requests.get(URL, headers=headers, timeout=15)
    
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📊 Headers: {dict(response.headers)}")
    
    print(f"\n📄 Resposta:")
    print(response.text)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Barbeiros retornados: {len(data.get('barbeiros', []))}")
        for b in data.get('barbeiros', []):
            print(f"   - {b.get('nome')} (ID: {b.get('id')})")
    else:
        print(f"\n❌ ERRO {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Exceção: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
