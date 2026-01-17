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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Criar configuração padrão se não existir
        if not ConfiguracaoBarbearia.query.first():
            config = ConfiguracaoBarbearia(
                nome_barbearia="Navalha's Barber Club",
                horario_abertura="09:00",
                horario_fechamento="19:00",
                duracao_atendimento=30,
                intervalo_almoco_inicio="12:00",
                intervalo_almoco_fim="13:00"
            )
            db.session.add(config)
            db.session.commit()
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
