from database import db
from datetime import datetime
import secrets

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(100))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    total_agendamentos = db.Column(db.Integer, default=0)
    ultimo_agendamento = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)
    
    # Relacionamento com agendamentos
    agendamentos = db.relationship('Agendamento', backref='cliente', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'telefone': self.telefone,
            'email': self.email,
            'total_agendamentos': self.total_agendamentos,
            'ultimo_agendamento': self.ultimo_agendamento.isoformat() if self.ultimo_agendamento else None,
            'observacoes': self.observacoes
        }

class Barbeiro(db.Model):
    __tablename__ = 'barbeiros'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    foto_url = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)
    ordem = db.Column(db.Integer, default=0)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='barbeiro', lazy=True)
    servicos = db.relationship('Servico', secondary='barbeiro_servico', backref='barbeiros')
    
    def to_dict(self):
        servicos = self.servicos if self.servicos else []
        return {
            'id': self.id,
            'nome': self.nome,
            'foto_url': self.foto_url,
            'ativo': self.ativo,
            'ordem': self.ordem,
            'servicos': [s.to_dict() for s in servicos],
            'servicos_ids': [s.id for s in servicos],
            'servicos_count': len(servicos)
        }

class Servico(db.Model):
    __tablename__ = 'servicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200))
    duracao = db.Column(db.Integer, nullable=False)  # em minutos
    preco = db.Column(db.Float, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='servico', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'duracao': self.duracao,
            'preco': self.preco,
            'ativo': self.ativo
        }

# Tabela de associação entre Barbeiro e Servico
barbeiro_servico = db.Table('barbeiro_servico',
    db.Column('barbeiro_id', db.Integer, db.ForeignKey('barbeiros.id'), primary_key=True),
    db.Column('servico_id', db.Integer, db.ForeignKey('servicos.id'), primary_key=True)
)

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    nome_cliente = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=True, default='')
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='confirmado')  # confirmado, cancelado, concluido
    token_confirmacao = db.Column(db.String(100), unique=True)
    lembrete_enviado = db.Column(db.Boolean, default=False)
    confirmado_cliente = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    observacoes = db.Column(db.Text)
    
    def __init__(self, **kwargs):
        super(Agendamento, self).__init__(**kwargs)
        if not self.token_confirmacao:
            self.token_confirmacao = secrets.token_urlsafe(32)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_cliente': self.nome_cliente,
            'telefone': self.telefone,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'status': self.status,
            'lembrete_enviado': self.lembrete_enviado,
            'confirmado_cliente': self.confirmado_cliente,
            'observacoes': self.observacoes,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'barbeiro': self.barbeiro.to_dict() if self.barbeiro else None,
            'servico': self.servico.to_dict() if self.servico else None
        }

class ConfiguracaoBarbearia(db.Model):
    __tablename__ = 'configuracao'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_barbearia = db.Column(db.String(100), nullable=False)
    horario_abertura = db.Column(db.String(5), nullable=False)  # formato HH:MM
    horario_fechamento = db.Column(db.String(5), nullable=False)
    duracao_atendimento = db.Column(db.Integer, default=30)  # minutos
    intervalo_almoco_inicio = db.Column(db.String(5))
    intervalo_almoco_fim = db.Column(db.String(5))
    dias_funcionamento = db.Column(db.String(50), default='1,2,3,4,5,6')  # 0=domingo, 6=sábado
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_barbearia': self.nome_barbearia,
            'horario_abertura': self.horario_abertura,
            'horario_fechamento': self.horario_fechamento,
            'duracao_atendimento': self.duracao_atendimento,
            'intervalo_almoco_inicio': self.intervalo_almoco_inicio,
            'intervalo_almoco_fim': self.intervalo_almoco_fim,
            'dias_funcionamento': self.dias_funcionamento
        }

class DiaIndisponivel(db.Model):
    __tablename__ = 'dias_indisponiveis'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, unique=True)
    motivo = db.Column(db.String(200))
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.isoformat() if self.data else None,
            'motivo': self.motivo
        }

class HorarioEspecial(db.Model):
    __tablename__ = 'horarios_especiais'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=True)  # null = todos os barbeiros
    descricao = db.Column(db.String(200))  # Ex: "Feriado", "Horário Reduzido"
    horario_abertura = db.Column(db.String(5))  # Ex: "09:00"
    horario_fechamento = db.Column(db.String(5))  # Ex: "14:00"
    intervalo_almoco_inicio = db.Column(db.String(5))
    intervalo_almoco_fim = db.Column(db.String(5))
    
    # Relacionamento
    barbeiro = db.relationship('Barbeiro', backref='horarios_especiais', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.isoformat() if self.data else None,
            'barbeiro_id': self.barbeiro_id,
            'barbeiro_nome': self.barbeiro.nome if self.barbeiro else 'Todos',
            'descricao': self.descricao,
            'horario_abertura': self.horario_abertura,
            'horario_fechamento': self.horario_fechamento,
            'intervalo_almoco_inicio': self.intervalo_almoco_inicio,
            'intervalo_almoco_fim': self.intervalo_almoco_fim
        }

class HorarioBarbeiro(db.Model):
    __tablename__ = 'horarios_barbeiros'
    
    id = db.Column(db.Integer, primary_key=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=domingo, 1=segunda, ..., 6=sábado
    horario_inicio = db.Column(db.String(5), nullable=False)  # Ex: "09:00"
    horario_fim = db.Column(db.String(5), nullable=False)  # Ex: "18:00"
    intervalo_almoco_inicio = db.Column(db.String(5))
    intervalo_almoco_fim = db.Column(db.String(5))
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamento
    barbeiro_rel = db.relationship('Barbeiro', backref='horarios', lazy=True)
    
    def to_dict(self):
        dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
        return {
            'id': self.id,
            'barbeiro_id': self.barbeiro_id,
            'barbeiro_nome': self.barbeiro_rel.nome if self.barbeiro_rel else None,
            'dia_semana': self.dia_semana,
            'dia_semana_nome': dias_semana[self.dia_semana],
            'horario_inicio': self.horario_inicio,
            'horario_fim': self.horario_fim,
            'intervalo_almoco_inicio': self.intervalo_almoco_inicio,
            'intervalo_almoco_fim': self.intervalo_almoco_fim,
            'ativo': self.ativo
        }
