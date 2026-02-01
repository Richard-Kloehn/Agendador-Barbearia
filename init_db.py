"""
Script de inicialização do banco de dados
Execute este script para criar o banco e dados iniciais
"""

from app import app
from database import db
from models import ConfiguracaoBarbearia, Agendamento, Cliente, Barbeiro, Servico, HorarioBarbeiro
from datetime import datetime, timedelta

def inicializar_banco():
    """Cria as tabelas e dados iniciais"""
    
    with app.app_context():
        print("🔧 Criando tabelas do banco de dados...")
        db.create_all()
        print("✅ Tabelas criadas!")
        
        # Verificar se já existe configuração
        config_existente = ConfiguracaoBarbearia.query.first()
        
        if not config_existente:
            print("\n📝 Criando configuração padrão...")
            
            config_padrao = ConfiguracaoBarbearia(
                nome_barbearia="Navalha's Barber Club",
                horario_abertura="09:00",
                horario_fechamento="19:00",
                duracao_atendimento=30,  # 30 minutos por atendimento
                intervalo_almoco_inicio="12:00",
                intervalo_almoco_fim="13:00",
                dias_funcionamento="0,1,2,3,4,5"  # Segunda a Sábado
            )
            
            db.session.add(config_padrao)
            db.session.commit()
            
            print("✅ Configuração criada com sucesso!")
            print("\n📋 Configurações:")
            print(f"   Nome: {config_padrao.nome_barbearia}")
            print(f"   Horário: {config_padrao.horario_abertura} - {config_padrao.horario_fechamento}")
            print(f"   Duração por atendimento: {config_padrao.duracao_atendimento} minutos")
            print(f"   Almoço: {config_padrao.intervalo_almoco_inicio} - {config_padrao.intervalo_almoco_fim}")
        else:
            print("\n✅ Configuração já existe!")
            print(f"   Nome: {config_existente.nome_barbearia}")
        
        
        # Inicializar barbeiros e serviços
        print("\n👨‍💼 Criando barbeiros e serviços...")
        
        # Criar barbeiros
        if Barbeiro.query.count() == 0:
            barbeiros = [
                Barbeiro(
                    nome="Bryan Victor Felippi",
                    foto_url="https://via.placeholder.com/150?text=Bryan",
                    ativo=True,
                    ordem=1
                ),
                Barbeiro(
                    nome="Fabricio",
                    foto_url="https://via.placeholder.com/150?text=Fabricio",
                    ativo=True,
                    ordem=2
                ),
                Barbeiro(
                    nome="Felipe Soares Santana",
                    foto_url="https://via.placeholder.com/150?text=Felipe",
                    ativo=True,
                    ordem=3
                )
            ]
            
            for barbeiro in barbeiros:
                db.session.add(barbeiro)
            
            print(f"✅ {len(barbeiros)} barbeiros criados!")
        else:
            barbeiros = Barbeiro.query.all()
            print(f"✅ {len(barbeiros)} barbeiros já existem!")
        
        # Criar serviços
        if Servico.query.count() == 0:
            servicos = [
                Servico(
                    nome="Corte de Cabelo",
                    descricao="Corte masculino profissional",
                    duracao=30,
                    preco=45.00,
                    ativo=True
                ),
                Servico(
                    nome="Barba",
                    descricao="Aparar e modelar barba",
                    duracao=30,
                    preco=45.00,
                    ativo=True
                ),
                Servico(
                    nome="Combo (Cabelo + Barba)",
                    descricao="Corte de cabelo e barba",
                    duracao=45,
                    preco=95.00,
                    ativo=True
                ),
                Servico(
                    nome="Sobrancelha",
                    descricao="Design de sobrancelha",
                    duracao=15,
                    preco=25.00,
                    ativo=True
                ),
                Servico(
                    nome="Pézinho",
                    descricao="Aparar pézinho e nuca",
                    duracao=15,
                    preco=20.00,
                    ativo=True
                )
            ]
            
            for servico in servicos:
                db.session.add(servico)
            
            db.session.commit()
            print(f"✅ {len(servicos)} serviços criados!")
        else:
            servicos = Servico.query.all()
            print(f"✅ {len(servicos)} serviços já existem!")
        
        # Associar todos os serviços a todos os barbeiros
        barbeiros = Barbeiro.query.all()
        servicos = Servico.query.all()
        
        for barbeiro in barbeiros:
            if not barbeiro.servicos:
                barbeiro.servicos = servicos
        
        db.session.commit()
        print(f"✅ Serviços associados aos barbeiros!")
        
        # Criar horários para os barbeiros (Segunda a Sábado)
        print("\n⏰ Criando horários dos barbeiros...")
        horarios_criados = 0
        
        for barbeiro in barbeiros:
            # Verificar se barbeiro já tem horários configurados
            if HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro.id).count() == 0:
                # Criar horários padrão para Segunda (1) a Sábado (6)
                # Segunda a Sexta: 09:00-19:00 com almoço 12:00-13:00
                # Sábado: 08:00-14:00 sem almoço
                
                horarios_semana = [
                    # Segunda a Sexta
                    HorarioBarbeiro(
                        barbeiro_id=barbeiro.id,
                        dia_semana=1,  # Segunda
                        horario_inicio="09:00",
                        horario_fim="19:00",
                        intervalo_almoco_inicio="12:00",
                        intervalo_almoco_fim="13:00",
                        ativo=True
                    ),
                    HorarioBarbeiro(
                        barbeiro_id=barbeiro.id,
                        dia_semana=2,  # Terça
                        horario_inicio="09:00",
                        horario_fim="19:00",
                        intervalo_almoco_inicio="12:00",
                        intervalo_almoco_fim="13:00",
                        ativo=True
                    ),
                    HorarioBarbeiro(
                        barbeiro_id=barbeiro.id,
                        dia_semana=3,  # Quarta
                        horario_inicio="09:00",
                        horario_fim="19:00",
                        intervalo_almoco_inicio="12:00",
                        intervalo_almoco_fim="13:00",
                        ativo=True
                    ),
                    HorarioBarbeiro(
                        barbeiro_id=barbeiro.id,
                        dia_semana=4,  # Quinta
                        horario_inicio="09:00",
                        horario_fim="19:00",
                        intervalo_almoco_inicio="12:00",
                        intervalo_almoco_fim="13:00",
                        ativo=True
                    ),
                    HorarioBarbeiro(
                        barbeiro_id=barbeiro.id,
                        dia_semana=5,  # Sexta
                        horario_inicio="09:00",
                        horario_fim="19:00",
                        intervalo_almoco_inicio="12:00",
                        intervalo_almoco_fim="13:00",
                        ativo=True
                    ),
                    # Sábado
                    HorarioBarbeiro(
                        barbeiro_id=barbeiro.id,
                        dia_semana=6,  # Sábado
                        horario_inicio="08:00",
                        horario_fim="14:00",
                        intervalo_almoco_inicio=None,
                        intervalo_almoco_fim=None,
                        ativo=True
                    ),
                ]
                
                for horario in horarios_semana:
                    db.session.add(horario)
                    horarios_criados += 1
        
        db.session.commit()
        print(f"✅ {horarios_criados} horários criados para os barbeiros!")
        
        # Criar alguns agendamentos de exemplo (opcional)
        criar_agendamentos_exemplo = input("\n❓ Deseja criar agendamentos de exemplo? (s/n): ").lower()
        
        if criar_agendamentos_exemplo == 's' and len(barbeiros) > 0 and len(servicos) > 0:
            print("\n📅 Criando agendamentos de exemplo...")
            
            hoje = datetime.now()
            amanha = hoje + timedelta(days=1)
            
            exemplos = [
                {
                    "nome_cliente": "João Silva",
                    "telefone": "11999998888",
                    "data_hora": amanha.replace(hour=10, minute=0, second=0, microsecond=0),
                    "barbeiro_id": barbeiros[0].id,
                    "servico_id": servicos[0].id,
                    "status": "confirmado",
                    "observacoes": "Cliente regular"
                },
                {
                    "nome_cliente": "Pedro Santos",
                    "telefone": "11988887777",
                    "data_hora": amanha.replace(hour=11, minute=0, second=0, microsecond=0),
                    "barbeiro_id": barbeiros[1].id,
                    "servico_id": servicos[1].id,
                    "status": "pendente",
                    "observacoes": "Primeiro agendamento"
                },
                {
                    "nome_cliente": "Carlos Oliveira",
                    "telefone": "11977776666",
                    "data_hora": amanha.replace(hour=14, minute=0, second=0, microsecond=0),
                    "barbeiro_id": barbeiros[2].id,
                    "servico_id": servicos[2].id,
                    "status": "confirmado",
                    "observacoes": ""
                }
            ]
            
            for exemplo in exemplos:
                agendamento = Agendamento(**exemplo)
                db.session.add(agendamento)
            
            db.session.commit()
            print(f"✅ {len(exemplos)} agendamentos de exemplo criados!")
        
        print("\n" + "="*50)
        print("🎉 Banco de dados inicializado com sucesso!")
        print("="*50)
        print("\n🚀 Próximos passos:")
        print("1. Execute: python app.py")
        print("2. Acesse: http://localhost:5000")
        print("3. Painel Admin: http://localhost:5000/admin-dashboard")
        print("\n💡 Dica: Configure o WhatsApp no arquivo .env para enviar lembretes")

if __name__ == "__main__":
    print("="*50)
    print("🏪 INICIALIZAÇÃO DO SISTEMA DE BARBEARIA")
    print("="*50)
    inicializar_banco()
