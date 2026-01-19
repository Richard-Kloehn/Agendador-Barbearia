# 🗄️ EXEMPLO DE CONFIGURAÇÃO DO BANCO PARA SEU APP

# Este é um exemplo de como conectar seu app ao Supabase
# Copie e adapte para seu código existente

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

class DatabaseConnection:
    """Classe para gerenciar conexão com Supabase PostgreSQL"""
    
    @staticmethod
    def get_connection():
        """Retorna uma conexão com o banco de dados"""
        try:
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            return conn
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return None
    
    @staticmethod
    def execute_query(query, params=None):
        """Executa uma query e retorna resultados"""
        conn = DatabaseConnection.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"❌ Erro na query: {e}")
            return None
    
    @staticmethod
    def insert_or_update(query, params):
        """Insere ou atualiza dados"""
        conn = DatabaseConnection.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir/atualizar: {e}")
            conn.close()
            return False


# 📋 EXEMPLOS DE USO:

class Barbeiros:
    """Gerenciar barbeiros"""
    
    @staticmethod
    def get_all():
        """Retorna todos os barbeiros"""
        query = "SELECT * FROM barbeiros ORDER BY nome"
        return DatabaseConnection.execute_query(query)
    
    @staticmethod
    def get_by_id(barbeiro_id):
        """Retorna barbeiro específico"""
        query = "SELECT * FROM barbeiros WHERE id = %s"
        results = DatabaseConnection.execute_query(query, (barbeiro_id,))
        return results[0] if results else None
    
    @staticmethod
    def create(nome, telefone, email=None):
        """Cria novo barbeiro"""
        query = """
        INSERT INTO barbeiros (nome, telefone, email)
        VALUES (%s, %s, %s)
        RETURNING id
        """
        conn = DatabaseConnection.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, (nome, telefone, email))
            new_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            return new_id
        except Exception as e:
            print(f"❌ Erro ao criar barbeiro: {e}")
            conn.close()
            return None
    
    @staticmethod
    def update(barbeiro_id, nome=None, telefone=None, email=None):
        """Atualiza dados do barbeiro"""
        updates = []
        params = []
        
        if nome:
            updates.append("nome = %s")
            params.append(nome)
        if telefone:
            updates.append("telefone = %s")
            params.append(telefone)
        if email:
            updates.append("email = %s")
            params.append(email)
        
        if not updates:
            return False
        
        params.append(barbeiro_id)
        query = f"UPDATE barbeiros SET {', '.join(updates)} WHERE id = %s"
        return DatabaseConnection.insert_or_update(query, tuple(params))


class Servicos:
    """Gerenciar serviços"""
    
    @staticmethod
    def get_all():
        """Retorna todos os serviços"""
        query = "SELECT * FROM servicos ORDER BY nome"
        return DatabaseConnection.execute_query(query)
    
    @staticmethod
    def get_by_id(servico_id):
        """Retorna serviço específico"""
        query = "SELECT * FROM servicos WHERE id = %s"
        results = DatabaseConnection.execute_query(query, (servico_id,))
        return results[0] if results else None
    
    @staticmethod
    def create(nome, duracao_minutos, preco):
        """Cria novo serviço"""
        query = """
        INSERT INTO servicos (nome, duracao_minutos, preco)
        VALUES (%s, %s, %s)
        RETURNING id
        """
        return DatabaseConnection.insert_or_update(query, (nome, duracao_minutos, preco))


