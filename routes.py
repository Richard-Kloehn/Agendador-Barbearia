from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta, time, timezone
from database import db
import pytz
from sqlalchemy.orm import joinedload
from models import Agendamento, ConfiguracaoBarbearia, DiaIndisponivel, Cliente, HorarioEspecial, Barbeiro, Servico, HorarioBarbeiro
from werkzeug.utils import secure_filename
import re
import os
from functools import lru_cache
from sqlalchemy import and_, or_

# Importar serviço de WhatsApp com whapi.cloud (nova integração)
from services.whapi_service import enviar_confirmacao_agendamento, enviar_lembrete_whatsapp

api_bp = Blueprint('api', __name__)
admin_bp = Blueprint('admin', __name__)

# Cache para dados que mudam pouco
_cache_dias_com_barbeiros = {'data': None, 'valor': None}
_cache_config = {'data': None, 'valor': None}

def validar_telefone(telefone):
    """Valida formato de telefone brasileiro"""
    telefone = re.sub(r'\D', '', telefone)
    return len(telefone) >= 10 and len(telefone) <= 11

def gerar_horarios_disponiveis(data, config, barbeiro_id=None, duracao_servico=None):
    """Gera lista de horários disponíveis para uma data, barbeiro e serviço específicos (otimizado)"""
    horarios = []
    
    if not barbeiro_id:
        return horarios
    
    # Buscar horários especiais com uma única query (otimizado com or_)
    horarios_especiais = HorarioEspecial.query.filter(
        HorarioEspecial.data == data,
        or_(HorarioEspecial.barbeiro_id == barbeiro_id, HorarioEspecial.barbeiro_id == None)
    ).all()
    
    # Priorizar horário específico do barbeiro
    horario_especial = None
    for h in horarios_especiais:
        if h.barbeiro_id == barbeiro_id:
            horario_especial = h
            break
    
    if not horario_especial and horarios_especiais:
        horario_especial = horarios_especiais[0]
    
    if horario_especial and horario_especial.horario_abertura:
        # Usar horários especiais
        hora_inicio = datetime.strptime(horario_especial.horario_abertura, '%H:%M').time()
        hora_fim = datetime.strptime(horario_especial.horario_fechamento, '%H:%M').time()
        almoco_inicio = None
        almoco_fim = None
        if horario_especial.intervalo_almoco_inicio and horario_especial.intervalo_almoco_fim:
            almoco_inicio = datetime.strptime(horario_especial.intervalo_almoco_inicio, '%H:%M').time()
            almoco_fim = datetime.strptime(horario_especial.intervalo_almoco_fim, '%H:%M').time()
    else:
        # Usar horários do barbeiro
        dia_semana = data.weekday()  # 0=segunda, 6=domingo
        if dia_semana == 6:  # domingo
            dia_semana = 0
        else:
            dia_semana += 1
        
        horario_barbeiro = HorarioBarbeiro.query.filter_by(
            barbeiro_id=barbeiro_id, 
            dia_semana=dia_semana,
            ativo=True
        ).first()
        
        if not horario_barbeiro:
            # Barbeiro não trabalha neste dia
            return []
        
        hora_inicio = datetime.strptime(horario_barbeiro.horario_inicio, '%H:%M').time()
        hora_fim = datetime.strptime(horario_barbeiro.horario_fim, '%H:%M').time()
        almoco_inicio = None
        almoco_fim = None
        if horario_barbeiro.intervalo_almoco_inicio and horario_barbeiro.intervalo_almoco_fim:
            almoco_inicio = datetime.strptime(horario_barbeiro.intervalo_almoco_inicio, '%H:%M').time()
            almoco_fim = datetime.strptime(horario_barbeiro.intervalo_almoco_fim, '%H:%M').time()
    
    # Usar duração do serviço se fornecida, senão usar configuração
    if duracao_servico:
        duracao = timedelta(minutes=duracao_servico)
    else:
        duracao = timedelta(minutes=config.duracao_atendimento)
    
    # Gerar horários
    hora_atual = datetime.combine(data, hora_inicio)
    hora_final = datetime.combine(data, hora_fim)
    # Usar timezone do Brasil
    tz_brasil = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(tz_brasil).replace(tzinfo=None)
    
    # Pré-carregar agendamentos do barbeiro nesta data (uma única query em vez de muitas)
    agendamentos_dia = Agendamento.query.filter(
        Agendamento.data_hora >= datetime.combine(data, time(0, 0)),
        Agendamento.data_hora <= datetime.combine(data, time(23, 59)),
        Agendamento.barbeiro_id == barbeiro_id,
        Agendamento.status.in_(['pendente', 'confirmado'])
    ).all()
    
    # Criar set de horas ocupadas incluindo TODA a duração do serviço
    horas_ocupadas = set()
    for agendamento in agendamentos_dia:
        # Pegar duração do serviço do agendamento
        duracao_agendamento = timedelta(minutes=agendamento.servico.duracao if agendamento.servico else 30)
        hora_inicio_agendamento = agendamento.data_hora
        hora_fim_agendamento = hora_inicio_agendamento + duracao_agendamento
        
        # Marcar TODOS os slots de 30 em 30 min durante o agendamento
        slot_atual = hora_inicio_agendamento
        while slot_atual < hora_fim_agendamento:
            horas_ocupadas.add(slot_atual)
            slot_atual += timedelta(minutes=30)  # Intervalo de 30 min
    
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
        
        # Verificar se horário já está agendado ou se conflita com algum agendamento existente
        # Precisamos verificar se o novo horário + duração do serviço não conflita
        hora_fim_novo = hora_atual + duracao
        conflito = False
        
        # Verificar se algum slot do novo agendamento está ocupado
        slot_verificacao = hora_atual
        while slot_verificacao < hora_fim_novo:
            if slot_verificacao in horas_ocupadas:
                conflito = True
                break
            slot_verificacao += timedelta(minutes=30)
        
        if not conflito:
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

