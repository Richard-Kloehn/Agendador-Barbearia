"""
Endpoint de debug para verificar dados no banco de produção
"""
from flask import Blueprint, jsonify, request
from models import Barbeiro, HorarioBarbeiro, ConfiguracaoBarbearia, Servico
from database import db
from datetime import datetime

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
            'banco_url': str(db_url).split('@')[0] + '@***',
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

@debug_bp.route('/debug/teste-data', methods=['GET'])
def debug_teste_data():
    """Testa busca de barbeiros para uma data específica"""
    try:
        data_str = request.args.get('data', '2026-02-03')  # Default terça
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        
        # Calcular dia da semana
        dia_semana_python = data.weekday()
        
        # Buscar config
        config = ConfiguracaoBarbearia.query.first()
        
        # Buscar horários para esse dia
        horarios = HorarioBarbeiro.query.filter_by(
            dia_semana=dia_semana_python,
            ativo=True
        ).all()
        
        # Buscar barbeiros
        barbeiros = Barbeiro.query.filter_by(ativo=True).all()
        
        return jsonify({
            'data_testada': data_str,
            'dia_da_semana': data.strftime('%A'),
            'python_weekday': dia_semana_python,
            'dias_funcionamento_config': config.dias_funcionamento if config else None,
            'total_barbeiros_ativos': len(barbeiros),
            'total_horarios_encontrados': len(horarios),
            'horarios_encontrados': [{
                'barbeiro_id': h.barbeiro_id,
                'barbeiro_nome': Barbeiro.query.get(h.barbeiro_id).nome if h.barbeiro_id else None,
                'dia_semana': h.dia_semana,
                'horario': f"{h.horario_inicio}-{h.horario_fim}"
            } for h in horarios]
        })
    
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'tipo': type(e).__name__
        }), 500
