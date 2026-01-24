"""
🚀 SCRIPT DE INICIALIZAÇÃO DO RAILWAY
Cria todas as tabelas e popula com dados iniciais
"""

import os
import sys

# Pedir a DATABASE_URL do Railway
print("=" * 70)
print("🚀 INICIALIZAÇÃO DO BANCO DE DADOS NO RAILWAY")
print("=" * 70)
print()
print("1. No Railway, vá em: web → Variables")
print("2. Copie o valor de DATABASE_URL")
print("3. Cole aqui abaixo:")
print()

database_url = input("DATABASE_URL do Railway: ").strip()

if not database_url or 'postgresql://' not in database_url:
    print("❌ URL inválida! Deve começar com postgresql://")
    sys.exit(1)

# Configurar a URL
os.environ['DATABASE_URL'] = database_url

print()
print("=" * 70)
print("📦 CRIANDO TABELAS...")
print("=" * 70)
print()

# Importar app e criar tabelas
from app import app, db
from models import Barbeiro, Servico, HorarioBarbeiro

with app.app_context():
    # Criar todas as tabelas
    db.create_all()
    print("✅ Tabelas criadas com sucesso!")
    print()
    
    # Verificar se já tem barbeiros
    if Barbeiro.query.first():
        print("⚠️  Banco já tem dados! Pulando inicialização...")
    else:
        print("=" * 70)
        print("👨‍💼 CRIANDO BARBEIROS...")
        print("=" * 70)
        print()
        
        # Criar barbeiros
        barbeiros_data = [
            {"nome": "João Silva", "foto_url": "/static/img/barbeiro1.jpg", "ordem": 1},
            {"nome": "Pedro Santos", "foto_url": "/static/img/barbeiro2.jpg", "ordem": 2},
            {"nome": "Carlos Oliveira", "foto_url": "/static/img/barbeiro3.jpg", "ordem": 3}
        ]
        
        barbeiros_criados = []
        for data in barbeiros_data:
            barbeiro = Barbeiro(
                nome=data['nome'],
                foto_url=data['foto_url'],
                ativo=True,
                ordem=data['ordem']
            )
            db.session.add(barbeiro)
            barbeiros_criados.append(barbeiro)
            print(f"✅ Barbeiro criado: {data['nome']}")
        
        db.session.commit()
        print()
        
        print("=" * 70)
        print("✂️  CRIANDO SERVIÇOS...")
        print("=" * 70)
        print()
        
        # Criar serviços
        servicos_data = [
            {"nome": "Corte Simples", "descricao": "Corte de cabelo tradicional", "preco": 30.00, "duracao": 30},
            {"nome": "Corte + Barba", "descricao": "Corte de cabelo + barba completa", "preco": 50.00, "duracao": 45},
            {"nome": "Barba", "descricao": "Apenas barba", "preco": 25.00, "duracao": 20},
            {"nome": "Corte Degradê", "descricao": "Corte degradê moderno", "preco": 40.00, "duracao": 40}
        ]
        
        for data in servicos_data:
            servico = Servico(
                nome=data['nome'],
                descricao=data['descricao'],
                preco=data['preco'],
                duracao=data['duracao'],
                ativo=True
            )
            db.session.add(servico)
            
            # Associar todos os barbeiros a todos os serviços
            servico.barbeiros = barbeiros_criados
            print(f"✅ Serviço criado: {data['nome']} - R$ {data['preco']:.2f}")
        
        db.session.commit()
        print()
        
        print("=" * 70)
        print("⏰ CRIANDO HORÁRIOS DOS BARBEIROS...")
        print("=" * 70)
        print()
        
        # Criar horários para cada barbeiro
        for barbeiro in barbeiros_criados:
            # Segunda a Sexta (dias 2-6)
            for dia in range(2, 7):
                horario = HorarioBarbeiro(
                    barbeiro_id=barbeiro.id,
                    dia_semana=dia,
                    horario_inicio="09:00",
                    horario_fim="18:00",
                    intervalo_almoco_inicio="12:00",
                    intervalo_almoco_fim="13:00",
                    ativo=True
                )
                db.session.add(horario)
            
            # Sábado (dia 7)
            horario_sabado = HorarioBarbeiro(
                barbeiro_id=barbeiro.id,
                dia_semana=7,
                horario_inicio="09:00",
                horario_fim="14:00",
                intervalo_almoco_inicio=None,
                intervalo_almoco_fim=None,
                ativo=True
            )
            db.session.add(horario_sabado)
            
            print(f"✅ Horários criados para: {barbeiro.nome}")
        
        db.session.commit()
        print()
        
        print("=" * 70)
        print("🎉 INICIALIZAÇÃO COMPLETA!")
        print("=" * 70)
        print()
        print(f"✅ {len(barbeiros_criados)} barbeiros criados")
        print(f"✅ {len(servicos_data)} serviços criados")
        print(f"✅ Horários configurados (Seg-Sex: 9h-18h, Sáb: 9h-14h)")
        print()
        print("🌐 Seu site está pronto para uso!")
        print()

print("=" * 70)
print("✅ PROCESSO FINALIZADO!")
print("=" * 70)
