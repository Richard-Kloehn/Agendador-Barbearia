from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, time
from database import db
from models import Agendamento, ConfiguracaoBarbearia, DiaIndisponivel, Cliente, HorarioEspecial, Barbeiro, Servico
from services.whatsapp_service import enviar_confirmacao_agendamento, enviar_lembrete_whatsapp
import re

api_bp = Blueprint('api', __name__)
admin_bp = Blueprint('admin', __name__)

def validar_telefone(telefone):
    """Valida formato de telefone brasileiro"""
    telefone = re.sub(r'\D', '', telefone)
    return len(telefone) >= 10 and len(telefone) <= 11

def gerar_horarios_disponiveis(data, config, barbeiro_id=None, duracao_servico=None):
    """Gera lista de horários disponíveis para uma data, barbeiro e serviço específicos"""
    horarios = []
    
    # Verificar se existe horário especial para esta data
    horario_especial = HorarioEspecial.query.filter_by(data=data).first()
    
    if horario_especial:
        # Usar horários especiais
        hora_inicio = datetime.strptime(horario_especial.horario_abertura, '%H:%M').time()
        hora_fim = datetime.strptime(horario_especial.horario_fechamento, '%H:%M').time()
        almoco_inicio = None
        almoco_fim = None
        if horario_especial.intervalo_almoco_inicio and horario_especial.intervalo_almoco_fim:
            almoco_inicio = datetime.strptime(horario_especial.intervalo_almoco_inicio, '%H:%M').time()
            almoco_fim = datetime.strptime(horario_especial.intervalo_almoco_fim, '%H:%M').time()
    else:
        # Usar horários normais da configuração
        hora_inicio = datetime.strptime(config.horario_abertura, '%H:%M').time()
        hora_fim = datetime.strptime(config.horario_fechamento, '%H:%M').time()
        almoco_inicio = None
        almoco_fim = None
        if config.intervalo_almoco_inicio and config.intervalo_almoco_fim:
            almoco_inicio = datetime.strptime(config.intervalo_almoco_inicio, '%H:%M').time()
            almoco_fim = datetime.strptime(config.intervalo_almoco_fim, '%H:%M').time()
    
    # Usar duração do serviço se fornecida, senão usar configuração
    if duracao_servico:
        duracao = timedelta(minutes=duracao_servico)
    else:
        duracao = timedelta(minutes=config.duracao_atendimento)
    
    # Gerar horários
    hora_atual = datetime.combine(data, hora_inicio)
    hora_final = datetime.combine(data, hora_fim)
    agora = datetime.now()
    
    while hora_atual < hora_final:
        # Se for hoje, ocultar horários que já passaram
        if data == agora.date() and hora_atual <= agora:
            hora_atual += duracao
            continue
        
        # Verificar se não está no horário de almoço
        if almoco_inicio and almoco_fim:
            if almoco_inicio <= hora_atual.time() < almoco_fim:
                hora_atual += duracao
                continue
        
        # Verificar se horário já está agendado para este barbeiro específico
        query = Agendamento.query.filter(
            Agendamento.data_hora == hora_atual,
            Agendamento.status.in_(['pendente', 'confirmado'])
        )
        
        if barbeiro_id:
            query = query.filter(Agendamento.barbeiro_id == barbeiro_id)
        
        agendamento_existente = query.first()
        
        if not agendamento_existente:
            horarios.append(hora_atual.strftime('%H:%M'))
        
        hora_atual += duracao
    
    return horarios

