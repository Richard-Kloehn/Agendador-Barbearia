from flask import Flask, render_template, session, redirect, url_for, request
from flask_cors import CORS
from flask_compress import Compress
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///barbearia.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['ADMIN_PASSWORD'] = '123'  # Senha do admin

# Otimizações para produção
if os.getenv('DATABASE_URL') and 'postgresql' in os.getenv('DATABASE_URL', ''):
    # Pool de conexões otimizado para PostgreSQL
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 5
    }

# Inicializar banco
from database import db
db.init_app(app)
CORS(app)

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

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Configuração do scheduler para envio de lembretes
scheduler = BackgroundScheduler()

def enviar_lembretes():
    """Envia lembretes 24 horas antes dos agendamentos via whapi.cloud"""
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
        
        # 1. CRIAR BARBEIROS
        if Barbeiro.query.count() == 0:
            print("📋 Criando barbeiros...")
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
        
        # 2. CRIAR SERVIÇOS
        if Servico.query.count() == 0:
            print("✂️ Criando serviços...")
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
        
        # 3. CRIAR HORÁRIOS
        if HorarioBarbeiro.query.count() == 0:
            barbeiros = Barbeiro.query.all()
            
            if not barbeiros:
                print("⚠️ Nenhum barbeiro cadastrado para criar horários")
                return
            
            print(f"🕐 Criando horários para {len(barbeiros)} barbeiro(s)...")
            
            # Horários padrão
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
            
            for barbeiro in barbeiros:
                for horario_data in horarios_padrao:
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
            
            db.session.commit()
            print(f"✅ {len(barbeiros) * len(horarios_padrao)} horários criados!")
        
        print("✅ Inicialização completa!")

# Inicializar dados na primeira execução
inicializar_dados_basicos()

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
