from flask import Flask, render_template, session, redirect, url_for, request
from flask_cors import CORS
from flask_compress import Compress
try:
    from flask_wtf.csrf import CSRFProtect
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    SEGURANCA_ATIVA = True
except ImportError:
    SEGURANCA_ATIVA = False
    print("⚠️ Módulos de segurança não instalados. Execute: pip install flask-wtf flask-limiter")
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Corrigir DATABASE_URL do Render (postgres:// -> postgresql://)
database_url = os.getenv('DATABASE_URL', 'sqlite:///barbearia.db')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', '123')  # Senha via env
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Token CSRF não expira

# Configurações de política de cancelamento
app.config['PRAZO_MINIMO_CANCELAMENTO_HORAS'] = int(os.getenv('PRAZO_MINIMO_CANCELAMENTO_HORAS', '2'))
app.config['PRAZO_MINIMO_REAGENDAMENTO_HORAS'] = int(os.getenv('PRAZO_MINIMO_REAGENDAMENTO_HORAS', '2'))

# Otimizações para produção
if database_url and 'postgresql' in database_url:
    # Pool de conexões otimizado para PostgreSQL + SSL
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 5,  # Reduzido para plano grátis
        'pool_recycle': 1800,  # 30 minutos
        'pool_pre_ping': True,  # Testa conexão antes de usar
        'max_overflow': 2,  # Reduzido para plano grátis
        'connect_args': {
            'sslmode': 'require',  # Força SSL
            'connect_timeout': 10  # Timeout de 10 segundos
        }
    }

# Inicializar banco
from database import db
db.init_app(app)
CORS(app)

# Proteção CSRF (se disponível)
if SEGURANCA_ATIVA:
    csrf = CSRFProtect(app)
    print("✅ Proteção CSRF ativada")
    
    # Rate Limiting (proteção contra spam/abuso)
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    print("✅ Rate Limiting ativado")
else:
    print("⚠️ Segurança básica - instale flask-wtf e flask-limiter para proteção completa")

# Criar índices automaticamente na primeira execução (produção)
def criar_indices_se_necessario():
    """Cria índices no banco de dados se ainda não existirem"""
    if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
        try:
            from sqlalchemy import text
            with app.app_context():
                # Verificar se índices já existem
                resultado = db.session.execute(text(
                    "SELECT indexname FROM pg_indexes WHERE tablename = 'agendamento'"
                )).fetchall()
                
                indices_existentes = [r[0] for r in resultado]
                
                if 'idx_agendamento_data_hora' not in indices_existentes:
                    print("📊 Criando índices de performance...")
                    
                    # Criar todos os índices
                    db.session.execute(text(
                        "CREATE INDEX IF NOT EXISTS idx_agendamento_data_hora ON agendamento(data_hora)"
                    ))
                    db.session.execute(text(
                        "CREATE INDEX IF NOT EXISTS idx_agendamento_barbeiro ON agendamento(barbeiro_id)"
                    ))
                    db.session.execute(text(
                        "CREATE INDEX IF NOT EXISTS idx_agendamento_status ON agendamento(status)"
                    ))
                    db.session.execute(text(
                        "CREATE INDEX IF NOT EXISTS idx_cliente_telefone ON cliente(telefone)"
                    ))
                    db.session.execute(text(
                        "CREATE INDEX IF NOT EXISTS idx_agendamento_data_status ON agendamento(data_hora, status)"
                    ))
                    
                    db.session.commit()
                    print("✅ Índices criados com sucesso!")
                else:
                    print("✅ Índices já existem")
        except Exception as e:
            print(f"⚠️ Erro ao criar índices: {e}")
            
# Criar índices ao iniciar
criar_indices_se_necessario()

# Compressão gzip para reduzir tamanho das respostas
Compress(app)

