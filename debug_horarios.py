"""Script rápido para debug de horários"""
from app import app
from database import db
from models import Barbeiro, HorarioBarbeiro
from datetime import datetime

with app.app_context():
    print("="*60)
    print("DEBUG: HORÁRIOS DOS BARBEIROS")
    print("="*60)
    
    # Verificar banco
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"\n📊 Banco: {'PostgreSQL (Produção)' if 'postgresql' in db_url else 'SQLite (Local)'}")
    
    # Listar barbeiros
    barbeiros = Barbeiro.query.all()
    print(f"\n👥 Total de barbeiros: {len(barbeiros)}")
    
    # Listar horários
    dias_nomes = {0: 'Dom', 1: 'Seg', 2: 'Ter', 3: 'Qua', 4: 'Qui', 5: 'Sex', 6: 'Sáb'}
    
    for barbeiro in barbeiros:
        print(f"\n{'='*60}")
        print(f"Barbeiro: {barbeiro.nome} (ID: {barbeiro.id})")
        print(f"Ativo: {'✅' if barbeiro.ativo else '❌'}")
        
        horarios = HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro.id).order_by(HorarioBarbeiro.dia_semana).all()
        
        if not horarios:
            print("❌ SEM HORÁRIOS!")
        else:
            print(f"Horários cadastrados: {len(horarios)}")
            for h in horarios:
                status = "✅" if h.ativo else "❌"
                print(f"  {status} Dia {h.dia_semana} ({dias_nomes[h.dia_semana]}): {h.horario_inicio}-{h.horario_fim}")
    
    # Testar conversão para hoje
    print(f"\n{'='*60}")
    print("TESTE DE CONVERSÃO")
    print("="*60)
    
    hoje = datetime.now().date()
    python_weekday = hoje.weekday()
    dia_sistema = python_weekday + 1
    if dia_sistema == 7:
        dia_sistema = 0
    
    print(f"Data: {hoje.strftime('%d/%m/%Y - %A')}")
    print(f"Python weekday(): {python_weekday} (0=seg, 6=dom)")
    print(f"Dia no sistema: {dia_sistema} (1=seg, 6=sáb, 0=dom)")
    
    horarios_hoje = HorarioBarbeiro.query.filter_by(dia_semana=dia_sistema, ativo=True).all()
    print(f"\n🔍 Horários encontrados para dia {dia_sistema}: {len(horarios_hoje)}")
    for h in horarios_hoje:
        b = Barbeiro.query.get(h.barbeiro_id)
        print(f"  - {b.nome if b else 'N/A'} ({h.horario_inicio}-{h.horario_fim})")
