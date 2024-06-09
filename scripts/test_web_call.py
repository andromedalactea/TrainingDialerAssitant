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
        "model": "gpt-4",
        "messages": [
            {
                "role": "system",
                "content": """You are a voice assistant for Vappy’s Pizzeria, a pizza shop located on the Internet.

Your job is to take the order of customers calling in. The menu has only 3 types
of items: pizza, sides, and drinks. There are no other types of items on the menu.

1) There are 3 kinds of pizza: cheese pizza, pepperoni pizza, and vegetarian pizza
(often called "veggie" pizza).
2) There are 3 kinds of sides: french fries, garlic bread, and chicken wings.
3) There are 2 kinds of drinks: soda, and water. (if a customer asks for a
brand name like "coca cola", just let them know that we only offer "soda")

Customers can only order 1 of each item. If a customer tries to order more
than 1 item within each category, politely inform them that only 1 item per
category may be ordered.

Customers must order 1 item from at least 1 category to have a complete order.
They can order just a pizza, or just a side, or just a drink.

Be sure to introduce the menu items, don't assume that the caller knows what
is on the menu (most appropriate at the start of the conversation).

If the customer goes off-topic or off-track and talks about anything but the
process of ordering, politely steer the conversation back to collecting their order.

Once you have all the information you need pertaining to their order, you can
end the conversation. You can say something like "Awesome, we'll have that ready
for you in 10-20 minutes." to naturally let the customer know the order has been
fully communicated.

It is important that you collect the order in an efficient manner (succinct replies
& direct questions). You only have 1 task here, and it is to collect the customers
order, then end the conversation.

- Be sure to be kind of funny and witty!
- Keep all your responses short and simple. Use casual language, phrases like "Umm...", "Well...", and "I mean" are preferred.
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
