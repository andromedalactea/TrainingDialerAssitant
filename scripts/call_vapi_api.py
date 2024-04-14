import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import pytz


# Chage the environment variables
load_dotenv()

def call_ai(phone_number, url_server, phoneNumberId="c976502a-22c5-4f10-9aa0-36bd075d473b", assistant_id="3f559bb3-4688-42d7-a690-c76bcaaea873"):
    """
    Calls the AI assistant using the VAPI API.

    Args:
      customer_id (str): The ID of the customer.
      phone_number (str): The phone number to call.
      assistant_id (str, optional): The ID of the assistant..

    Returns:
      None
    """
    # Extract the promt for the AI like USer
    with open('promts/calificate_call.promt', 'r') as file:
        promt_AI_like_user = file.read()  # read all content

    ## Determinate the fisrt message respect the actual time of United States
    # Establecer la zona horaria de Nueva York
    try:
        timezone = pytz.timezone('America/New_York')

        # Obtener la hora actual en la zona horaria deseada
        time = datetime.now(timezone)

        # Determinar el mensaje apropiado según la hora
        if time.hour < 12:
            first_message = "Good morning"
        elif time.hour < 18:
            first_message = "Good afternoon"
        else:
            first_message = "Good night"
    except:
        first_message = "Hello"

    # Doing the call with Vapi API
    token_vapi = os.getenv('VAPI_KEY')
    url = "https://api.vapi.ai/call/phone"
    payload = {
      "phoneNumberId": phoneNumberId,
      "customer": {
      "number": phone_number
      },
      "assistantId": assistant_id,
      "assistant": {
          "firstMessage": f"{first_message}",
          "serverUrl": url_server,

        "model": {
          "provider": "custom-llm",
          "url": "https://api.openai.com/v1/chat/completions",
          "model": "ft:gpt-3.5-turbo-0125:igd:okey:9CrshYXi",
          "urlRequestMetadataEnabled": False,
          "messages": [
             {
               "role": "system",
               "content": f"{promt_AI_like_user}"
             }
           ]
         } 
      }
    }
    headers = {
      "Authorization": f"Bearer {token_vapi}",
      "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    # print(response.text)
    # print(response.status_code)
    return "Call made" if response.status_code == 201 else "Error making the call"+ response.text

# Example usage:
if __name__ == "__main__":

    phone_number = "+18065133219" # My phone number
    # phone_number = "+19545158586" # Other phone number
    print(call_ai( phone_number))

