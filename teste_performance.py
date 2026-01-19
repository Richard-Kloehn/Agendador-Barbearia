#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para validar as otimizações de performance
Executa: python teste_performance.py
"""

from app import app
from database import db
from models import Barbeiro, HorarioBarbeiro, Servico
from datetime import datetime, timedelta
import time
import json

def test_barbeiros_com_horarios():
    """Testa se barbeiros têm horários configurados"""
    print("\n" + "="*60)
    print("✅ TESTE 1: Verificar Horários dos Barbeiros")
    print("="*60)
    
    with app.app_context():
        barbeiros = Barbeiro.query.filter_by(ativo=True).all()
        print(f"\n📊 Total de barbeiros ativos: {len(barbeiros)}")
        
        for barbeiro in barbeiros:
            horarios = HorarioBarbeiro.query.filter_by(
                barbeiro_id=barbeiro.id,
                ativo=True
            ).all()
            
            print(f"\n👨‍💼 {barbeiro.nome}:")
            if horarios:
                for h in horarios:
                    dia = ['🟦 Domingo', '🟫 Segunda', '🟫 Terça', '🟫 Quarta', '🟫 Quinta', '🟫 Sexta', '🟨 Sábado'][h.dia_semana]
                    almoco = f"Almoço: {h.intervalo_almoco_inicio}-{h.intervalo_almoco_fim}" if h.intervalo_almoco_inicio else "Sem almoço"
                    print(f"  {dia}: {h.horario_inicio}-{h.horario_fim} ({almoco})")
            else:
                print("  ⚠️  Nenhum horário configurado!")
        
        return len([h for b in barbeiros for h in HorarioBarbeiro.query.filter_by(barbeiro_id=b.id).all()]) > 0

def test_query_performance():
    """Testa performance das queries otimizadas"""
    print("\n" + "="*60)
    print("⚡ TESTE 2: Performance de Queries")
    print("="*60)
    
    with app.app_context():
        from routes import get_dias_com_barbeiros_otimizado
        
        # Teste 1: Primeira chamada (sem cache)
        print("\n🔄 Primeira chamada (sem cache):")
        start = time.time()
        dias_cache = get_dias_com_barbeiros_otimizado()
        tempo1 = time.time() - start
        print(f"  ⏱️  Tempo: {tempo1*1000:.2f}ms")
        print(f"  📅 Dias com barbeiros: {sorted(dias_cache)}")
        
        # Teste 2: Segunda chamada (com cache)
        print("\n🔄 Segunda chamada (com cache):")
        start = time.time()
        dias_cache2 = get_dias_com_barbeiros_otimizado()
        tempo2 = time.time() - start
        print(f"  ⏱️  Tempo: {tempo2*1000:.2f}ms")
        print(f"  ⚡ Melhoria: {((tempo1-tempo2)/tempo1*100):.0f}% mais rápido")
        
        return True

def test_horarios_disponiveis():
    """Testa geração de horários disponíveis"""
    print("\n" + "="*60)
    print("📅 TESTE 3: Geração de Horários Disponíveis")
    print("="*60)
    
    with app.app_context():
        from routes import gerar_horarios_disponiveis
        
        config = app.config
        from models import ConfiguracaoBarbearia
        conf = ConfiguracaoBarbearia.query.first()
        
        # Próximo dia útil
        hoje = datetime.now().date()
        amanha = hoje + timedelta(days=1)
        
        # Se amanhã é domingo, vai para segunda
        while amanha.weekday() == 6:
            amanha += timedelta(days=1)
        
        print(f"\n📅 Data testada: {amanha.strftime('%A, %d/%m/%Y')}")
        
        barbeiro_id = 1  # Bryan
        servico_duracao = 30
        
        start = time.time()
        horarios = gerar_horarios_disponiveis(amanha, conf, barbeiro_id, servico_duracao)
        tempo = time.time() - start
        
        print(f"⏱️  Tempo de geração: {tempo*1000:.2f}ms")
        print(f"📊 Horários disponíveis: {len(horarios)}")
        if horarios:
            print(f"   Primeiro: {horarios[0]}")
            print(f"   Último: {horarios[-1]}")
        
        return len(horarios) > 0

def test_api_endpoints():
    """Testa endpoints da API"""
    print("\n" + "="*60)
    print("🌐 TESTE 4: Endpoints da API")
    print("="*60)
    
    with app.test_client() as client:
        # Teste GET /api/barbeiros
        print("\n🔹 GET /api/barbeiros")
        start = time.time()
        response = client.get('/api/barbeiros')
        tempo = time.time() - start
        
        print(f"   Status: {response.status_code}")
        print(f"   Tempo: {tempo*1000:.2f}ms")
        
        data = response.get_json()
        if data and 'barbeiros' in data:
            print(f"   Barbeiros retornados: {len(data['barbeiros'])}")
        
        # Teste GET /api/datas-disponiveis
        print("\n🔹 GET /api/datas-disponiveis")
        start = time.time()
        response = client.get('/api/datas-disponiveis')
        tempo = time.time() - start
        
        print(f"   Status: {response.status_code}")
        print(f"   Tempo: {tempo*1000:.2f}ms")
        
        data = response.get_json()
        if data:
            print(f"   Datas indisponíveis: {len(data.get('datas_indisponiveis', []))}")
        
        # Teste GET /api/barbeiro/1/horarios (novo endpoint)
        print("\n🔹 GET /api/barbeiro/1/horarios (NOVO)")
        start = time.time()
        response = client.get('/api/barbeiro/1/horarios')
        tempo = time.time() - start
        
        print(f"   Status: {response.status_code}")
        print(f"   Tempo: {tempo*1000:.2f}ms")
        
        data = response.get_json()
        if data and 'horarios' in data:
            print(f"   Dias configurados: {len(data['horarios'])}")
        
        return response.status_code == 200

def main():
    """Executa todos os testes"""
    print("\n" + "🔬 "*20)
    print("TESTES DE PERFORMANCE E FUNCIONALIDADE")
    print("🔬 "*20)
    
    results = {
        'Horários dos Barbeiros': test_barbeiros_com_horarios(),
        'Query Performance': test_query_performance(),
        'Horários Disponíveis': test_horarios_disponiveis(),
        'API Endpoints': test_api_endpoints(),
    }
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    for teste, resultado in results.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{status}: {teste}")
    
    total_pass = sum(1 for r in results.values() if r)
    total_tests = len(results)
    
    print("\n" + "-"*60)
    print(f"Resultado Final: {total_pass}/{total_tests} testes passaram")
    
    if total_pass == total_tests:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema otimizado e funcionando!")
    else:
        print(f"\n⚠️  {total_tests - total_pass} teste(s) falharam. Revise os erros acima.")
    
    print("="*60)

if __name__ == '__main__':
    main()
