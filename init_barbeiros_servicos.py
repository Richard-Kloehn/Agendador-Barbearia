"""Script para adicionar barbeiros e serviços ao banco de dados"""
from app import app
from database import db
from models import Barbeiro, Servico

def inicializar_barbeiros_servicos():
    with app.app_context():
        print("🚀 Iniciando cadastro de barbeiros e serviços...")
        
        # Verificar se já existem dados
        if Barbeiro.query.count() > 0:
            print("⚠️  Barbeiros já cadastrados. Pulando...")
        else:
            # Criar barbeiros
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
            
            print("✅ Serviços cadastrados com sucesso!")
        
        # Commit das alterações
        db.session.commit()
        
        # Associar todos os serviços a todos os barbeiros
        barbeiros = Barbeiro.query.all()
        servicos = Servico.query.all()
        
        for barbeiro in barbeiros:
            if not barbeiro.servicos:
                barbeiro.servicos = servicos
        
        db.session.commit()
        
        print(f"✅ {len(barbeiros)} barbeiros e {len(servicos)} serviços associados!")
        print("\n📊 Resumo:")
        print(f"   Barbeiros: {Barbeiro.query.count()}")
        print(f"   Serviços: {Servico.query.count()}")
        print("\n✨ Banco de dados atualizado com sucesso!")

if __name__ == '__main__':
    inicializar_barbeiros_servicos()
