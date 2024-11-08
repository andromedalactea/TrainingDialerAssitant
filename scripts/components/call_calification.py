# Python libraries
import re
import os
import base64

# Local imports
from components.auxiliar_functions import absolute_path

# Third-party libraries
import pytz
import requests
from datetime import datetime
from pymongo import MongoClient

# Function to calificate the call
from openai import OpenAI


## Define some functions
def calificate_call(call_transcript: str):
    # System promt to the AI
    prompt_path = absolute_path('../../prompts/calificate_call_v2.prompt')
    with open(prompt_path, 'r') as file:
        promt_calificate_AI = file.read()  # read all content

    # Create the client for OpenAI
    client = OpenAI()

    completion = client.chat.completions.create(
    model="gpt-4o",
    temperature = 0,
    messages=[
        {"role": "system", "content": f"{promt_calificate_AI}"},
        {"role": "system", "content": f"{call_transcript}"},
    ]
    )

    return str(completion.choices[0].message.content)

def calificate_call_from_direct_audio(audio_url: str, context_call: str="") -> tuple:
    # Fetch the audio file and convert it to a base64 encoded string
    response = requests.get(audio_url)
    response.raise_for_status()
    wav_data = response.content
    encoded_string = base64.b64encode(wav_data).decode('utf-8')
    promp_calificate_AI_path = absolute_path('../../prompts/calificate_call_from_audio_or_transcript_v2.prompt')
    with open(promp_calificate_AI_path, 'r') as file:
        promt_calificate_AI = file.read()  # read all content

    # Create the client for OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-audio-preview",
        modalities=["text"],
        messages=[
            {
                "role": "user",
                "content": [
                    { 
                        "type": "text",
                        "text": promt_calificate_AI
                    },
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": encoded_string,
                            "format": "wav"
                        }
                    },
                    {
                        "type": "text",
                        "text": context_call
                    }
                ]
            },
        ],
        max_tokens=8000,
        temperature=0
    )
    
    transcript_qualification = str(response.choices[0].message.content)
    print(transcript_qualification)
    # Definir los patrones de las etiquetas con expresiones regulares
    transcript_pattern = r"<transcript>\s*(.*?)\s*<transcript>"
    qualification_pattern = r"<qualification>\s*(.*?)\s*<qualification>"

    # Buscar la transcripción
    transcript_match = re.search(transcript_pattern, transcript_qualification, re.DOTALL)
    transcript = transcript_match.group(1) if transcript_match else None

    # Buscar la calificación
    qualification_match = re.search(qualification_pattern, transcript_qualification, re.DOTALL)
    qualification = qualification_match.group(1) if qualification_match else None

    return transcript, qualification

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

# Function to Save the calification in th MongoDB
def save_calification_mongo(call_json):

    # Configurate the MongoDB connection
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    
    # Select the database
    db = client['TrainingDialer']
    
    # Select the collection
    collection = db['performanceCalification']
    
    # Insert the calification
    collection.insert_one(call_json)
    
    return True

if __name__ == '__main__':
    
    #  Evaluate the calification response
    transcript = """
                AI: Good night. How are you doing?
                User: I'm doing wonderful.
                User: Can you tell me something about it? Maybe you're the business owner.
                AI: No.
                User: Okay. So much interesting. I'm here because, uh, I want to offer, um, credit card for you. Are you interested in that?
                AI: Yeah. We're a roofing company.
                """ 
    
    print(calificate_call(transcript))