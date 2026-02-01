"""
Script para atualizar o banco PostgreSQL do Railway diretamente
Execute com: python atualizar_banco_railway.py
"""
import os
from app import app
from database import db
from models import Barbeiro, HorarioBarbeiro, ConfiguracaoBarbearia

# Forçar uso do DATABASE_URL (PostgreSQL do Railway)
with app.app_context():
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    
    print("="*70)
    print("🔧 ATUALIZANDO BANCO DE DADOS DO RAILWAY")
    print("="*70)
    print(f"Banco: {'PostgreSQL (Railway)' if 'postgresql' in db_url else 'SQLite (Local)'}")
    
    if 'postgresql' not in db_url:
        print("\n❌ ERRO: Não está conectado ao PostgreSQL!")
        print("Configure DATABASE_URL do Railway nas variáveis de ambiente")
        exit(1)
    
    print("✅ Conectado ao PostgreSQL do Railway\n")
    
    # 1. Atualizar configuração
    print("="*70)
    print("1️⃣ CONFIGURAÇÃO")
    print("="*70)
    
    config = ConfiguracaoBarbearia.query.first()
    if config:
        print(f"Dias atuais: {config.dias_funcionamento}")
        config.dias_funcionamento = "0,1,2,3,4,5"  # Segunda a Sábado
        db.session.commit()
        print(f"✅ Atualizado para: {config.dias_funcionamento}\n")
    else:
        print("⚠️ Criando configuração...")
        config = ConfiguracaoBarbearia(
            nome_barbearia="Navalha's Barber Club",
            horario_abertura="09:00",
            horario_fechamento="19:00",
            duracao_atendimento=30,
            intervalo_almoco_inicio="12:00",
            intervalo_almoco_fim="13:00",
            dias_funcionamento="0,1,2,3,4,5"
        )
        db.session.add(config)
        db.session.commit()
        print("✅ Configuração criada!\n")
    
    # 2. Recriar horários
    print("="*70)
    print("2️⃣ HORÁRIOS DOS BARBEIROS")
    print("="*70)
    
    barbeiros = Barbeiro.query.all()
    print(f"Barbeiros: {len(barbeiros)}\n")
    
    # Horários padrão (0=segunda, 1=terça, ..., 5=sábado)
    horarios_padrao = [
        {'dia_semana': 0, 'horario_inicio': '09:00', 'horario_fim': '18:00', 
         'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
        {'dia_semana': 1, 'horario_inicio': '09:00', 'horario_fim': '18:00',
         'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
        {'dia_semana': 2, 'horario_inicio': '09:00', 'horario_fim': '18:00',
         'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
        {'dia_semana': 3, 'horario_inicio': '09:00', 'horario_fim': '18:00',
         'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
        {'dia_semana': 4, 'horario_inicio': '09:00', 'horario_fim': '18:00',
         'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
        {'dia_semana': 5, 'horario_inicio': '09:00', 'horario_fim': '17:00',
         'intervalo_almoco_inicio': None, 'intervalo_almoco_fim': None}
    ]
    
    dias_nomes = {0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex', 5: 'Sáb'}
    total_criados = 0
    
    for barbeiro in barbeiros:
        print(f"🔧 {barbeiro.nome}:")
        
        # Deletar horários antigos
        qtd = HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro.id).delete()
        print(f"   Removidos: {qtd} horários antigos")
        
        # Criar novos
        for h in horarios_padrao:
            horario = HorarioBarbeiro(
                barbeiro_id=barbeiro.id,
                dia_semana=h['dia_semana'],
                horario_inicio=h['horario_inicio'],
                horario_fim=h['horario_fim'],
                intervalo_almoco_inicio=h['intervalo_almoco_inicio'],
                intervalo_almoco_fim=h['intervalo_almoco_fim'],
                ativo=True
            )
            db.session.add(horario)
            total_criados += 1
        
        print(f"   Criados: {len(horarios_padrao)} horários novos\n")
    
    db.session.commit()
    
    # 3. Verificação
    print("="*70)
    print("3️⃣ VERIFICAÇÃO")
    print("="*70)
    
    for barbeiro in barbeiros:
        horarios = HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro.id).order_by(HorarioBarbeiro.dia_semana).all()
        print(f"\n{barbeiro.nome}: {len(horarios)} horários")
        for h in horarios:
            print(f"  ✅ Dia {h.dia_semana} ({dias_nomes[h.dia_semana]}): {h.horario_inicio}-{h.horario_fim}")
    
    print("\n" + "="*70)
    print(f"🎉 SUCESSO! {total_criados} horários criados no PostgreSQL do Railway")
    print("="*70)