@api_bp.route('/horarios-disponiveis', methods=['GET'])
def get_horarios_disponiveis():
    """Retorna horários disponíveis para uma data, barbeiro e serviço"""
    data_str = request.args.get('data')
    barbeiro_id = request.args.get('barbeiro_id', type=int)
    servico_id = request.args.get('servico_id', type=int)
    
    if not data_str:
        return jsonify({'erro': 'Data não fornecida'}), 400
    
    if not barbeiro_id or not servico_id:
        return jsonify({'erro': 'Barbeiro e serviço são obrigatórios'}), 400
    
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Não permitir agendamentos para datas passadas
    if data < datetime.now().date():
        return jsonify({'erro': 'Não é possível agendar para datas passadas'}), 400
    
    # Verificar se é dia indisponível
    dia_indisponivel = DiaIndisponivel.query.filter_by(data=data).first()
    if dia_indisponivel:
        return jsonify({'disponiveis': [], 'mensagem': f'Dia indisponível: {dia_indisponivel.motivo}'})
    
    # Obter configuração
    config = ConfiguracaoBarbearia.query.first()
    if not config:
        return jsonify({'erro': 'Configuração não encontrada'}), 500
    
    # Verificar barbeiro
    barbeiro = Barbeiro.query.get(barbeiro_id)
    if not barbeiro:
        return jsonify({'erro': 'Barbeiro não encontrado'}), 404
    
    # Verificar serviço
    servico = Servico.query.get(servico_id)
    if not servico:
        return jsonify({'erro': 'Serviço não encontrado'}), 404
    
    # Verificar dia da semana
    dias_funcionamento = [int(d) for d in config.dias_funcionamento.split(',')]
    if data.weekday() not in dias_funcionamento:
        return jsonify({'disponiveis': [], 'mensagem': 'Barbearia fechada neste dia'})
    
    horarios = gerar_horarios_disponiveis(data, config, barbeiro_id, servico.duracao)
    
    return jsonify({
        'disponiveis': horarios,
        'data': data_str,
        'barbeiro': barbeiro.to_dict(),
        'servico': servico.to_dict()
    })

@api_bp.route('/buscar-cliente', methods=['GET'])
def buscar_cliente():
    """Busca cliente por nome ou telefone para autocompletar"""
    termo = request.args.get('termo', '')
    
    if len(termo) < 3:
        return jsonify({'clientes': []})
    
    # Buscar por nome ou telefone
    clientes = Cliente.query.filter(
        db.or_(
            Cliente.nome_completo.ilike(f'%{termo}%'),
            Cliente.telefone.like(f'%{termo}%')
        )
    ).limit(5).all()
    
    return jsonify({
        'clientes': [c.to_dict() for c in clientes]
    })

@api_bp.route('/agendar', methods=['POST'])
def criar_agendamento():
    """Cria novo agendamento e salva/atualiza dados do cliente"""
    dados = request.get_json()
    
    # Validações
    if not dados.get('nome_cliente') or not dados.get('data_hora') or not dados.get('barbeiro_id') or not dados.get('servico_id'):
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    # Validar barbeiro e serviço
    barbeiro_id = dados.get('barbeiro_id')
    servico_id = dados.get('servico_id')
    
    barbeiro = Barbeiro.query.get(barbeiro_id)
    if not barbeiro or not barbeiro.ativo:
        return jsonify({'erro': 'Barbeiro não disponível'}), 400
    
    servico = Servico.query.get(servico_id)
    if not servico or not servico.ativo:
        return jsonify({'erro': 'Serviço não disponível'}), 400
    
    # Verificar se o barbeiro oferece esse serviço
    if servico not in barbeiro.servicos:
        return jsonify({'erro': 'Este serviço não está disponível para o barbeiro selecionado'}), 400
    
    telefone = dados.get('telefone', '').strip()
    
    # Se telefone foi fornecido, validar
    if telefone and not validar_telefone(telefone):
        return jsonify({'erro': 'Telefone inválido'}), 400
    
    try:
        data_hora = datetime.fromisoformat(dados['data_hora'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'erro': 'Formato de data/hora inválido'}), 400
    
    # Verificar se horário já está ocupado PELO MESMO BARBEIRO
    agendamento_existente = Agendamento.query.filter(
        Agendamento.data_hora == data_hora,
        Agendamento.barbeiro_id == barbeiro_id,
        Agendamento.status.in_(['pendente', 'confirmado'])
    ).first()
    
    if agendamento_existente:
        return jsonify({'erro': 'Horário não está mais disponível'}), 409
    
    telefone_limpo = re.sub(r'\D', '', telefone) if telefone else None
    
    # Buscar ou criar cliente (apenas se telefone fornecido)
    cliente = None
    if telefone_limpo:
        cliente = Cliente.query.filter_by(telefone=telefone_limpo).first()
        
        if not cliente:
            # Criar novo cliente
            cliente = Cliente(
                nome_completo=dados['nome_cliente'],
                telefone=telefone_limpo,
                email=dados.get('email', ''),
                total_agendamentos=0
            )
            db.session.add(cliente)
        else:
            # Atualizar dados do cliente se mudaram
            cliente.nome_completo = dados['nome_cliente']
            if dados.get('email'):
                cliente.email = dados['email']
        
        # Atualizar estatísticas do cliente
        cliente.total_agendamentos += 1
        cliente.ultimo_agendamento = data_hora
    
    # Criar agendamento
    agendamento = Agendamento(
        cliente_id=cliente.id if cliente else None,
        nome_cliente=dados['nome_cliente'],
        telefone=telefone_limpo or '',
        data_hora=data_hora,
        barbeiro_id=barbeiro_id,
        servico_id=servico_id,
        status='pendente',
        observacoes=dados.get('observacoes', '')
    )
    
    db.session.add(agendamento)
    db.session.commit()
    
    # Enviar confirmação por WhatsApp apenas se telefone foi fornecido
    if telefone_limpo:
        try:
            enviar_confirmacao_agendamento(agendamento)
        except Exception as e:
            print(f"Erro ao enviar WhatsApp: {e}")
    
    return jsonify({
        'mensagem': 'Agendamento criado com sucesso!',
        'agendamento': agendamento.to_dict(),
        'cliente': cliente.to_dict() if cliente else None
    }), 201