# Headers de cache para melhor performance
@app.after_request
def set_cache_headers(response):
    # Cache estático (CSS, JS, imagens) por 7 dias
    if response.content_type and any(x in response.content_type for x in ['text/css', 'application/javascript', 'image/', 'font/']):
        response.cache_control.max_age = 604800  # 7 dias
        response.cache_control.public = True
    # HTML: cache por 1 hora
    elif response.content_type and 'text/html' in response.content_type:
        response.cache_control.max_age = 3600
        response.cache_control.public = True
    return response

# Importar models e routes
from models import Agendamento, ConfiguracaoBarbearia
from routes import api_bp, admin_bp
from debug_routes import debug_bp

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(debug_bp, url_prefix='/debug')

# Configuração do scheduler para envio de lembretes
scheduler = BackgroundScheduler()

def enviar_lembretes():
    """Envia lembretes 24 horas antes dos agendamentos via Evolution API"""
    from services.whapi_service import enviar_lembrete_whatsapp
    
    with app.app_context():
        amanha = datetime.now() + timedelta(days=1)
        inicio_dia = amanha.replace(hour=0, minute=0, second=0, microsecond=0)
        fim_dia = amanha.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        agendamentos = Agendamento.query.filter(
            Agendamento.data_hora >= inicio_dia,
            Agendamento.data_hora <= fim_dia,
            Agendamento.lembrete_enviado == False,
            Agendamento.status == 'confirmado',
            Agendamento.telefone != ''  # Apenas agendamentos com telefone
        ).all()
        
        print(f"🔍 Verificando lembretes: {len(agendamentos)} agendamentos encontrados para amanhã")
        
        for agendamento in agendamentos:
            try:
                print(f"📤 Enviando lembrete para {agendamento.nome_cliente}...")
                sucesso = enviar_lembrete_whatsapp(agendamento)
                
                if sucesso:
                    agendamento.lembrete_enviado = True
                    db.session.commit()
                    print(f"✅ Lembrete enviado para {agendamento.nome_cliente}")
                else:
                    print(f"❌ Falha ao enviar lembrete para {agendamento.nome_cliente}")
                    
            except Exception as e:
                print(f"❌ Erro ao enviar lembrete para {agendamento.nome_cliente}: {e}")

# Agendar verificação a cada hora
scheduler.add_job(func=enviar_lembretes, trigger="interval", hours=1)
scheduler.start()
print("✅ Scheduler de lembretes iniciado (verifica a cada 1 hora)")

