import os
from dotenv import load_dotenv
load_dotenv()

import whisper

model = whisper.load_model("large")
result = model.transcribe("audios_train_assistant/20240313-180141_8436612990-all.wav")
# print(result)

from openai import OpenAI
client = OpenAI()

# result = "Hello. Yes, hello sir. May I speak with the business owner of Miguel Srectoran, the owner? Oh, pleasure speaking to you sir. Apologies, I know you're busy, this is just less than a minute. So my name here is Nat, I'm from Aventus Bay and I'm not here to change any of what you have, I respect what you have. This is regarding about the new guidelines because you're an owner. So basically, her owners are no longer required to pay any processing fees, which is good news. It's zero processing, you will save thousands of dollars. But like I said sir, this is just information that we want to share to you. So my colleagues, they were trying to definitely reach you back tomorrow for only a couple of minutes and you will explain to you zero processing. So my question here, sir, is what would be the best time to reach you back tomorrow? Would it be the morning sir or in the afternoon?"
response = client.chat.completions.create(
  model="gpt-4",
  messages=
  [
  {"role": "user", "content":f"{result['text']}"},
  {"role": "system",
             "content":"""
  El texto anterior corresponde a una llamada entre agente de call center y un usuario quiero que me ayudes infiriendo según el contesto que parte del texto son dichas por el agente y cuales por el usuario y me entregues exactamente el mismo texto pero añadiendole la inferencia de quien esta habalando, no cambies nada de lo que se dice, solamente si considersa que algo esta fuera de contexto (como muchos numeros repetidos sin sentido) o hay algo que el agente no debio decir entonces lo omites  pero  nunca modifiques lo que se dijo solo eliminas las partes que consideres que un agente de call center bueno no debe de  decir, pero nunca cambies lo que se dijo en el texto original. tu respuesta debe de ser en formato json IMPORTANTE: debes de prestar mucha atención a la inferencia de quien habla en cada momento para hacer una correcta diarización del texto eres super experto en esto
  """}
                ]
        )
print(response.choices[0].message.content)