@api_bp.route('/confirmar/<token>', methods=['POST'])
def confirmar_agendamento_api(token):
    """Confirma ou cancela agendamento via token"""
    agendamento = Agendamento.query.filter_by(token_confirmacao=token).first()
    
    if not agendamento:
        return jsonify({'erro': 'Token inválido'}), 404
    
    dados = request.get_json()
    acao = dados.get('acao')  # 'confirmar' ou 'cancelar'
    
    if acao == 'confirmar':
        agendamento.status = 'confirmado'
        agendamento.confirmado_cliente = True
        mensagem = 'Agendamento confirmado com sucesso!'
    elif acao == 'cancelar':
        agendamento.status = 'cancelado'
        mensagem = 'Agendamento cancelado'
    else:
        return jsonify({'erro': 'Ação inválida'}), 400
    
    db.session.commit()
    
    return jsonify({'mensagem': mensagem})

# ========== ROTAS ADMIN ==========

@admin_bp.route('/agendamentos', methods=['GET'])
def listar_agendamentos():
    """Lista todos os agendamentos"""
    data_str = request.args.get('data')
    status = request.args.get('status')
    
    query = Agendamento.query
    
    if data_str:
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            inicio = datetime.combine(data, time.min)
            fim = datetime.combine(data, time.max)
            query = query.filter(Agendamento.data_hora >= inicio, Agendamento.data_hora <= fim)
        except ValueError:
            pass
    
    if status:
        query = query.filter_by(status=status)
    
    agendamentos = query.order_by(Agendamento.data_hora.desc()).all()
    
    return jsonify({
        'agendamentos': [a.to_dict() for a in agendamentos]
    })

@admin_bp.route('/agendamentos/<int:id>', methods=['PUT'])
def atualizar_agendamento(id):
    """Atualiza status de agendamento"""
    agendamento = Agendamento.query.get_or_404(id)
    dados = request.get_json()
    
    if 'status' in dados:
        agendamento.status = dados['status']
    
    if 'observacoes' in dados:
        agendamento.observacoes = dados['observacoes']
    
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Agendamento atualizado',
        'agendamento': agendamento.to_dict()
    })

@admin_bp.route('/agendamentos/<int:id>', methods=['DELETE'])
def deletar_agendamento(id):
    """Deleta agendamento"""
    agendamento = Agendamento.query.get_or_404(id)
    db.session.delete(agendamento)
    db.session.commit()
    
    return jsonify({'mensagem': 'Agendamento deletado'})

@admin_bp.route('/configuracao', methods=['GET'])
def get_configuracao():
    """Retorna configuração da barbearia"""
    config = ConfiguracaoBarbearia.query.first()
    if not config:
        return jsonify({'erro': 'Configuração não encontrada'}), 404
    
    return jsonify(config.to_dict())

@admin_bp.route('/configuracao', methods=['PUT'])
def atualizar_configuracao():
    """Atualiza configuração da barbearia"""
    config = ConfiguracaoBarbearia.query.first()
    if not config:
        return jsonify({'erro': 'Configuração não encontrada'}), 404
    
    dados = request.get_json()
    
    if 'nome_barbearia' in dados:
        config.nome_barbearia = dados['nome_barbearia']
    if 'horario_abertura' in dados:
        config.horario_abertura = dados['horario_abertura']
    if 'horario_fechamento' in dados:
        config.horario_fechamento = dados['horario_fechamento']
    if 'duracao_atendimento' in dados:
        config.duracao_atendimento = dados['duracao_atendimento']
    if 'intervalo_almoco_inicio' in dados:
        config.intervalo_almoco_inicio = dados['intervalo_almoco_inicio']
    if 'intervalo_almoco_fim' in dados:
        config.intervalo_almoco_fim = dados['intervalo_almoco_fim']
    if 'dias_funcionamento' in dados:
        config.dias_funcionamento = dados['dias_funcionamento']
    
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Configuração atualizada',
        'configuracao': config.to_dict()
    })