class Agendamentos:
    """Gerenciar agendamentos"""
    
    @staticmethod
    def get_all():
        """Retorna todos os agendamentos"""
        query = """
        SELECT a.*, b.nome as barbeiro_nome, s.nome as servico_nome
        FROM agendamentos a
        LEFT JOIN barbeiros b ON a.barbeiro_id = b.id
        LEFT JOIN servicos s ON a.servico_id = s.id
        ORDER BY a.data_agendamento DESC
        """
        return DatabaseConnection.execute_query(query)
    
    @staticmethod
    def get_by_date(data):
        """Retorna agendamentos de uma data específica"""
        query = """
        SELECT a.*, b.nome as barbeiro_nome, s.nome as servico_nome
        FROM agendamentos a
        LEFT JOIN barbeiros b ON a.barbeiro_id = b.id
        LEFT JOIN servicos s ON a.servico_id = s.id
        WHERE DATE(a.data_agendamento) = %s
        ORDER BY a.data_agendamento
        """
        return DatabaseConnection.execute_query(query, (data,))
    
    @staticmethod
    def get_by_barbeiro(barbeiro_id, data_inicio=None, data_fim=None):
        """Retorna agendamentos de um barbeiro"""
        if data_inicio and data_fim:
            query = """
            SELECT a.*, b.nome as barbeiro_nome, s.nome as servico_nome
            FROM agendamentos a
            LEFT JOIN barbeiros b ON a.barbeiro_id = b.id
            LEFT JOIN servicos s ON a.servico_id = s.id
            WHERE a.barbeiro_id = %s AND a.data_agendamento BETWEEN %s AND %s
            ORDER BY a.data_agendamento
            """
            return DatabaseConnection.execute_query(query, (barbeiro_id, data_inicio, data_fim))
        else:
            query = """
            SELECT a.*, b.nome as barbeiro_nome, s.nome as servico_nome
            FROM agendamentos a
            LEFT JOIN barbeiros b ON a.barbeiro_id = b.id
            LEFT JOIN servicos s ON a.servico_id = s.id
            WHERE a.barbeiro_id = %s
            ORDER BY a.data_agendamento DESC
            """
            return DatabaseConnection.execute_query(query, (barbeiro_id,))
    
    @staticmethod
    def create(barbeiro_id, cliente_nome, cliente_telefone, data_agendamento, servico_id, status='pendente'):
        """Cria novo agendamento"""
        query = """
        INSERT INTO agendamentos (barbeiro_id, cliente_nome, cliente_telefone, data_agendamento, servico_id, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        conn = DatabaseConnection.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, (barbeiro_id, cliente_nome, cliente_telefone, data_agendamento, servico_id, status))
            new_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            return new_id
        except Exception as e:
            print(f"❌ Erro ao criar agendamento: {e}")
            conn.close()
            return None
    
    @staticmethod
    def update_status(agendamento_id, novo_status):
        """Atualiza status do agendamento"""
        query = "UPDATE agendamentos SET status = %s WHERE id = %s"
        return DatabaseConnection.insert_or_update(query, (novo_status, agendamento_id))
    
    @staticmethod
    def delete(agendamento_id):
        """Deleta um agendamento"""
        query = "DELETE FROM agendamentos WHERE id = %s"
        return DatabaseConnection.insert_or_update(query, (agendamento_id,))


# 📝 EXEMPLOS DE COMO USAR NO FLASK:

"""
# No seu app.py, substitua as queries do SQLite por isso:

from database_config_exemplo import Barbeiros, Servicos, Agendamentos

@app.route('/barbeiros')
def get_barbeiros():
    barbeiros = Barbeiros.get_all()
    return jsonify(barbeiros)

@app.route('/servicos')
def get_servicos():
    servicos = Servicos.get_all()
    return jsonify(servicos)

@app.route('/agendar', methods=['POST'])
def agendar():
    data = request.json
    novo_id = Agendamentos.create(
        barbeiro_id=data['barbeiro_id'],
        cliente_nome=data['cliente_nome'],
        cliente_telefone=data['cliente_telefone'],
        data_agendamento=data['data_agendamento'],
        servico_id=data['servico_id']
    )
    return jsonify({'id': novo_id, 'status': 'criado'})

@app.route('/agendamentos/<data>')
def get_agendamentos_por_data(data):
    agendamentos = Agendamentos.get_by_date(data)
    return jsonify(agendamentos)
"""

if __name__ == '__main__':
    # Teste rápido
    print("🧪 Testando conexão com banco...")
    
    barbeiros = Barbeiros.get_all()
    if barbeiros:
        print(f"✅ Encontrados {len(barbeiros)} barbeiros")
        for b in barbeiros:
            print(f"  - {b['nome']} ({b['telefone']})")
    
    servicos = Servicos.get_all()
    if servicos:
        print(f"✅ Encontrados {len(servicos)} serviços")
        for s in servicos:
            print(f"  - {s['nome']} ({s['duracao_minutos']}min - R${s['preco']})")
    
    print("\n✅ Tudo funcionando!")
