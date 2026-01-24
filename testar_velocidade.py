import time
import requests
from datetime import datetime

def testar_velocidade_site():
    """Testa a velocidade de carregamento do site no Render"""
    
    # Substitua pela URL do seu site no Render
    URL = "https://seu-site.onrender.com"  # ← TROCAR AQUI
    
    print("🔍 TESTANDO VELOCIDADE DO SITE NO RENDER")
    print("=" * 60)
    print()
    
    # Teste 1: Primeira requisição (pode estar hibernando)
    print("📊 TESTE 1: Primeira requisição (cold start)")
    inicio = time.time()
    try:
        response = requests.get(URL, timeout=120)
        tempo_total = time.time() - inicio
        print(f"✅ Status: {response.status_code}")
        print(f"⏱️  Tempo: {tempo_total:.2f} segundos")
        
        if tempo_total > 30:
            print("⚠️  SERVIDOR ESTAVA HIBERNANDO!")
            print("   Solução: Plano pago do Render ($7/mês)")
        elif tempo_total > 5:
            print("⚠️  Um pouco lento, mas aceitável")
        else:
            print("✅ Velocidade excelente!")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    print("-" * 60)
    print()
    
    # Teste 2: Segunda requisição (servidor já ativo)
    print("📊 TESTE 2: Segunda requisição (servidor ativo)")
    time.sleep(2)
    inicio = time.time()
    try:
        response = requests.get(URL, timeout=30)
        tempo_total = time.time() - inicio
        print(f"✅ Status: {response.status_code}")
        print(f"⏱️  Tempo: {tempo_total:.2f} segundos")
        
        if tempo_total < 2:
            print("✅ Velocidade normal esperada!")
        else:
            print("⚠️  Ainda lento mesmo com servidor ativo")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    print("-" * 60)
    print()
    
    # Teste 3: Testar endpoint API
    print("📊 TESTE 3: Endpoint API de barbeiros")
    inicio = time.time()
    try:
        response = requests.get(f"{URL}/api/barbeiros", timeout=30)
        tempo_total = time.time() - inicio
        print(f"✅ Status: {response.status_code}")
        print(f"⏱️  Tempo: {tempo_total:.2f} segundos")
        
        if response.status_code == 200:
            dados = response.json()
            print(f"📦 Barbeiros retornados: {len(dados.get('barbeiros', []))}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    print("=" * 60)
    print("📝 DIAGNÓSTICO:")
    print()
    print("Se TESTE 1 > 30s: ⚠️  Servidor hibernando (plano grátis)")
    print("Se TESTE 2 < 2s:  ✅ Servidor funciona bem quando ativo")
    print("Se todos lentos: 🌍 Problema de latência ou conexão")

if __name__ == '__main__':
    testar_velocidade_site()
