# Python libraries
import os
import codecs
import sys
import signal
import json

# Third-party libraries
from flask import Flask, request, jsonify
from pyngrok import ngrok
from dotenv import load_dotenv

# # Guardar las referencias originales
# original_stdout = sys.stdout
# original_stderr = sys.stderr

# # Redirigir stdout y stderr a /dev/null para suprimir la salida
# sys.stdout = open(os.devnull, 'w')
# sys.stderr = open(os.devnull, 'w')

# # Función para imprimir mensajes críticos en la consola original
# def print_to_console(*args, **kwargs):
#     print(*args, file=original_stdout, **kwargs)

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
    temperature = 0,
    messages=[
        {"role": "system", "content": f"{promt_calificate_AI}"},
        {"role": "system", "content": f"{call_transcript}"}
    ]
    )
    return str(completion.choices[0].message.content)

# Flask app
app = Flask(__name__)
@app.route('/calificate_call', methods=['POST'])
def main_call():
    """Webhook endpoint that receives POST requests and processes call transcriptions."""
    try:
        data = request.json
        
        message_vapi = data.get('message')
        print(data)
        if  message_vapi.get('type') == 'end-of-call-report':
            # Extract call id
            call_data = message_vapi.get('call', {})
            call_id = call_data.get('id')
            

            transcript = message_vapi.get('transcript')
            calification = calificate_call(transcript)

            # Decode calification and clean it up
            decoded_calification = codecs.decode(calification, 'unicode_escape').replace("```json", "").replace("```", "")
            # Prepare the dictionary to be saved
            calification_dict = {
                "call_id": call_id,
                "calification": decoded_calification
            }
            # Save the calification in a file like a jsonl
            # Read the existing data
            try:
                with open("output_files/califications_history.jsonl", "r") as file:
                    existing_data = file.readlines()
            except FileNotFoundError:
                existing_data = []

            # Write the new data at the top
            with open("output_files/califications_history.jsonl", "w") as file:
                file.write(json.dumps(calification_dict) + "\n" + "".join(existing_data))
            
            print(json.dumps(calification_dict))
            
            return jsonify({"status": "success", "calification": decoded_calification}), 200
        else:
            return jsonify({"status": "ignored"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Define the port of your choice, by default Flask uses port 5000
    port = 8080
    # Configura el subdominio personalizado
    subdomain = "loosely-stirred-porpoise.ngrok-free.app"  # El subdominio que reservaste

    # Configure ngrok with the port on which Flask is running
    ngrok_tunnel = ngrok.connect(port, domain=subdomain)
    print('NGROK Tunnel URL:', ngrok_tunnel.public_url)

    # Run the Flask server, making sure it is publicly accessible and on the correct port
    app.run(host='0.0.0.0', port=port)

    # Disconnect the ngrok tunnel when you are ready to end the session
    ngrok.disconnect(ngrok_tunnel.public_url)
