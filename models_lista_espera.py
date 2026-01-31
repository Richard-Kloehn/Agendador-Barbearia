"""
Model para Lista de Espera
===========================
Permite clientes se cadastrarem para serem notificados quando horários ficarem disponíveis
"""

from database import db
from datetime import datetime

class ListaEspera(db.Model):
    """Cadastro de clientes na lista de espera"""
    __tablename__ = 'lista_espera'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    data_desejada = db.Column(db.Date, nullable=False)  # Data que o cliente deseja
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=True)  # Opcional
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=True)  # Opcional
    notificado = db.Column(db.Boolean, default=False)  # Se já foi notificado
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    data_notificacao = db.Column(db.DateTime, nullable=True)  # Quando foi notificado
    
    # Relacionamentos
    barbeiro = db.relationship('Barbeiro', backref='lista_espera')
    servico = db.relationship('Servico', backref='lista_espera')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_cliente': self.nome_cliente,
            'telefone': self.telefone,
            'data_desejada': self.data_desejada.strftime('%Y-%m-%d'),
            'barbeiro': self.barbeiro.to_dict() if self.barbeiro else None,
            'servico': self.servico.to_dict() if self.servico else None,
            'notificado': self.notificado,
            'data_cadastro': self.data_cadastro.isoformat(),
            'data_notificacao': self.data_notificacao.isoformat() if self.data_notificacao else None
        }
