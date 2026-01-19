"""
Servidor API de WhatsApp - Para rodar em VPS
=============================================
Este servidor recebe requisições HTTP e envia mensagens WhatsApp
usando automação Selenium.

INSTALAR NO VPS:
1. pip install flask flask-cors
2. Já tem selenium, webdriver-manager instalados
3. python whatsapp_api_server.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from services.whatsapp_service_automation import WhatsAppService
import logging

app = Flask(__name__)
CORS(app)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Token de segurança (defina uma senha forte)
API_TOKEN = os.getenv('WHATSAPP_API_TOKEN', 'sua-senha-secreta-aqui-mude-isso')

# Instância única do serviço WhatsApp
whatsapp_service = None

def verificar_token():
    """Verifica se o token de autorização é válido"""
    token = request.headers.get('Authorization')
    if not token or token != f'Bearer {API_TOKEN}':
        return False
    return True

@app.route('/health', methods=['GET'])
def health_check():
    """Verifica se o servidor está funcionando"""
    return jsonify({
        'status': 'online',
        'whatsapp_ativo': whatsapp_service is not None and whatsapp_service.driver is not None
    })

@app.route('/iniciar', methods=['POST'])
def iniciar_whatsapp():
    """Inicia o navegador WhatsApp (primeira vez ou após reiniciar)"""
    if not verificar_token():
        return jsonify({'erro': 'Token inválido'}), 401
    
    global whatsapp_service
    
    try:
        if whatsapp_service is None:
            whatsapp_service = WhatsAppService()
        
        if not whatsapp_service.iniciar_navegador():
            return jsonify({'erro': 'Falha ao iniciar navegador'}), 500
        
        if not whatsapp_service.abrir_whatsapp_web():
            return jsonify({'erro': 'Falha ao abrir WhatsApp Web'}), 500
        
        logger.info("✅ WhatsApp iniciado com sucesso!")
        return jsonify({'mensagem': 'WhatsApp iniciado com sucesso'})
    
    except Exception as e:
        logger.error(f"Erro ao iniciar WhatsApp: {e}")
        return jsonify({'erro': str(e)}), 500

@app.route('/enviar', methods=['POST'])
def enviar_mensagem():
    """Envia uma mensagem WhatsApp"""
    if not verificar_token():
        return jsonify({'erro': 'Token inválido'}), 401
    
    dados = request.get_json()
    numero = dados.get('numero')
    mensagem = dados.get('mensagem')
    
    if not numero or not mensagem:
        return jsonify({'erro': 'Número e mensagem são obrigatórios'}), 400
    
    global whatsapp_service
    
    # Verificar se WhatsApp está iniciado
    if whatsapp_service is None or whatsapp_service.driver is None:
        return jsonify({'erro': 'WhatsApp não está iniciado. Execute /iniciar primeiro'}), 503
    
    try:
        sucesso = whatsapp_service.enviar_mensagem(numero, mensagem)
        
        if sucesso:
            logger.info(f"✅ Mensagem enviada para {numero}")
            return jsonify({'mensagem': 'Mensagem enviada com sucesso'})
        else:
            logger.error(f"❌ Falha ao enviar mensagem para {numero}")
            return jsonify({'erro': 'Falha ao enviar mensagem'}), 500
    
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        return jsonify({'erro': str(e)}), 500

@app.route('/enviar-lote', methods=['POST'])
def enviar_lote():
    """Envia múltiplas mensagens em lote"""
    if not verificar_token():
        return jsonify({'erro': 'Token inválido'}), 401
    
    dados = request.get_json()
    mensagens = dados.get('mensagens', [])
    
    if not mensagens:
        return jsonify({'erro': 'Lista de mensagens vazia'}), 400
    
    global whatsapp_service
    
    if whatsapp_service is None or whatsapp_service.driver is None:
        return jsonify({'erro': 'WhatsApp não está iniciado'}), 503
    
    resultados = []
    
    for msg in mensagens:
        numero = msg.get('numero')
        mensagem = msg.get('mensagem')
        
        if not numero or not mensagem:
            resultados.append({'numero': numero, 'sucesso': False, 'erro': 'Dados incompletos'})
            continue
        
        try:
            sucesso = whatsapp_service.enviar_mensagem(numero, mensagem)
            resultados.append({
                'numero': numero,
                'sucesso': sucesso,
                'erro': None if sucesso else 'Falha ao enviar'
            })
        except Exception as e:
            resultados.append({'numero': numero, 'sucesso': False, 'erro': str(e)})
    
    enviados = sum(1 for r in resultados if r['sucesso'])
    
    return jsonify({
        'total': len(mensagens),
        'enviados': enviados,
        'falhados': len(mensagens) - enviados,
        'resultados': resultados
    })

@app.route('/parar', methods=['POST'])
def parar_whatsapp():
    """Para o navegador WhatsApp"""
    if not verificar_token():
        return jsonify({'erro': 'Token inválido'}), 401
    
    global whatsapp_service
    
    try:
        if whatsapp_service and whatsapp_service.driver:
            whatsapp_service.fechar()
            logger.info("WhatsApp fechado")
        
        return jsonify({'mensagem': 'WhatsApp parado com sucesso'})
    
    except Exception as e:
        logger.error(f"Erro ao parar WhatsApp: {e}")
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    
    print("\n" + "="*60)
    print("🚀 SERVIDOR API DE WHATSAPP")
    print("="*60)
    print(f"\n📡 Rodando em: http://localhost:{port}")
    print(f"🔐 Token: {API_TOKEN}")
    print("\n⚠️  IMPORTANTE:")
    print("   1. Execute /iniciar primeiro (POST)")
    print("   2. Escaneie QR Code na primeira vez")
    print("   3. Use /enviar para enviar mensagens")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
