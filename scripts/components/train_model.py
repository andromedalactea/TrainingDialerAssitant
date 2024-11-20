import os
import json
import tempfile
from openai import OpenAI
from pymongo import MongoClient
from pytz import timezone
from datetime import datetime

def get_openai_jsonl_from_audios(db, model_id, field_to_use):
    """
    Given a model_id, extract the relevant audio transcriptions where 'diarization_successful' is True,
    format them as a JSONL file, and return the file-like object ready to be uploaded to OpenAI.
    
    Args:
        db: MongoDB database connection.
        model_id (str): The model ID to filter the audios.
        field_to_use (str): The field to use from the audio data ('ai_like_assistant' or 'ai_like_user').

    Returns:
        tempfile.NamedTemporaryFile: A file-like object ready to be used in 'open(training_data, "rb")'.
    """

    # Step 1: Retrieve the model document from the `models` collection
    model_collection = db["models"]
    model = model_collection.find_one({"model_id": model_id}, {"_id": 0, "audios": 1})

    if not model or "audios" not in model:
        raise ValueError("Model not found or contains no audios")
    
    # Extract the list of audio IDs from the model's `audios` field
    audio_ids = [audio["audio_id"] for audio in model["audios"]]

    if not audio_ids:
        return []

    # Step 2: Query the `audio_uploads` collection to retrieve audios with `diarization_successful` set to True
    audio_collection = db["audio_uploads"]
    
    query = {
        "audio_id": {"$in": audio_ids},
        "diarization_successful": True
    }
    
    # Fetch audios from MongoDB (omit the MongoDB `_id` field)
    audio_documents = list(audio_collection.find(query, {"_id": 0, field_to_use: 1}))

    if not audio_documents:
        raise ValueError(f"No audios found with diarization_successful == True for model {model_id}")

    # Step 3: Prepare the data in JSONL format (one line per audio)
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".jsonl") as temp_file:
        for audio in audio_documents:
            # Ensure the field_to_use exists in each document
            if field_to_use in audio:
                # Build the JSON structure for OpenAI
                jsonl_data = {
                    "messages":  audio[field_to_use]
                }
                # Write each audio's data to the temp_file as a new line in JSONL format
                temp_file.write(json.dumps(jsonl_data) + "\n")

        return temp_file.name  # Return the path of the temp file


def fine_tunning_model(model_id: str, db, openai_model: str, ai_like: str) -> str:

    # Extract the data from the model
    temp_file_path = get_openai_jsonl_from_audios(db, model_id, ai_like)

    # Instantiate OpenAI client
    client = OpenAI()

    # Open the temporary file in 'rb' mode and upload it to OpenAI
    with open(temp_file_path, "rb") as f:
        response_file = client.files.create(
            file=f,
            purpose="fine-tune",
        )
    print(response_file)

    # Generate the fine tunning job
    response_fine_tunning = client.fine_tuning.jobs.create(
        training_file=response_file.id,
        model=openai_model
    )
    print(response_fine_tunning)
    # Get the current time in the New York timezone
    ny_tz = timezone('America/New_York')
    timestamp = datetime.now(ny_tz)
    time = timestamp.isoformat()

    # Add the model id and the training file id to the model document to the trained_models list like a dictionary
    model_collection = db["models"]
    model_collection.update_one(
        {"model_id": model_id},
        {"$push": {"trained_models": {"output_model": "processing",
                                      "openai_model": openai_model,
                                      "training_file_id": response_file.id,
                                      "training_file_name": response_file.filename,
                                      "job_id": response_fine_tunning.id,
                                      "status": response_fine_tunning.status,
                                      "created_at": time,
                                      "updated_at": time}}}
    )

    # Clean up the temporary file after it has been uploaded successfully
    os.remove(temp_file_path)

    return "success"

if __name__ == "__main__":

    from dotenv import load_dotenv
    import os

    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client['TrainingDialer']

    model_id = "3ef2981d-39fd-41d7-9823-654b5a664dc2"  
    result = fine_tunning_model(model_id, db, "gpt-4o-mini-2024-07-18", "ai_like_assistant")

    print(result)