"""
Script para testar a API de barbeiros em produção
"""
import requests
from datetime import datetime, timedelta

# URL do Render
BASE_URL = "https://agendador-barbearia.onrender.com"

def testar_barbeiros():
    """Testa o endpoint de barbeiros"""
    print("=" * 60)
    print("🧪 TESTANDO API DE BARBEIROS EM PRODUÇÃO")
    print("=" * 60)
    
    # Testar sem data (deve retornar todos)
    print("\n1️⃣ Testando sem data (todos os barbeiros)...")
    try:
        response = requests.get(f"{BASE_URL}/api/barbeiros", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Barbeiros encontrados: {len(data.get('barbeiros', []))}")
            for b in data.get('barbeiros', []):
                print(f"      - {b.get('nome')} (ID: {b.get('id')})")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    # Testar com data específica
    print("\n2️⃣ Testando com data 2026-01-22...")
    try:
        response = requests.get(f"{BASE_URL}/api/barbeiros?data=2026-01-22", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Barbeiros disponíveis: {len(data.get('barbeiros', []))}")
            for b in data.get('barbeiros', []):
                print(f"      - {b.get('nome')} (ID: {b.get('id')})")
            if len(data.get('barbeiros', [])) == 0:
                print("   ⚠️ NENHUM BARBEIRO DISPONÍVEL PARA ESTA DATA!")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    # Testar com data de amanhã
    amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"\n3️⃣ Testando com data de amanhã ({amanha})...")
    try:
        response = requests.get(f"{BASE_URL}/api/barbeiros?data={amanha}", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Barbeiros disponíveis: {len(data.get('barbeiros', []))}")
            for b in data.get('barbeiros', []):
                print(f"      - {b.get('nome')} (ID: {b.get('id')})")
            if len(data.get('barbeiros', [])) == 0:
                print("   ⚠️ NENHUM BARBEIRO DISPONÍVEL PARA ESTA DATA!")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")
    print("=" * 60)

if __name__ == '__main__':
    testar_barbeiros()