@admin_bp.route('/estatisticas', methods=['GET'])
def get_estatisticas():
    """Retorna estatísticas de agendamentos"""
    hoje = datetime.now().date()
    
    # Total de agendamentos
    total = Agendamento.query.count()
    
    # Agendamentos hoje
    inicio_hoje = datetime.combine(hoje, time.min)
    fim_hoje = datetime.combine(hoje, time.max)
    hoje_count = Agendamento.query.filter(
        Agendamento.data_hora >= inicio_hoje,
        Agendamento.data_hora <= fim_hoje
    ).count()
    
    # Agendamentos pendentes
    pendentes = Agendamento.query.filter_by(status='pendente').count()
    
    # Agendamentos confirmados
    confirmados = Agendamento.query.filter_by(status='confirmado').count()
    
    return jsonify({
        'total': total,
        'hoje': hoje_count,
        'pendentes': pendentes,
        'confirmados': confirmados
    })

# ===== ROTAS DE HORÁRIOS ESPECIAIS =====

@admin_bp.route('/horarios-especiais', methods=['GET'])
def listar_horarios_especiais():
    """Lista todos os horários especiais"""
    horarios = HorarioEspecial.query.order_by(HorarioEspecial.data).all()
    return jsonify({
        'horarios_especiais': [h.to_dict() for h in horarios]
    })

@admin_bp.route('/horarios-especiais', methods=['POST'])
def criar_horario_especial():
    """Cria um novo horário especial"""
    dados = request.get_json()
    
    if not dados.get('data') or not dados.get('horario_abertura') or not dados.get('horario_fechamento'):
        return jsonify({'erro': 'Data, horário de abertura e fechamento são obrigatórios'}), 400
    
    try:
        data = datetime.strptime(dados['data'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'erro': 'Formato de data inválido'}), 400
    
    # Verificar se já existe
    existente = HorarioEspecial.query.filter_by(data=data).first()
    if existente:
        return jsonify({'erro': 'Já existe horário especial para esta data'}), 409
    
    horario = HorarioEspecial(
        data=data,
        descricao=dados.get('descricao', ''),
        horario_abertura=dados['horario_abertura'],
        horario_fechamento=dados['horario_fechamento'],
        intervalo_almoco_inicio=dados.get('intervalo_almoco_inicio'),
        intervalo_almoco_fim=dados.get('intervalo_almoco_fim')
    )
    
    db.session.add(horario)
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Horário especial criado',
        'horario': horario.to_dict()
    }), 201

@admin_bp.route('/horarios-especiais/<int:id>', methods=['DELETE'])
def deletar_horario_especial(id):
    """Deleta um horário especial"""
    horario = HorarioEspecial.query.get(id)
    if not horario:
        return jsonify({'erro': 'Horário especial não encontrado'}), 404
    
    db.session.delete(horario)
    db.session.commit()
    
    return jsonify({'mensagem': 'Horário especial deletado'})

# ===== ROTAS DE BARBEIROS =====

@api_bp.route('/barbeiros', methods=['GET'])
def listar_barbeiros():
    """Lista todos os barbeiros ativos"""
    barbeiros = Barbeiro.query.filter_by(ativo=True).order_by(Barbeiro.ordem).all()
    return jsonify({
        'barbeiros': [b.to_dict() for b in barbeiros]
    })

@admin_bp.route('/barbeiros', methods=['GET'])
def admin_listar_barbeiros():
    """Lista todos os barbeiros"""
    barbeiros = Barbeiro.query.order_by(Barbeiro.ordem).all()
    return jsonify({
        'barbeiros': [b.to_dict() for b in barbeiros]
    })

