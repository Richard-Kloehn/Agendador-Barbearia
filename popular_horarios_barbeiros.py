"""
Script para popular horários dos barbeiros no banco de dados
==============================================================
Cria horários padrão para todos os barbeiros cadastrados
"""

from app import app, db
from models import Barbeiro, HorarioBarbeiro

def popular_horarios_barbeiros():
    """Cria horários padrão para todos os barbeiros"""
    
    with app.app_context():
        # Buscar todos os barbeiros
        barbeiros = Barbeiro.query.all()
        
        if not barbeiros:
            print("❌ Nenhum barbeiro encontrado no banco de dados!")
            print("   Execute primeiro: python init_barbeiros_servicos.py")
            return
        
        print(f"📋 Encontrados {len(barbeiros)} barbeiro(s)")
        
        for barbeiro in barbeiros:
            print(f"\n👤 Configurando horários para: {barbeiro.nome}")
            
            # Verificar se já tem horários
            horarios_existentes = HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro.id).count()
            if horarios_existentes > 0:
                print(f"   ⚠️ Já possui {horarios_existentes} horário(s) cadastrado(s). Pulando...")
                continue
            
            # Definir horários padrão
            # Segunda a Sexta: 09:00 às 18:00 (com almoço 12:00-13:00)
            # Sábado: 09:00 às 17:00 (sem almoço)
            # Domingo: Fechado
            
            horarios_padrao = [
                # Domingo (0) - Fechado (não cria registro)
                
                # Segunda (1)
                {
                    'dia_semana': 1,
                    'horario_inicio': '09:00',
                    'horario_fim': '18:00',
                    'intervalo_almoco_inicio': '12:00',
                    'intervalo_almoco_fim': '13:00'
                },
                # Terça (2)
                {
                    'dia_semana': 2,
                    'horario_inicio': '09:00',
                    'horario_fim': '18:00',
                    'intervalo_almoco_inicio': '12:00',
                    'intervalo_almoco_fim': '13:00'
                },
                # Quarta (3)
                {
                    'dia_semana': 3,
                    'horario_inicio': '09:00',
                    'horario_fim': '18:00',
                    'intervalo_almoco_inicio': '12:00',
                    'intervalo_almoco_fim': '13:00'
                },
                # Quinta (4)
                {
                    'dia_semana': 4,
                    'horario_inicio': '09:00',
                    'horario_fim': '18:00',
                    'intervalo_almoco_inicio': '12:00',
                    'intervalo_almoco_fim': '13:00'
                },
                # Sexta (5)
                {
                    'dia_semana': 5,
                    'horario_inicio': '09:00',
                    'horario_fim': '18:00',
                    'intervalo_almoco_inicio': '12:00',
                    'intervalo_almoco_fim': '13:00'
                },
                # Sábado (6)
                {
                    'dia_semana': 6,
                    'horario_inicio': '09:00',
                    'horario_fim': '17:00',
                    'intervalo_almoco_inicio': None,
                    'intervalo_almoco_fim': None
                }
            ]
            
            # Criar horários
            for horario_data in horarios_padrao:
                horario = HorarioBarbeiro(
                    barbeiro_id=barbeiro.id,
                    dia_semana=horario_data['dia_semana'],
                    horario_inicio=horario_data['horario_inicio'],
                    horario_fim=horario_data['horario_fim'],
                    intervalo_almoco_inicio=horario_data['intervalo_almoco_inicio'],
                    intervalo_almoco_fim=horario_data['intervalo_almoco_fim'],
                    ativo=True
                )
                db.session.add(horario)
            
            db.session.commit()
            print(f"   ✅ {len(horarios_padrao)} horários criados com sucesso!")
        
        print("\n" + "="*60)
        print("✅ CONCLUÍDO! Horários dos barbeiros configurados.")
        print("="*60)

if __name__ == '__main__':
    popular_horarios_barbeiros()
