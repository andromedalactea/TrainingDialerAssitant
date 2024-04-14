# Python libraries
import os
import codecs
import sys
import signal

# Third-party libraries
from flask import Flask, request, jsonify
from pyngrok import ngrok
from dotenv import load_dotenv

# Guardar las referencias originales
original_stdout = sys.stdout
original_stderr = sys.stderr

# Redirigir stdout y stderr a /dev/null para suprimir la salida
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# Función para imprimir mensajes críticos en la consola original
def print_to_console(*args, **kwargs):
    print(*args, file=original_stdout, **kwargs)

# Load environment variables from the .env file
load_dotenv()

# Function to calificate the call
from openai import OpenAI

## Define some functions
def calificate_call(call_transcript: str):
    # System promt to the AI
    with open('promts/calificate_call.promt', 'r') as file:
        promt_calificate_AI = file.read()  # read all content

    # Create the client for OpenAI
    client = OpenAI()

    completion = client.chat.completions.create(
    model="gpt-4-0125-preview",
    temperature=0,
    messages=[
        {"role": "system", "content": f"{promt_calificate_AI}"},
        {"role": "system", "content": f"{call_transcript}"}
    ]
    )
    return str(completion.choices[0].message.content)

def webhook():
    """
    Webhook endpoint that receives POST requests.
    """
    data = request.json
    print(data)
    # Check if it's the end of the call 'end-of-call-report'
    message_vapi = data.get('message')

    if message_vapi.get('type') == 'end-of-call-report':

        # Extract the necessary information to save a history
        transcript = message_vapi.get('transcript')

        # Save the information as a note in the specific lead
        calification = calificate_call(transcript)

        # Decode calification
        decode_calification = codecs.decode(calification, 'unicode_escape')
        
        print_to_console(decode_calification)
        
        return jsonify({"status": "success", "calification": calification}), 200
    else:
        return jsonify({"status": "ignored"}), 200
    
def shutdown():
    print('Shutting down server...')
    os.kill(os.getpid(), signal.SIGINT)
    return 'Server shutting down...'

app = Flask(__name__)
ngrok.set_auth_token(os.getenv('NGROK_KEY'))

@app.route('/calificate_call', methods=['POST'])
def main_call():
    """
    This function is the main entry point for the webhook.
    is weebhook is only of one usage, to calificate the call.
    """
    # Start the webhook
    webhook()

    # Shutdown the server
    shutdown()
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Define the port of your choice, by default Flask uses port 5000
    port = 5000
    # Configura el subdominio personalizado
    subdomain = "loosely-stirred-porpoise.ngrok-free.app"  # El subdominio que reservaste

    # Configure ngrok with the port on which Flask is running
    ngrok_tunnel = ngrok.connect(port, domain=subdomain)
    print('NGROK Tunnel URL:', ngrok_tunnel.public_url)

    # Run the Flask server, making sure it is publicly accessible and on the correct port
    app.run(host='0.0.0.0', port=5000)

    # Disconnect the ngrok tunnel when you are ready to end the session
    ngrok.disconnect(ngrok_tunnel.public_url)