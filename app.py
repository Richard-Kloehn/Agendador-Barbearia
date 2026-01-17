from flask import Flask, render_template, session, redirect, url_for, request
from flask_cors import CORS
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

# Inicializar banco
from database import db
db.init_app(app)
CORS(app)

# Importar models e routes
from models import Agendamento, ConfiguracaoBarbearia
from routes import api_bp, admin_bp

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Configuração do scheduler para envio de lembretes
scheduler = BackgroundScheduler()

def enviar_lembretes():
    """Envia lembretes 24 horas antes dos agendamentos"""
    from services.whatsapp_service import enviar_lembrete_whatsapp
    
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
    
    for agendamento in agendamentos:
        try:
            enviar_lembrete_whatsapp(agendamento)
            agendamento.lembrete_enviado = True
            db.session.commit()
        except Exception as e:
            print(f"Erro ao enviar lembrete para {agendamento.nome_cliente}: {e}")

# Agendar verificação a cada hora
scheduler.add_job(func=enviar_lembretes, trigger="interval", hours=1)
scheduler.start()

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
        from models import Barbeiro, Servico
        
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
        
        db.session.commit()
        print("✅ Banco de dados inicializado com barbeiros e serviços!")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
