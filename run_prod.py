"""
Script para rodar o servidor em modo de produção (sem auto-reload)
Isso evita que o WhatsApp seja interrompido durante o envio
"""
import os
from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    # Debug mode desligado para evitar reloads durante envio de WhatsApp
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