# Função para popular horários automaticamente
def inicializar_dados_basicos():
    """Popula barbeiros, serviços e horários automaticamente na primeira execução"""
    with app.app_context():
        from models import Barbeiro, Servico, HorarioBarbeiro
        
        print("="*60)
        print("🔍 VERIFICANDO DADOS NO BANCO...")
        print("="*60)
        
        # Contar registros existentes
        total_barbeiros = Barbeiro.query.count()
        total_servicos = Servico.query.count()
        total_horarios = HorarioBarbeiro.query.count()
        
        print(f"📊 Barbeiros: {total_barbeiros}")
        print(f"📊 Serviços: {total_servicos}")
        print(f"📊 Horários: {total_horarios}")
        
        # 1. CRIAR BARBEIROS
        if total_barbeiros == 0:
            print("\n📋 Criando barbeiros...")
            barbeiros_data = [
                {'nome': 'Bryan Victor Felippi', 'foto_url': '/static/img/barbeiro1.jpg', 'ordem': 1},
                {'nome': 'Fabricio', 'foto_url': '/static/img/barbeiro2.jpg', 'ordem': 2},
                {'nome': 'Felipe Soares Santana', 'foto_url': '/static/img/barbeiro3.jpg', 'ordem': 3}
            ]
            
            for b_data in barbeiros_data:
                barbeiro = Barbeiro(
                    nome=b_data['nome'],
                    foto_url=b_data['foto_url'],
                    ativo=True,
                    ordem=b_data['ordem']
                )
                db.session.add(barbeiro)
            
            db.session.commit()
            print(f"✅ {len(barbeiros_data)} barbeiros criados!")
        else:
            print(f"\n✅ Barbeiros já existem ({total_barbeiros})")
        
        # 2. CRIAR SERVIÇOS
        if total_servicos == 0:
            print("\n✂️ Criando serviços...")
            servicos_data = [
                {'nome': 'Corte de Cabelo', 'duracao': 30, 'preco': 45.00, 'ordem': 1},
                {'nome': 'Barba', 'duracao': 20, 'preco': 30.00, 'ordem': 2},
                {'nome': 'Corte + Barba', 'duracao': 45, 'preco': 70.00, 'ordem': 3},
                {'nome': 'Pezinho', 'duracao': 15, 'preco': 20.00, 'ordem': 4}
            ]
            
            for s_data in servicos_data:
                servico = Servico(
                    nome=s_data['nome'],
                    descricao=f"{s_data['nome']} profissional",
                    duracao=s_data['duracao'],
                    preco=s_data['preco'],
                    ativo=True,
                    ordem=s_data['ordem']
                )
                db.session.add(servico)
            
            db.session.commit()
            print(f"✅ {len(servicos_data)} serviços criados!")
            
            # Associar todos os serviços a todos os barbeiros
            barbeiros = Barbeiro.query.all()
            servicos = Servico.query.all()
            for barbeiro in barbeiros:
                barbeiro.servicos = servicos
            db.session.commit()
            print("✅ Serviços associados aos barbeiros!")
        else:
            print(f"\n✅ Serviços já existem ({total_servicos})")
        
        # 3. CRIAR HORÁRIOS (sempre que tiver barbeiros sem horários)
        barbeiros = Barbeiro.query.all()
        
        if not barbeiros:
            print("\n⚠️ Nenhum barbeiro cadastrado para criar horários")
        else:
            # Horários padrão esperados
            horarios_padrao = [
                {'dia_semana': 1, 'horario_inicio': '09:00', 'horario_fim': '18:00', 
                 'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
                {'dia_semana': 2, 'horario_inicio': '09:00', 'horario_fim': '18:00',
                 'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
                {'dia_semana': 3, 'horario_inicio': '09:00', 'horario_fim': '18:00',
                 'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
                {'dia_semana': 4, 'horario_inicio': '09:00', 'horario_fim': '18:00',
                 'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
                {'dia_semana': 5, 'horario_inicio': '09:00', 'horario_fim': '18:00',
                 'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
                {'dia_semana': 6, 'horario_inicio': '09:00', 'horario_fim': '17:00',
                 'intervalo_almoco_inicio': None, 'intervalo_almoco_fim': None}
            ]
            
            # Verificar horários faltantes para cada barbeiro
            total_criados = 0
            for barbeiro in barbeiros:
                # Buscar quais dias já têm horários
                horarios_existentes = HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro.id).all()
                dias_existentes = {h.dia_semana for h in horarios_existentes}
                
                # Criar apenas os horários faltantes
                horarios_faltantes = [h for h in horarios_padrao if h['dia_semana'] not in dias_existentes]
                
                if horarios_faltantes:
                    print(f"\n   Criando {len(horarios_faltantes)} horário(s) faltante(s) para: {barbeiro.nome}")
                    for horario_data in horarios_faltantes:
                        horario = HorarioBarbeiro(
                            barbeiro_id=barbeiro.id,
                            dia_semana=horario_data['dia_semana'],
                            horario_inicio=horario_data['horario_inicio'],
                            horario_fim=horario_data['horario_fim'],
                            intervalo_almoco_inicio=horario_data['intervalo_almoco_inicio'],
                            intervalo_almoco_fim=horario_data['intervalo_almoco_fim'],
                            ativo=True
                        )
                        db.session.add(horario)
                        total_criados += 1
            
            if total_criados > 0:
                db.session.commit()
                print(f"\n✅ {total_criados} horário(s) criado(s)!")
            else:
                print(f"\n✅ Todos os barbeiros já têm horários completos ({total_horarios} total)")
        
        print("="*60)
        print("✅ Verificação completa!")
        print("="*60)

# Inicializar dados na primeira execução
try:
    inicializar_dados_basicos()
except Exception as e:
    print(f"❌ Erro ao inicializar dados: {e}")
    import traceback
    traceback.print_exc()

# Corrigir horários se necessário (importante para produção)
try:
    from corrigir_horarios_producao import corrigir_horarios_producao
    corrigir_horarios_producao()
except Exception as e:
    print(f"⚠️ Aviso ao corrigir horários: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        senha = request.form.get('senha')
        if senha == app.config['ADMIN_PASSWORD']:
            session['admin_logado'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', erro='Senha incorreta')
    return render_template('login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logado', None)
    return redirect(url_for('index'))

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logado'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/confirmar/<token>')
def confirmar_agendamento(token):
    """Página de confirmação via WhatsApp"""
    agendamento = Agendamento.query.filter_by(token_confirmacao=token).first()
    if agendamento:
        return render_template('confirmar.html', agendamento=agendamento)
    return "Link inválido ou expirado", 404

# Inicializar banco de dados na primeira execução
with app.app_context():
    db.create_all()
    
    # Criar configuração padrão se não existir
    if not ConfiguracaoBarbearia.query.first():
        from models import Barbeiro, Servico, HorarioBarbeiro
        
        config = ConfiguracaoBarbearia(
            nome_barbearia="Navalha's Barber Club",
            horario_abertura="09:00",
            horario_fechamento="19:00",
            duracao_atendimento=30,
            intervalo_almoco_inicio="12:00",
            intervalo_almoco_fim="13:00"
        )
        db.session.add(config)
        
        # Criar barbeiros iniciais
        barbeiro1 = Barbeiro(nome="Bryan Victor Felippi", foto_url="https://via.placeholder.com/150", ativo=True, ordem=1)
        barbeiro2 = Barbeiro(nome="Fabricio", foto_url="https://via.placeholder.com/150", ativo=True, ordem=2)
        barbeiro3 = Barbeiro(nome="Felipe Soares Santana", foto_url="https://via.placeholder.com/150", ativo=True, ordem=3)
        
        db.session.add_all([barbeiro1, barbeiro2, barbeiro3])
        db.session.flush()
        
        # Criar serviços iniciais
        servico1 = Servico(nome="Corte", descricao="Corte de cabelo masculino", duracao=30, preco=45.00, ativo=True)
        servico2 = Servico(nome="Barba", descricao="Barba completa", duracao=30, preco=45.00, ativo=True)
        servico3 = Servico(nome="Combo Corte + Barba", descricao="Corte e barba", duracao=45, preco=95.00, ativo=True)
        servico4 = Servico(nome="Sobrancelha", descricao="Design de sobrancelha", duracao=15, preco=25.00, ativo=True)
        servico5 = Servico(nome="Pézinho", descricao="Acabamento do pescoço", duracao=15, preco=20.00, ativo=True)
        
        db.session.add_all([servico1, servico2, servico3, servico4, servico5])
        db.session.flush()
        
        # Associar todos os serviços a todos os barbeiros
        for barbeiro in [barbeiro1, barbeiro2, barbeiro3]:
            barbeiro.servicos.extend([servico1, servico2, servico3, servico4, servico5])
        
        # Criar horários padrão para os barbeiros (Segunda a Sábado)
        for barbeiro in [barbeiro1, barbeiro2, barbeiro3]:
            for dia in range(1, 7):  # 1=Segunda até 6=Sábado
                horario = HorarioBarbeiro(
                    barbeiro_id=barbeiro.id,
                    dia_semana=dia,
                    horario_inicio=config.horario_abertura,
                    horario_fim=config.horario_fechamento,
                    intervalo_almoco_inicio=config.intervalo_almoco_inicio,
                    intervalo_almoco_fim=config.intervalo_almoco_fim,
                    ativo=True
                )
                db.session.add(horario)
        
        db.session.commit()
        print("✅ Banco de dados inicializado com barbeiros, serviços e horários!")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