def get_dias_com_barbeiros_otimizado():
    """Retorna dias da semana com barbeiros usando uma única query otimizada"""
    global _cache_dias_com_barbeiros
    
    # Usar cache se foi atualizado há menos de 1 hora
    # Usar timezone do Brasil
    tz_brasil = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(tz_brasil).replace(tzinfo=None)
    
    if _cache_dias_com_barbeiros['data'] and (agora - _cache_dias_com_barbeiros['data']).total_seconds() < 3600:
        return _cache_dias_com_barbeiros['valor']
    
    # Query otimizada: uma única query com join
    horarios = HorarioBarbeiro.query.join(Barbeiro).filter(
        Barbeiro.ativo == True,
        HorarioBarbeiro.ativo == True
    ).distinct(HorarioBarbeiro.dia_semana).all()
    
    dias_com_barbeiros = {h.dia_semana for h in horarios}
    
    # Atualizar cache
    _cache_dias_com_barbeiros = {'data': agora, 'valor': dias_com_barbeiros}
    
    return dias_com_barbeiros

@api_bp.route('/datas-disponiveis', methods=['GET'])
def listar_datas_disponiveis():
    """Retorna informações sobre disponibilidade de datas para os próximos 90 dias (otimizado)"""
    hoje = datetime.now().date()
    data_final = hoje + timedelta(days=90)
    
    # Buscar dias bloqueados com uma única query
    dias_bloqueados_query = DiaIndisponivel.query.filter(
        DiaIndisponivel.data >= hoje,
        DiaIndisponivel.data <= data_final
    ).all()
    
    datas_bloqueadas = {d.data.strftime('%Y-%m-%d') for d in dias_bloqueados_query}
    
    # Buscar horários especiais com uma única query
    horarios_especiais_query = HorarioEspecial.query.filter(
        HorarioEspecial.data >= hoje,
        HorarioEspecial.data <= data_final
    ).all()
    
    datas_especiais = {h.data.strftime('%Y-%m-%d') for h in horarios_especiais_query}
    
    # Obter dias com barbeiros (com cache)
    dias_com_barbeiros = get_dias_com_barbeiros_otimizado()
    
    # Gerar lista de datas indisponíveis de forma otimizada
    datas_indisponiveis = []
    data_atual = hoje
    
    while data_atual <= data_final:
        data_str = data_atual.strftime('%Y-%m-%d')
        
        # Verificações na ordem de performance (mais rápidas primeiro)
        if data_str in datas_bloqueadas:
            datas_indisponiveis.append(data_str)
        elif data_str in datas_especiais:
            # Horário especial sempre disponível, pula
            pass
        else:
            # Verificar dia da semana
            dia_semana = data_atual.weekday()  # 0=segunda, 6=domingo
            dia_semana_db = 0 if dia_semana == 6 else dia_semana + 1
            
            # Se não tem nenhum barbeiro neste dia da semana
            if dia_semana_db not in dias_com_barbeiros:
                datas_indisponiveis.append(data_str)
        
        data_atual += timedelta(days=1)
    
    return jsonify({
        'datas_indisponiveis': datas_indisponiveis
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
    
    # Verificar conflitos de horário considerando a DURAÇÃO COMPLETA do serviço
    # Novo agendamento: data_hora até data_hora + duração do serviço
    hora_fim_novo = data_hora + timedelta(minutes=servico.duracao)
    
    # Buscar TODOS os agendamentos do barbeiro neste dia
    agendamentos_existentes = Agendamento.query.filter(
        Agendamento.barbeiro_id == barbeiro_id,
        Agendamento.status.in_(['pendente', 'confirmado']),
        Agendamento.data_hora >= datetime.combine(data_hora.date(), time(0, 0)),
        Agendamento.data_hora <= datetime.combine(data_hora.date(), time(23, 59))
    ).all()
    
    # Verificar se o novo agendamento conflita com algum existente
    for agendamento_existente in agendamentos_existentes:
        hora_inicio_existente = agendamento_existente.data_hora
        duracao_existente = agendamento_existente.servico.duracao if agendamento_existente.servico else 30
        hora_fim_existente = hora_inicio_existente + timedelta(minutes=duracao_existente)
        
        # Conflito se:
        # 1. Novo começa durante um agendamento existente
        # 2. Novo termina durante um agendamento existente  
        # 3. Novo engloba um agendamento existente
        if (data_hora < hora_fim_existente and hora_fim_novo > hora_inicio_existente):
            return jsonify({
                'erro': 'Horário não está mais disponível. Conflita com outro agendamento.',
                'conflito': {
                    'horario_existente': hora_inicio_existente.strftime('%H:%M'),
                    'duracao_existente': duracao_existente
                }
            }), 409
    
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
        status='confirmado',
        observacoes=dados.get('observacoes', '')
    )
    
    db.session.add(agendamento)
    db.session.commit()
    
    # Verificar se o agendamento é para menos de 24 horas
    # Se sim, enviar lembrete imediatamente
    tempo_ate_agendamento = data_hora - datetime.now()
    horas_ate_agendamento = tempo_ate_agendamento.total_seconds() / 3600
    
    lembrete_enviado = False
    if horas_ate_agendamento < 24 and telefone_limpo:
        # Agendamento com menos de 24h - enviar lembrete imediatamente
        try:
            print(f"⚡ Agendamento em menos de 24h - Enviando lembrete imediato para {agendamento.nome_cliente}")
            lembrete_enviado = enviar_lembrete_whatsapp(agendamento)
            if lembrete_enviado:
                agendamento.lembrete_enviado = True
                db.session.commit()
                print(f"✅ Lembrete imediato enviado com sucesso")
            else:
                print(f"❌ Falha no envio do lembrete imediato")
        except Exception as e:
            print(f"❌ Erro ao enviar lembrete imediato: {e}")
    else:
        print(f"📅 Agendamento para mais de 24h - Lembrete será enviado automaticamente pelo scheduler")
    
    return jsonify({
        'mensagem': 'Agendamento criado com sucesso!',
        'agendamento': agendamento.to_dict(),
        'cliente': cliente.to_dict() if cliente else None,
        'lembrete_enviado': lembrete_enviado
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

@api_bp.route('/meus-agendamentos', methods=['GET'])
def meus_agendamentos():
    """Busca agendamentos por telefone e opcionalmente por nome"""
    telefone = request.args.get('telefone')
    nome = request.args.get('nome')
    
    if not telefone:
        return jsonify({'erro': 'Telefone é obrigatório'}), 400
    
    # Buscar agendamentos futuros ou recentes (últimos 7 dias)
    data_limite = datetime.now() - timedelta(days=7)
    
    # Buscar por telefone, excluindo cancelados
    query = Agendamento.query.filter(
        Agendamento.telefone == telefone,
        Agendamento.data_hora >= data_limite,
        Agendamento.status != 'cancelado'
    )
    
    # Se nome foi fornecido, filtrar também por nome (case insensitive)
    if nome:
        query = query.filter(Agendamento.nome_cliente.ilike(f'%{nome}%'))
    
    agendamentos = query.order_by(Agendamento.data_hora.asc()).all()
    
    return jsonify({
        'agendamentos': [a.to_dict() for a in agendamentos]
    })

@api_bp.route('/cancelar-agendamento/<int:id>', methods=['PUT'])
def cancelar_agendamento_cliente(id):
    """Permite cliente cancelar seu próprio agendamento"""
    agendamento = Agendamento.query.get_or_404(id)
    
    # Verificar se agendamento já passou
    if agendamento.data_hora < datetime.now():
        return jsonify({'erro': 'Não é possível cancelar agendamentos passados'}), 400
    
    # Verificar se já está cancelado
    if agendamento.status == 'cancelado':
        return jsonify({'erro': 'Este agendamento já foi cancelado'}), 400
    
    agendamento.status = 'cancelado'
    db.session.commit()
    
    return jsonify({'mensagem': 'Agendamento cancelado com sucesso'})

# ========== ROTAS ADMIN ==========

@admin_bp.route('/agendamentos', methods=['GET'])
def listar_agendamentos():
    """Lista todos os agendamentos"""
    barbeiro_id = request.args.get('barbeiro_id', type=int)
    data_str = request.args.get('data')
    status = request.args.get('status')
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    # Atualizar automaticamente agendamentos confirmados que já passaram do horário
    # Usar timezone do Brasil
    tz_brasil = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(tz_brasil).replace(tzinfo=None)
    
    agendamentos_passados = Agendamento.query.filter(
        Agendamento.status == 'confirmado',
        Agendamento.data_hora < agora
    ).all()
    
    for ag in agendamentos_passados:
        ag.status = 'concluido'
    
    if agendamentos_passados:
        db.session.commit()
    
    query = Agendamento.query
    
    if barbeiro_id:
        query = query.filter_by(barbeiro_id=barbeiro_id)
    
    if data_str:
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            inicio = datetime.combine(data, time.min)
            fim = datetime.combine(data, time.max)
            query = query.filter(Agendamento.data_hora >= inicio, Agendamento.data_hora <= fim)
        except ValueError:
            pass
    
    # Filtros de período (para dashboard)
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            inicio = datetime.combine(data_inicio, time.min)
            query = query.filter(Agendamento.data_hora >= inicio)
        except ValueError:
            pass
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            fim = datetime.combine(data_fim, time.max)
            query = query.filter(Agendamento.data_hora <= fim)
        except ValueError:
            pass
    
    if status:
        query = query.filter_by(status=status)
    
    # Eager loading para evitar N+1 queries (otimização de performance)
    agendamentos = query.options(
        joinedload(Agendamento.barbeiro),
        joinedload(Agendamento.servico),
        joinedload(Agendamento.cliente)
    ).order_by(Agendamento.data_hora.desc()).all()
    
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

@admin_bp.route('/estatisticas-barbeiros', methods=['GET'])
def get_estatisticas_barbeiros():
    """Retorna estatísticas de atendimentos por barbeiro e serviço em um período"""
    from sqlalchemy import func
    
    # Obter parâmetros de data e barbeiro
    barbeiro_id = request.args.get('barbeiro_id', type=int)
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    # Query base
    query = db.session.query(
        Barbeiro.nome.label('barbeiro_nome'),
        Servico.nome.label('servico_nome'),
        func.count(Agendamento.id).label('quantidade')
    ).join(
        Agendamento, Agendamento.barbeiro_id == Barbeiro.id
    ).join(
        Servico, Agendamento.servico_id == Servico.id
    ).filter(
        Agendamento.status.in_(['confirmado', 'concluido'])
    )
    
    # Aplicar filtro de barbeiro se fornecido
    if barbeiro_id:
        query = query.filter(Barbeiro.id == barbeiro_id)
    
    # Aplicar filtros de data se fornecidos
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            inicio_dia = datetime.combine(data_inicio, time.min)
            query = query.filter(Agendamento.data_hora >= inicio_dia)
        except ValueError:
            pass
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            fim_dia = datetime.combine(data_fim, time.max)
            query = query.filter(Agendamento.data_hora <= fim_dia)
        except ValueError:
            pass
    
    # Agrupar por barbeiro e serviço
    resultados = query.group_by(
        Barbeiro.nome, Servico.nome
    ).order_by(
        Barbeiro.nome, func.count(Agendamento.id).desc()
    ).all()
    
    # Formatar resultados
    estatisticas = []
    for resultado in resultados:
        estatisticas.append({
            'barbeiro_nome': resultado.barbeiro_nome,
            'servico_nome': resultado.servico_nome,
            'quantidade': resultado.quantidade
        })
    
    return jsonify({
        'estatisticas': estatisticas
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
    
    barbeiro_id = dados.get('barbeiro_id')
    
    # Verificar se já existe para esta data e barbeiro
    query = HorarioEspecial.query.filter_by(data=data)
    if barbeiro_id:
        query = query.filter_by(barbeiro_id=barbeiro_id)
    else:
        query = query.filter_by(barbeiro_id=None)
    
    existente = query.first()
    if existente:
        return jsonify({'erro': 'Já existe horário especial para esta data e barbeiro'}), 409
    
    horario = HorarioEspecial(
        data=data,
        barbeiro_id=barbeiro_id if barbeiro_id else None,
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
    """Lista barbeiros ativos e disponíveis para uma data específica"""
    try:
        data_str = request.args.get('data')
        
        # Se não tiver data, retorna todos os barbeiros ativos com eager loading
        if not data_str:
            barbeiros = Barbeiro.query.options(joinedload(Barbeiro.servicos))\
                .filter_by(ativo=True)\
                .order_by(Barbeiro.ordem)\
                .all()
            return jsonify({
                'barbeiros': [b.to_dict() for b in barbeiros]
            })
        
        # Converter string para objeto date
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            print(f"❌ Formato de data inválido: {data_str}")
            return jsonify({'erro': 'Formato de data inválido'}), 400
        
        # Verificar se a data está disponível (não está bloqueada)
        dia_indisponivel = DiaIndisponivel.query.filter_by(data=data).first()
        if dia_indisponivel:
            # Data bloqueada - sem barbeiros disponíveis
            return jsonify({'barbeiros': []})
        
        # Buscar todos os barbeiros ativos com eager loading
        barbeiros = Barbeiro.query.options(joinedload(Barbeiro.servicos))\
            .filter_by(ativo=True)\
            .order_by(Barbeiro.ordem)\
            .all()
        
        # Filtrar barbeiros que trabalham neste dia da semana
        # Python weekday: 0=segunda, 1=terça, ..., 6=domingo
        # Banco de dados: 0=domingo, 1=segunda, ..., 6=sábado
        dia_semana_python = data.weekday()  # 0=segunda-feira, 6=domingo
        
        # Converter para formato do banco (0=domingo, 1=segunda, ..., 6=sábado)
        if dia_semana_python == 6:  # domingo
            dia_semana_db = 0
        else:
            dia_semana_db = dia_semana_python + 1
        
        print(f"🔍 Buscando barbeiros para {data_str} (dia da semana DB: {dia_semana_db})")
        
        # Pré-carregar TODOS os horários especiais e normais com uma única query (otimizado)
        horarios_especiais = HorarioEspecial.query.filter(
            HorarioEspecial.data == data
        ).all()
        
        horarios_barbeiros = HorarioBarbeiro.query.filter(
            HorarioBarbeiro.dia_semana == dia_semana_db,
            HorarioBarbeiro.ativo == True
        ).all()
        
        print(f"   Horários encontrados: {len(horarios_barbeiros)}")
        
        # Criar dicts para busca O(1)
        especiais_por_barbeiro = {h.barbeiro_id: h for h in horarios_especiais if h.barbeiro_id}
        especial_geral = next((h for h in horarios_especiais if h.barbeiro_id is None), None)
        horarios_dict = {h.barbeiro_id: h for h in horarios_barbeiros}
        
        barbeiros_disponiveis = []
        
        for barbeiro in barbeiros:
            # Verificações rápidas (dicts/set lookups)
            if barbeiro.id in especiais_por_barbeiro:
                # Barbeiro tem horário especial - está disponível
                barbeiros_disponiveis.append(barbeiro)
            elif especial_geral:
                # Tem horário especial geral - barbeiro está disponível
                barbeiros_disponiveis.append(barbeiro)
            elif barbeiro.id in horarios_dict:
                # Barbeiro trabalha neste dia
                barbeiros_disponiveis.append(barbeiro)
        
        print(f"   Barbeiros disponíveis: {len(barbeiros_disponiveis)}")
        
        # Se não encontrou nenhum barbeiro, logar para debug
        if not barbeiros_disponiveis:
            print(f"⚠️ Nenhum barbeiro disponível para {data_str}")
            print(f"   Total de barbeiros ativos: {len(barbeiros)}")
            print(f"   Horários cadastrados para dia {dia_semana_db}: {len(horarios_barbeiros)}")
            for h in horarios_barbeiros:
                print(f"      - Barbeiro ID {h.barbeiro_id}: {h.horario_inicio}-{h.horario_fim}")
        
        return jsonify({
            'barbeiros': [b.to_dict() for b in barbeiros_disponiveis]
        })
        
    except Exception as e:
        print(f"❌ ERRO ao listar barbeiros: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500

@api_bp.route('/barbeiro/<int:barbeiro_id>/horarios', methods=['GET'])
def get_horarios_barbeiro(barbeiro_id):
    """Retorna horários de um barbeiro (com cache)"""
    barbeiro = Barbeiro.query.get(barbeiro_id)
    if not barbeiro:
        return jsonify({'erro': 'Barbeiro não encontrado'}), 404
    
    # Uma única query otimizada
    horarios = HorarioBarbeiro.query.filter_by(
        barbeiro_id=barbeiro_id,
        ativo=True
    ).order_by(HorarioBarbeiro.dia_semana).all()
    
    # Mapear dias da semana para nomes
    dias_nomes = {
        0: 'Domingo',
        1: 'Segunda',
        2: 'Terça',
        3: 'Quarta',
        4: 'Quinta',
        5: 'Sexta',
        6: 'Sábado'
    }
    
    horarios_dict = {}
    for h in horarios:
        dia_nome = dias_nomes[h.dia_semana]
        horarios_dict[dia_nome] = {
            'inicio': h.horario_inicio,
            'fim': h.horario_fim,
            'almoco_inicio': h.intervalo_almoco_inicio,
            'almoco_fim': h.intervalo_almoco_fim
        }
    
    return jsonify({
        'barbeiro_id': barbeiro_id,
        'barbeiro_nome': barbeiro.nome,
        'horarios': horarios_dict
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

@admin_bp.route('/upload-foto-barbeiro', methods=['POST'])
def upload_foto_barbeiro():
    """Faz upload da foto do barbeiro"""
    if 'foto' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['foto']
    
    if file.filename == '':
        return jsonify({'erro': 'Nenhum arquivo selecionado'}), 400
    
    # Verificar extensão permitida
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    if not allowed_file(file.filename):
        return jsonify({'erro': 'Formato de arquivo não permitido'}), 400
    
    # Criar nome seguro com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    new_filename = f"barbeiro_{timestamp}{ext}"
    
    # Criar diretório se não existir
    upload_folder = os.path.join('static', 'img', 'barbeiros')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Salvar arquivo
    filepath = os.path.join(upload_folder, new_filename)
    file.save(filepath)
    
    # Retornar URL relativa
    foto_url = f"/static/img/barbeiros/{new_filename}"
    
    return jsonify({
        'mensagem': 'Upload realizado com sucesso',
        'foto_url': foto_url
    }), 200

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

@admin_bp.route('/horarios-barbeiro/<int:barbeiro_id>', methods=['GET'])
def get_horarios_barbeiro(barbeiro_id):
    """Retorna horários de um barbeiro"""
    barbeiro = Barbeiro.query.get(barbeiro_id)
    if not barbeiro:
        return jsonify({'erro': 'Barbeiro não encontrado'}), 404
    
    horarios = HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro_id).all()
    
    return jsonify({
        'barbeiro': barbeiro.to_dict(),
        'horarios': [h.to_dict() for h in horarios]
    })

@admin_bp.route('/horarios-barbeiro/<int:barbeiro_id>', methods=['POST'])
def salvar_horarios_barbeiro(barbeiro_id):
    """Salva/atualiza horários de um barbeiro"""
    barbeiro = Barbeiro.query.get(barbeiro_id)
    if not barbeiro:
        return jsonify({'erro': 'Barbeiro não encontrado'}), 404
    
    dados = request.get_json()
    horarios_novos = dados.get('horarios', [])
    
    # Deletar horários antigos
    HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro_id).delete()
    
    # Adicionar novos horários
    for h in horarios_novos:
        horario = HorarioBarbeiro(
            barbeiro_id=barbeiro_id,
            dia_semana=h['dia_semana'],
            horario_inicio=h['horario_inicio'],
            horario_fim=h['horario_fim'],
            intervalo_almoco_inicio=h.get('intervalo_almoco_inicio'),
            intervalo_almoco_fim=h.get('intervalo_almoco_fim'),
            ativo=True
        )
        db.session.add(horario)
    
    db.session.commit()
    
    return jsonify({'mensagem': 'Horários salvos com sucesso'})

# ===== ROTAS DE DIAS INDISPONÍVEIS (FECHADOS) =====

@admin_bp.route('/dias-indisponiveis', methods=['GET'])
def listar_dias_indisponiveis():
    """Lista todos os dias indisponíveis"""
    dias = DiaIndisponivel.query.order_by(DiaIndisponivel.data).all()
    return jsonify({
        'dias_indisponiveis': [d.to_dict() for d in dias]
    })

@admin_bp.route('/dias-indisponiveis', methods=['POST'])
def criar_dia_indisponivel():
    """Marca um dia como fechado"""
    dados = request.get_json()
    
    if not dados.get('data'):
        return jsonify({'erro': 'Data é obrigatória'}), 400
    
    try:
        data = datetime.strptime(dados['data'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'erro': 'Formato de data inválido'}), 400
    
    # Verificar se já existe
    existente = DiaIndisponivel.query.filter_by(data=data).first()
    if existente:
        return jsonify({'erro': 'Este dia já está marcado como fechado'}), 409
    
    dia = DiaIndisponivel(
        data=data,
        motivo=dados.get('motivo', 'Fechado')
    )
    
    db.session.add(dia)
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Dia marcado como fechado',
        'dia': dia.to_dict()
    }), 201

@admin_bp.route('/dias-indisponiveis/<int:id>', methods=['DELETE'])
def deletar_dia_indisponivel(id):
    """Remove um dia fechado"""
    dia = DiaIndisponivel.query.get(id)
    if not dia:
        return jsonify({'erro': 'Dia não encontrado'}), 404
    
    db.session.delete(dia)
    db.session.commit()
    
    return jsonify({'mensagem': 'Dia removido'})

