import os
import streamlit as st
from vapi_python import Vapi
from dotenv import load_dotenv

load_dotenv(override=True)

# Configurar Vapi
vapi = Vapi(api_key=os.getenv('VAPI_KEY_PUBLIC'))

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

" are preferred.
- This is a voice conversation, so keep your responses short, like in a real conversation. Don't ramble for too long.""",
            },
        ],
    },
}

# Iniciar el asistente
vapi.start(assistant=assistant)

# Crear la interfaz de Streamlit
st.title("Vappy's Pizzeria Voice Assistant")
st.write("Click the button below and start speaking to place your order!")

if st.button("Start Talking"):
    st.write("Please enable your microphone and start speaking...")

    # Aquí debes agregar el código JavaScript para capturar el audio
    st.markdown(
        """
        <script>
        const startRecording = () => {
            navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                const mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();

                const audioChunks = [];
                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });

                mediaRecorder.addEventListener("stop", () => {
                    const audioBlob = new Blob(audioChunks);
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);
                    audio.play();

                    // Aquí puedes enviar el audio al servidor para su procesamiento
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'audio.wav');

                    fetch('https://your-server-url/upload', {
                        method: 'POST',
                        body: formData
                    }).then(response => {
                        return response.json();
                    }).then(data => {
                        console.log(data);
                        // Manejar la respuesta del servidor
                    }).catch(error => {
                        console.error('Error:', error);
                    });
                });

                setTimeout(() => {
                    mediaRecorder.stop();
                }, 5000); // Grabar durante 5 segundos
            });
        };

        document.querySelector('button').addEventListener('click', startRecording);
        </script>
        """,
        unsafe_allow_html=True
    )