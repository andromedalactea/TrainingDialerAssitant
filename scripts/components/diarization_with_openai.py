import re
import json
from openai import OpenAI
from dotenv import load_dotenv

# Define the absolute path function (adapt this for your project structure)
from components.auxiliar_functions import absolute_path

# Load environment variables
load_dotenv(override=True)

# Ensure the final role is always 'assistant' by truncating the list
def truncate_to_assistant(transcript_list):
    # Traverse the list in reverse and remove trailing 'user' entries
    while transcript_list and transcript_list[-1]['role'] == 'user':
        transcript_list.pop()  # Remove the last element if it's 'user'
    return transcript_list

def diarization(audio_data_base_64: str, audio_format: str="mp3") -> tuple:
    """Function that uses OpenAI to perform diarization and return a list of speaker-labeled transcripts."""
    
    # Load the diarization prompt from a file
    diarization_prompt_path = absolute_path('../../prompts/diarization.prompt')
    with open(diarization_prompt_path, 'r') as file:
        diarization_prompt = file.read()  # Read the entire prompt content
    
    # Create the OpenAI client
    client = OpenAI()

    # Call OpenAI API to process the transcription with diarization
    response = client.chat.completions.create(
        model="gpt-4o-audio-preview",  # The model may vary
        modalities=["text"],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_data_base_64,
                            "format": audio_format
                        }
                    },
                    { 
                        "type": "text",
                        "text": diarization_prompt
                    },
                ]
            },
        ],
        max_tokens=8000,
        temperature=0
    )
    
    # Extract the content from the response
    diarization_response = str(response.choices[0].message.content)
    print("Full Response: ", diarization_response)  # Debugging - show the raw response
    
    # Improved regex to capture the full list of dictionaries within brackets
    pattern = r'\[.*?\]'  # Capture everything within square brackets
    
    match = re.search(pattern, diarization_response, re.DOTALL)
    
    if match:
        # Extract the JSON fragment (list of dictionaries)
        json_str = match.group(0)
        
        try:
            # Convert the JSON string to a Python list of dictionaries
            transcript_list = json.loads(json_str)

            # Create a new list where roles are swapped
            swapped_transcript_list = []
            
            for transcript in transcript_list:
                # Make a copy of the dictionary to avoid modifying the original one
                new_transcript = transcript.copy()

                # Swap roles
                if new_transcript['role'] == 'assistant':
                    new_transcript['role'] = 'user'
                elif new_transcript['role'] == 'user':
                    new_transcript['role'] = 'assistant'

                # Append the swapped dictionary to the new list
                swapped_transcript_list.append(new_transcript)

            # Truncate the list to finish with the 'assistant' role
            transcript_list = truncate_to_assistant(transcript_list)
            swapped_transcript_list = truncate_to_assistant(swapped_transcript_list)
            
            return transcript_list, swapped_transcript_list
        
        except json.JSONDecodeError as e:
            print("Error: Failed to decode JSON.", e)
            return [], []
    else:
        print("No valid transcription data found.")
        return [], []

if __name__ == "__main__":
    # Load the audio file
    audio_path = absolute_path('/home/clickgreen/freelancers/TrainingDialerAssitant/test/audios_1/20240328-172959_9515320860-all.mp3')
    with open(audio_path, 'rb') as file:
        audio_data = file.read()

    # Call the diarization function
    diarized_output = diarization(audio_data)
    print("Diarization Result: ", diarized_output)