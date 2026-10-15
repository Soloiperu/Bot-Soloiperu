from flask import Flask, request
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

PAGE_TOKEN = os.environ.get('PAGE_TOKEN', '')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'soloiperu123')

MENSAJES = {
    'bienvenida': '''Hola 👋 Soy el asistente de Soloiperu - Tanques de Agua en Ica.

¿En qué tanque estás interesado?
Escribe:
- 1100L
- 2500L
- PRECIO
- UBICACION''',
    'precios': '''💧 LISTA DE PRECIOS SOLOIPERU - ICA:

✅ Tanque 1100L Eternit / Rotoplas: Desde S/ 550
✅ Tanque 2500L: Desde S/ 1,250
✅ Tanque 5000L: Desde S/ 2,800

Incluye tapa y accesorios.
Delivery GRATIS en Ica centro.

¿Quieres que te mande fotos? Escribe FOTOS
¿Quieres hablar con un asesor? Escribe ASESOR''',
    'ubicacion': '''📍 ESTAMOS EN ICA:

Local 1: Av. Principal - Ica (Frente a Sodimac)
Local 2: Carretera Panamericana Sur

📲 WhatsApp directo: 942 418 535
https://wa.me/51942418535

Atendemos de Lunes a Sabado 8am a 6pm. Delivery hoy mismo!''',
    'fotos': '''Claro, aquí tienes los modelos mas vendidos 👇

Te mando al WhatsApp con fotos y video para que veas la calidad.

Escribe ASESOR y te atiende Dario directamente al 942 418 535''',
    'asesor': '''Perfecto 👨💼

Te paso con Dario - Asesor de Soloiperu.

📲 Escribeme directo al WhatsApp: 942 418 535
👉 https://wa.me/51942418535?text=Hola%20Dario,%20vengo%20de%20Marketplace%20y%20quiero%20un%20tanque

Respondo en menos de 5 minutos.'''
}

def enviar_mensaje(recipient_id, texto):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": texto}}
    r = requests.post(url, json=payload)
    print(f"Enviado a {recipient_id}: {r.status_code} - {r.text}")

@app.route('/')
def home():
    return "Bot Soloiperu ACTIVO - Ica", 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verificacion de Facebook
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            print("WEBHOOK VERIFICADO")
            return request.args.get('hub.challenge')
        print(f"Token invalido. Recibido: {request.args.get('hub.verify_token')} Esperado: {VERIFY_TOKEN}")
        return "Token invalido", 403

    # POST - Llegan mensajes
    data = request.get_json()
    print("MENSAJE RECIBIDO:", json.dumps(data, indent=2))
    
    if data and data.get('object') == 'page':
        for entry in data.get('entry', []):
            for event in entry.get('messaging', []):
                if 'message' in event and 'text' in event['message']:
                    sender_id = event['sender']['id']
                    message_text = event['message']['text'].lower()
                    print(f"De {sender_id}: {message_text}")

                    if any(p in message_text for p in ['disponible', 'hola', 'buenas', 'info', 'tanque']):
                        enviar_mensaje(sender_id, MENSAJES['bienvenida'])
                    elif any(p in message_text for p in ['precio', 'cuanto', 'costo', '1100', '2500', '5000']):
                        enviar_mensaje(sender_id, MENSAJES['precios'])
                    elif any(p in message_text for p in ['donde', 'ubicacion', 'direccion', 'local', 'tienda']):
                        enviar_mensaje(sender_id, MENSAJES['ubicacion'])
                    elif 'fotos' in message_text or 'foto' in message_text:
                        enviar_mensaje(sender_id, MENSAJES['fotos'])
                    elif 'asesor' in message_text or 'whatsapp' in message_text:
                        enviar_mensaje(sender_id, MENSAJES['asesor'])
                    else:
                        enviar_mensaje(sender_id, MENSAJES['bienvenida'])
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
