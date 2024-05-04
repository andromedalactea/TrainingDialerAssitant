import streamlit as st
import json
import time
import os

# Suponiendo que estas funciones están definidas en tus scripts importados
from scripts.weebhook_calification import *
from scripts.call_vapi_api import *


# Definir la página inicial
def main_interface():
    domain = "loosely-stirred-porpoise.ngrok-free.app"
    url_server = f"https://{domain}/calificate_call"

    st.title("Training Dialer Assistant")
    with st.form(key='my_form', clear_on_submit=True):
        number = st.text_input("Enter the phone number:", help="Format: +18065133220")
        submit_button = st.form_submit_button(label='Send')
        if submit_button:
            call_id = call_ai(number, url_server)  # Asume que call_ai devuelve un ID o None
            if call_id:
                st.session_state['call_id'] = call_id
                st.session_state['current_view'] = 'waiting'
                st.experimental_rerun()
            else:
                st.error("There was an error with the number you entered. Please check and try again.")

# Definir la interfaz de espera
def waiting_interface():
    st.title('Waiting for Evaluation Results')
    st.write(f"Please wait, retrieving results for call ID: {st.session_state['call_id']}")
    
    filepath = "califications.jsonl"
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
                    st.experimental_rerun()
                    return
        time.sleep(1)
        attempts += 1

    if not found:
        st.error("Failed to retrieve results after several attempts. Please try again later.")

# Definir la interfaz de resultados
def results_interface():
    st.title('Evaluation Results for Customer Interaction')
    
    # Obtener los datos que ya han sido cargados en la sesión
    data = st.session_state['data']
    
    # Extraer y parsear el JSON de la clave "calification"
    if 'calification' in data:
        # Convertir el JSON string en un diccionario
        calification_data = json.loads(data["calification"])
        
        st.subheader('Metrics of evaluation (0-10):')
        # Iterar sobre las claves, exceptuando "Notes" y "call_id" que se manejan por separado
        for key, value in calification_data.items():
            if key not in ["Notes", "call_id"]:
                st.metric(label=key, value=value)
        
        # Verificar y mostrar las "Notes"
        if "Notes" in calification_data:
            st.subheader('Detailed Notes:')
            st.write(calification_data["Notes"])
        else:
            st.write("No detailed notes available.")
    else:
        st.error("Calification data not found in the response.")

    st.subheader('JSON Complete:')
    st.json(calification_data)  # Mostrar el JSON completo de la calificación

# Control del flujo de la aplicación
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'main'

if st.session_state['current_view'] == 'main':
    main_interface()
elif st.session_state['current_view'] == 'waiting':
    waiting_interface()
elif st.session_state['current_view'] == 'results':
    results_interface()
