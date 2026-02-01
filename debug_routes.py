"""
Endpoint de debug para verificar dados no banco de produção
"""
from flask import Blueprint, jsonify
from models import Barbeiro, HorarioBarbeiro, ConfiguracaoBarbearia, Servico
from database import db

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/info', methods=['GET'])
def debug_info():
    """Retorna informações do banco de dados para debug"""
    try:
        # Informações do banco
        db_url = db.engine.url
        db_type = "PostgreSQL" if "postgresql" in str(db_url) else "SQLite"
        
        # Configuração
        config = ConfiguracaoBarbearia.query.first()
        config_info = {
            'nome': config.nome_barbearia if config else None,
            'dias_funcionamento': config.dias_funcionamento if config else None,
            'horario': f"{config.horario_abertura} - {config.horario_fechamento}" if config else None
        } if config else None
        
        # Barbeiros
        barbeiros = Barbeiro.query.all()
        barbeiros_info = []
        
        for b in barbeiros:
            horarios = HorarioBarbeiro.query.filter_by(barbeiro_id=b.id).order_by(HorarioBarbeiro.dia_semana).all()
            barbeiros_info.append({
                'id': b.id,
                'nome': b.nome,
                'ativo': b.ativo,
                'total_horarios': len(horarios),
                'horarios': [{
                    'dia_semana': h.dia_semana,
                    'horario_inicio': h.horario_inicio,
                    'horario_fim': h.horario_fim,
                    'ativo': h.ativo
                } for h in horarios]
            })
        
        # Serviços
        servicos = Servico.query.all()
        servicos_info = [{
            'id': s.id,
            'nome': s.nome,
            'duracao': s.duracao,
            'preco': float(s.preco),
            'ativo': s.ativo
        } for s in servicos]
        
        return jsonify({
            'banco': db_type,
            'banco_url': str(db_url).split('@')[0] + '@***',  # Ocultar credenciais
            'configuracao': config_info,
            'total_barbeiros': len(barbeiros),
            'barbeiros': barbeiros_info,
            'total_servicos': len(servicos),
            'servicos': servicos_info
        })
    
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'tipo': type(e).__name__
        }), 500