@admin_bp.route('/barbeiros', methods=['POST'])
def criar_barbeiro():
    """Cria um novo barbeiro"""
    dados = request.get_json()
    
    if not dados.get('nome'):
        return jsonify({'erro': 'Nome é obrigatório'}), 400
    
    barbeiro = Barbeiro(
        nome=dados['nome'],
        foto_url=dados.get('foto_url', ''),
        ativo=dados.get('ativo', True),
        ordem=dados.get('ordem', 0)
    )
    
    db.session.add(barbeiro)
    db.session.commit()
    
    # Associar serviços se fornecidos
    if dados.get('servicos'):
        for servico_id in dados['servicos']:
            servico = Servico.query.get(servico_id)
            if servico:
                barbeiro.servicos.append(servico)
        db.session.commit()
    
    return jsonify({
        'mensagem': 'Barbeiro criado',
        'barbeiro': barbeiro.to_dict()
    }), 201

@admin_bp.route('/barbeiros/<int:id>', methods=['PUT'])
def atualizar_barbeiro(id):
    """Atualiza um barbeiro"""
    barbeiro = Barbeiro.query.get(id)
    if not barbeiro:
        return jsonify({'erro': 'Barbeiro não encontrado'}), 404
    
    dados = request.get_json()
    
    if 'nome' in dados:
        barbeiro.nome = dados['nome']
    if 'foto_url' in dados:
        barbeiro.foto_url = dados['foto_url']
    if 'ativo' in dados:
        barbeiro.ativo = dados['ativo']
    if 'ordem' in dados:
        barbeiro.ordem = dados['ordem']
    
    # Atualizar serviços
    if 'servicos' in dados:
        barbeiro.servicos = []
        for servico_id in dados['servicos']:
            servico = Servico.query.get(servico_id)
            if servico:
                barbeiro.servicos.append(servico)
    
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Barbeiro atualizado',
        'barbeiro': barbeiro.to_dict()
    })

@admin_bp.route('/barbeiros/<int:id>', methods=['DELETE'])
def deletar_barbeiro(id):
    """Deleta um barbeiro"""
    barbeiro = Barbeiro.query.get(id)
    if not barbeiro:
        return jsonify({'erro': 'Barbeiro não encontrado'}), 404
    
    db.session.delete(barbeiro)
    db.session.commit()
    
    return jsonify({'mensagem': 'Barbeiro deletado'})

# ===== ROTAS DE SERVIÇOS =====

@api_bp.route('/servicos', methods=['GET'])
def listar_servicos():
    """Lista todos os serviços ativos"""
    servicos = Servico.query.filter_by(ativo=True).all()
    return jsonify({
        'servicos': [s.to_dict() for s in servicos]
    })

@admin_bp.route('/servicos', methods=['GET'])
def admin_listar_servicos():
    """Lista todos os serviços"""
    servicos = Servico.query.all()
    return jsonify({
        'servicos': [s.to_dict() for s in servicos]
    })

@admin_bp.route('/servicos', methods=['POST'])
def criar_servico():
    """Cria um novo serviço"""
    dados = request.get_json()
    
    if not dados.get('nome') or not dados.get('duracao') or not dados.get('preco'):
        return jsonify({'erro': 'Nome, duração e preço são obrigatórios'}), 400
    
    servico = Servico(
        nome=dados['nome'],
        descricao=dados.get('descricao', ''),
        duracao=dados['duracao'],
        preco=dados['preco'],
        ativo=dados.get('ativo', True)
    )
    
    db.session.add(servico)
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Serviço criado',
        'servico': servico.to_dict()
    }), 201

@admin_bp.route('/servicos/<int:id>', methods=['PUT'])
def atualizar_servico(id):
    """Atualiza um serviço"""
    servico = Servico.query.get(id)
    if not servico:
        return jsonify({'erro': 'Serviço não encontrado'}), 404
    
    dados = request.get_json()
    
    if 'nome' in dados:
        servico.nome = dados['nome']
    if 'descricao' in dados:
        servico.descricao = dados['descricao']
    if 'duracao' in dados:
        servico.duracao = dados['duracao']
    if 'preco' in dados:
        servico.preco = dados['preco']
    if 'ativo' in dados:
        servico.ativo = dados['ativo']
    
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Serviço atualizado',
        'servico': servico.to_dict()
    })

@admin_bp.route('/servicos/<int:id>', methods=['DELETE'])
def deletar_servico(id):
    """Deleta um serviço"""
    servico = Servico.query.get(id)
    if not servico:
        return jsonify({'erro': 'Serviço não encontrado'}), 404
    
    db.session.delete(servico)
    db.session.commit()
    
    return jsonify({'mensagem': 'Serviço deletado'})
