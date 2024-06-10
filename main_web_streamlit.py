import streamlit as st
import json
import time
import os
import contextlib
import io
from vapi_python import Vapi
from dotenv import load_dotenv

# Import the necessary modules from your custom scripts.
from scripts.weebhook_calification import *
from scripts.call_vapi_api import *

load_dotenv(override=True)

# Configurar el dominio y URL del servidor
domain = "loosely-stirred-porpoise.ngrok-free.app"
url_server = f"https://{domain}/calificate_call"

# Leer el prompt
with open('promts/AI_like_user.promt', 'r') as file:
    prompt_AI_like_user = file.read()

assistant = {
    "serverUrl": url_server,
    "name": "Vapi’s Pizza Front Desk",
    "firstMessage": "Vappy’s Pizzeria speaking, how can I help you?",
    "transcriber": {
        "provider": "deepgram",
        "model": "nova-2",
        "language": "en-US",
    },
    "voice": {
        "provider": "playht",
        "voiceId": "jennifer",
    },
    "model": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": """You are a voice assistant for Vappy’s Pizzeria, a pizza shop located on the Internet.

Your job is to take the order of customers calling in. The menu has only 3 types
of items: pizza, sides, and drinks. There are no other types of items on the menu.

- This is a voice conversation, so keep your responses short, like in a real conversation. Don't ramble for too long.""",
            },
        ],
    },
}

def main_interface():
    st.title("Vappy's Pizzeria Voice Assistant")
    
    if 'call_id' not in st.session_state:
        st.session_state['call_id'] = None

    if 'call_active' not in st.session_state:
        st.session_state['call_active'] = False

    if 'vapi_instance' not in st.session_state:
        st.session_state['vapi_instance'] = None

    if not st.session_state['call_active']:
        if st.button("Start Talking"):
            # Asegurarse de que no exista una instancia anterior de Vapi
            if st.session_state['vapi_instance'] is not None:
                del st.session_state['vapi_instance']
            
            st.session_state['vapi_instance'] = Vapi(api_key=os.getenv('VAPI_KEY_PUBLIC'))
            
            # Capturar la salida de consola de vapi.start()
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                call = st.session_state['vapi_instance'].start(assistant=assistant)

            # Obtener la salida capturada
            output = f.getvalue()

            # Buscar el ID de la llamada en la salida capturada
            call_id = None
            for line in output.splitlines():
                if "Joining call..." in line:
                    call_id = line.split("... ")[1]
                    break

            if call_id:
                st.session_state['call_id'] = call_id
                st.session_state['call_active'] = True
                st.rerun()
            else:
                st.error("Failed to start the call. Please try again.")

    if st.session_state['call_active']:
        st.write("You are in a call. Please use the button below to end the call.")
        if st.button("End Call"):
            st.session_state['vapi_instance'].stop()
            del st.session_state['vapi_instance']
            st.session_state['vapi_instance'] = None
            st.session_state['current_view'] = 'waiting'
            st.session_state['call_active'] = False
            st.rerun()

def waiting_interface():
    st.title('Waiting for Evaluation Results')
    st.write(f"Please wait, retrieving results for call ID: {st.session_state['call_id']}")

    if st.button("Back to Home"):
        st.session_state['current_view'] = 'main'
        st.rerun()

    filepath = "output_files/califications_history.jsonl"
    found = False
    attempts = 0

    while not found and attempts < 1000:
        with open(filepath, 'r') as file:
            for line in file:
                data = json.loads(line)
                if data.get("call_id") == st.session_state['call_id']:
                    found = True
                    st.session_state['data'] = data
                    st.session_state['current_view'] = 'results'
                    st.rerun()
                    return
        time.sleep(1)
        attempts += 1

    if not found:
        st.error("Failed to retrieve results after several attempts. Please try again later.")

def results_interface():
    st.title('Evaluation Results for Customer Interaction')

    if st.button("Back to Home"):
        st.session_state['current_view'] = 'main'
        st.rerun()

    data = st.session_state['data']

    if 'calification' in data:
        calification_data = json.loads(data["calification"])
        st.subheader('Metrics of evaluation (0-10):')

        for key, value in calification_data.items():
            if key not in ["Notes", "call_id"]:
                st.metric(label=key, value=value)

        if "Notes" in calification_data:
            st.subheader('Detailed Notes:')
            st.write(calification_data["Notes"])
        else:
            st.write("No detailed notes available.")
    else:
        st.error("Calification data not found in the response.")

    st.subheader('JSON Complete:')
    st.json(calification_data)

if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'main'

if st.session_state['current_view'] == 'main':
    main_interface()
elif st.session_state['current_view'] == 'waiting':
    waiting_interface()
elif st.session_state['current_view'] == 'results':
    results_interface()
