# Python libraries
import os
import codecs
import sys
import signal
import json
import pytz

# Third-party libraries
from datetime import datetime
from flask import Flask, request, jsonify
from pyngrok import ngrok
from dotenv import load_dotenv

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
    model="gpt-4o",
    temperature = 0,
    messages=[
        {"role": "system", "content": f"{promt_calificate_AI}"},
        {"role": "system", "content": f"{call_transcript}"}
    ]
    )
    return str(completion.choices[0].message.content)

def get_current_time_ny():
    # Define the timezone for New York
    ny_tz = pytz.timezone('America/New_York')
    
    # Get the current time in the New York timezone
    ny_time = datetime.now(ny_tz)
    
    # Extract the date, hour, minutes, and seconds
    date = ny_time.strftime('%Y-%m-%d')
    hour = ny_time.strftime('%H')
    minute = ny_time.strftime('%M')
    second = ny_time.strftime('%S')
    
    return f"{date} {hour}:{minute}:{second} NYT"

# Flask app
app = Flask(__name__)
@app.route('/<path:path>', methods=['POST', 'GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def main_call(path):
    """Webhook endpoint that receives POST requests and processes call transcriptions."""
    try:
        data = request.json
        
        message_vapi = data.get('message')
        print(data)
        if  message_vapi.get('type') == 'end-of-call-report':
            # Extract call id
            call_data = message_vapi.get('call', {})
            call_id = data['message']['call']['assistantOverrides']['metadata']['call_secundary_id']
            reference = data['message']['call']['assistantOverrides']['metadata']['reference']
            print(call_id)
            

            transcript = message_vapi.get('transcript')
            calification = calificate_call(transcript)

            # Decode calification and clean it up
            decoded_calification = codecs.decode(calification, 'unicode_escape').replace("```json", "").replace("```", "")
            # Prepare the dictionary to be saved
            calification_dict = {
                "call_id": call_id,
                "calification": decoded_calification,
                "time" : get_current_time_ny(),
                "reference": reference
            }
            # Save the calification in a file like a jsonl
            # Read the existing data
            try:
                # Lee el archivo JSON existente
                with open('public/califications_history.json', 'r') as file:
                    data = json.load(file)

                # Verifica que el archivo contenga una lista
                if isinstance(data, list):
                    # Inserta el nuevo elemento al principio de la lista
                    data.insert(0, calification_dict)
                else:
                    print("El archivo JSON no contiene una lista.")

                # Escribe la lista actualizada de nuevo en el archivo JSON
                with open('public/califications_history.json', 'w') as file:
                    json.dump(data, file, indent=4)

            except FileNotFoundError:
                existing_data = []

            

            return jsonify({"status": "success", "calification": decoded_calification}), 200
        else:
            return jsonify({"status": "ignored"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    
    # Define the port of your choice, by default Flask uses port 5000
    port = 8080
    # Configura el subdominio personalizado
    subdomain = "hugely-cute-sunfish.ngrok-free.app"  # El subdominio que reservaste

    # Configure ngrok with the port on which Flask is running
    ngrok_tunnel = ngrok.connect(port, domain=subdomain)
    print('NGROK Tunnel URL:', ngrok_tunnel.public_url)

    # Run the Flask server, making sure it is publicly accessible and on the correct port
    app.run(host='0.0.0.0', port=port)

    # Disconnect the ngrok tunnel when you are ready to end the session 
    ngrok.disconnect(ngrok_tunnel.public_url)
    