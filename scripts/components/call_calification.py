# Python libraries
import os

# Third-party libraries
import pytz
from datetime import datetime
from pymongo import MongoClient

# Function to calificate the call
from openai import OpenAI

## Define some functions
def calificate_call(call_transcript: str):
    # System promt to the AI
    with open('promts/calificate_call_v2.prompt', 'r') as file:
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