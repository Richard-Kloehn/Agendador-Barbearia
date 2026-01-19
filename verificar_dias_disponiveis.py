"""Script para verificar dias disponíveis dos barbeiros"""
from app import app
from database import db
from models import HorarioBarbeiro, Barbeiro

def verificar_dias_disponiveis():
    with app.app_context():
        barbeiros = Barbeiro.query.filter_by(ativo=True).all()
        
        dias_semana = {
            0: 'Domingo',
            1: 'Segunda-feira',
            2: 'Terça-feira', 
            3: 'Quarta-feira',
            4: 'Quinta-feira',
            5: 'Sexta-feira',
            6: 'Sábado'
        }
        
        print("\n" + "="*60)
        print("DIAS DISPONÍVEIS POR BARBEIRO")
        print("="*60 + "\n")
        
        for barbeiro in barbeiros:
            print(f"🧔 {barbeiro.nome}")
            print("-" * 40)
            
            horarios = HorarioBarbeiro.query.filter_by(
                barbeiro_id=barbeiro.id,
                ativo=True
            ).order_by(HorarioBarbeiro.dia_semana).all()
            
            if not horarios:
                print("  ❌ Nenhum horário configurado")
            else:
                for horario in horarios:
                    dia = dias_semana.get(horario.dia_semana, 'Desconhecido')
                    almoco = ''
                    if horario.intervalo_almoco_inicio and horario.intervalo_almoco_fim:
                        almoco = f" (Almoço: {horario.intervalo_almoco_inicio}-{horario.intervalo_almoco_fim})"
                    print(f"  ✅ {dia}: {horario.horario_inicio} às {horario.horario_fim}{almoco}")
            
            print()
        
        print("="*60)
        print("📌 OBSERVAÇÃO:")
        print("  - Dia 0 = Domingo (FECHADO)")
        print("  - Dias 1-6 = Segunda a Sábado")
        print("="*60 + "\n")

if __name__ == '__main__':
    verificar_dias_disponiveis()
