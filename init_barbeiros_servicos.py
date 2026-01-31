"""Script para adicionar barbeiros e serviços ao banco de dados"""
from app import app
from database import db
from models import Barbeiro, Servico, HorarioBarbeiro

def inicializar_barbeiros_servicos():
    with app.app_context():
        print("🚀 Iniciando cadastro de barbeiros, serviços e horários...")
        
        # Verificar se já existem dados
        if Barbeiro.query.count() > 0:
            print("⚠️  Barbeiros já cadastrados. Pulando...")
        else:
            # Criar barbeiros
            barbeiros = [
                Barbeiro(
                    nome="Bryan Victor Felippi",
                    foto_url="/static/img/barbeiro1.jpg",
                    ativo=True,
                    ordem=1
                ),
                Barbeiro(
                    nome="Fabricio",
                    foto_url="/static/img/barbeiro2.jpg",
                    ativo=True,
                    ordem=2
                ),
                Barbeiro(
                    nome="Felipe Soares Santana",
                    foto_url="/static/img/barbeiro3.jpg",
                    ativo=True,
                    ordem=3
                )
            ]
            
            for barbeiro in barbeiros:
                db.session.add(barbeiro)
            
            db.session.commit()
            print("✅ Barbeiros cadastrados com sucesso!")
        
        if Servico.query.count() > 0:
            print("⚠️  Serviços já cadastrados. Pulando...")
        else:
            # Criar serviços
            servicos = [
                Servico(
                    nome="Corte de Cabelo",
                    descricao="Corte masculino profissional",
                    duracao=30,
                    preco=45.00,
                    ativo=True,
                    ordem=1
                ),
                Servico(
                    nome="Barba",
                    descricao="Aparar e modelar barba",
                    duracao=20,
                    preco=30.00,
                    ativo=True,
                    ordem=2
                ),
                Servico(
                    nome="Corte + Barba",
                    descricao="Corte de cabelo e barba",
                    duracao=45,
                    preco=70.00,
                    ativo=True,
                    ordem=3
                ),
                Servico(
                    nome="Pezinho",
                    descricao="Aparar pézinho e nuca",
                    duracao=15,
                    preco=20.00,
                    ativo=True,
                    ordem=4
                )
            ]
            
            for servico in servicos:
                db.session.add(servico)
            
            db.session.commit()
            print("✅ Serviços cadastrados com sucesso!")
        
        # Associar todos os serviços a todos os barbeiros
        barbeiros = Barbeiro.query.all()
        servicos = Servico.query.all()
        
        for barbeiro in barbeiros:
            if not barbeiro.servicos:
                barbeiro.servicos = servicos
        
        db.session.commit()
        print("✅ Serviços associados aos barbeiros!")
        
        # Criar horários dos barbeiros
        total_horarios = HorarioBarbeiro.query.count()
        print(f"\n📊 Horários existentes: {total_horarios}")
        
        if total_horarios == 0:
            print("\n⏰ Criando horários dos barbeiros...")
            
            # Horários padrão (1=Segunda, 2=Terça, ..., 6=Sábado)
            horarios_padrao = [
                {'dia_semana': 1, 'horario_inicio': '09:00', 'horario_fim': '18:00', 
                 'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
                {'dia_semana': 2, 'horario_inicio': '09:00', 'horario_fim': '18:00',
                 'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
                {'dia_semana': 3, 'horario_inicio': '09:00', 'horario_fim': '18:00',
                 'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
                {'dia_semana': 4, 'horario_inicio': '09:00', 'horario_fim': '18:00',
                 'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
                {'dia_semana': 5, 'horario_inicio': '09:00', 'horario_fim': '18:00',
                 'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
                {'dia_semana': 6, 'horario_inicio': '09:00', 'horario_fim': '17:00',
                 'intervalo_almoco_inicio': None, 'intervalo_almoco_fim': None}
            ]
            
            total_criados = 0
            for barbeiro in barbeiros:
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
                    total_criados += 1
            
            db.session.commit()
            print(f"✅ {total_criados} horários criados!")
        else:
            print("✅ Horários já cadastrados!")
        
        print("\n" + "="*60)
        print("✅ Inicialização completa!")
        print("="*60)
        print(f"📊 Barbeiros: {Barbeiro.query.count()}")
        print(f"✂️ Serviços: {Servico.query.count()}")
        print(f"⏰ Horários: {HorarioBarbeiro.query.count()}")
        print("="*60)

if __name__ == '__main__':
    inicializar_barbeiros_servicos()
