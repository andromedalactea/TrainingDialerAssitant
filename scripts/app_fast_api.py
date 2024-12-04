from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Query, BackgroundTasks  
from typing import List
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from pymongo import MongoClient, DESCENDING
from pydantic import  EmailStr
from dotenv import load_dotenv
from pytz import timezone
from openai import OpenAI
import uuid
from datetime import datetime
import base64
import os
import json
from bson import json_util
from io import BytesIO

# Local imports
from components.call_calification import calificate_call, calificate_call_from_direct_audio, get_current_time_ny, save_calification_mongo
from components.auxiliar_functions import absolute_path, convert_timestamp_to_date
from components.reports_for_email import generate_pdf_report
from components.send_emails import send_email_with_attachment
from components.diarization_with_openai import diarization
from components.train_model import fine_tunning_model

# Load environment variables
load_dotenv(override=True)

# Initialize the API
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['TrainingDialer']

# Openai client
client = OpenAI()

@app.post("/api/calificate_call")
async def main_call( data: dict):
    """Webhook endpoint that receives POST requests and processes call transcriptions."""   
    
    message = data.get("message")
    if  message.get("type") == "end-of-call-report":

        # Extract call id of vapi
        call_info = message.get("call")
        vapi_call_id = call_info.get("id")

        # Extract call data
        call_data = message.get("call", {})
        call_id = message["call"]["assistantOverrides"]["metadata"]["call_secundary_id"]
        reference = message["call"]["assistantOverrides"]["metadata"]["reference"]
        duration = message.get('durationSeconds')
        
        # Extract the transcript from the message
        transcript = message.get("transcript")
        
        # Extract audio url
        audio_url = message.get("recordingUrl")
        print(f"Audio URL: {audio_url}")

        # Extract the context of the call
        context_call = f"""This is some context for the call (For executive summary but is possible to use for other parts of the report as well):
            Date of the call: {convert_timestamp_to_date(message.get('timestamp'))}
            Duration of the call: {message.get('durationSeconds')} seconds
            Lead Name/ID: Agent Sales Trainer\n\n"
            """

        # Generate the calification direct from the AI audio or transcript
        try:
            transcript_from_audio, calification = calificate_call_from_direct_audio(audio_url, context_call)

            # Verificar si transcript_from_audio o calification son nulos
            if transcript_from_audio is None or calification is None:
                raise ValueError("One or both values are None")  # Forzar ir a la alternativa

        except Exception as e:
            print(f"Error: {e}")
            # Generate the calification
            calification = calificate_call(transcript)
        
        # Prepare the dictionary to be saved
        calification_dict = {
            "call_id": call_id,
            "vapi_call_id": vapi_call_id,
            "transcript": transcript,
            "calification": calification,
            "time" : get_current_time_ny(),
            "reference": reference,
            "duration": duration,
            "audio_url": audio_url
        }

        # Save the calification in a file like a jsonl
        save_calification_mongo(calification_dict)
        print("Calification saved")
        return {"status": "success", "calification": calification}
    else:
        return {"status": "ignored"}

@app.get("/api/call_info")
async def get_call(call_id: str):
    collection = db['performanceCalification']
    call = collection.find_one({"call_id": call_id}, {'_id': 0})
    if call:
        return JSONResponse(content=json.loads(json_util.dumps(call)))
    else:
        raise HTTPException(status_code=404, detail="Call not found")
    
@app.get("/api/call_info_paginated")
async def get_calls_paginated(page: int = 1, limit: int = 10):
    collection = db['performanceCalification']
    
    # Total documents in the collection
    total_calls = collection.count_documents({})
    
    # Sort the calls by time and get the paginated result
    calls = collection.find({}, {'_id': 0}).sort('time', -1).skip((page - 1) * limit).limit(limit)
    
    return {
        "total_calls": total_calls,
        "calls": list(calls),
        "page": page,
        "limit": limit
    }

@app.get("/api/search_calls")
async def search_calls(query: str, page: int = 1, limit: int = 10):
    collection = db['performanceCalification']
    
    # Realizar la búsqueda por coincidencias parciales en call_id o reference
    search_filter = {
        "$or": [
            {"call_id": {"$regex": query, "$options": "i"}},  # Búsqueda insensible a mayúsculas
            {"reference": {"$regex": query, "$options": "i"}}
        ]
    }
    
    total_calls = collection.count_documents(search_filter)
    
    # Ordenar por tiempo, como lo haces en la otra API
    calls = collection.find(search_filter, {'_id': 0}).sort('time', -1).skip((page - 1) * limit).limit(limit)
    
    return {
        "total_calls": total_calls,
        "calls": list(calls),
        "page": page,
        "limit": limit
    }


@app.get("/api/generate_report_file")
async def get_report(call_ids: List[str] = Query(...)):
    # Accedemos a la colección
    collection = db['performanceCalification']

    # Realizamos una búsqueda con el operador $in
    calls = collection.find({"call_id": {"$in": call_ids}}, {'_id': 0})
    
    # Convert the MongoDB cursor to a list of dictionaries
    calls_info = list(calls)

    # Si no se encontraron llamadas, lanzamos un error 404
    if not calls_info:
        raise HTTPException(status_code=404, detail="Calls not found")

    # Generamos el PDF como bytes (sin escribirlo en disco)
    pdf_bytes = generate_pdf_report(calls_info, absolute_path("../../css/style_report.css"))

    # Envolvemos los bytes en un BytesIO para poder retornarlos como StreamingResponse
    pdf_stream = BytesIO(pdf_bytes)

    # Devolvemos el PDF con el encabezado adecuado para el tipo de contenido
    return StreamingResponse(pdf_stream, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=call_report.pdf"
    })

@app.get("/api/send_report_email")
async def send_report_email(
    background_tasks: BackgroundTasks,        
    call_ids: List[str] = Query(...),
    receiver_email: EmailStr = Query(...),
    merge_pdfs: bool = Query(False)            
):
    # Accedemos a la colección
    collection = db['performanceCalification']

    # Realizamos una búsqueda con el operador $in
    calls = collection.find({"call_id": {"$in": call_ids}}, {'_id': 0})
    
    # Convertimos el cursor de MongoDB a una lista de diccionarios
    calls_info = list(calls)

    # Si no se encontraron llamadas, lanzamos un error 404
    if not calls_info:
        raise HTTPException(status_code=404, detail="Calls not found")

    # Si "merge_pdfs" es True, generamos un solo PDF con todos los reportes
    if merge_pdfs:
        pdf_bytes = generate_pdf_report(calls_info, absolute_path("../../css/style_report.css"))
        pdf_files = [('call_report.pdf', pdf_bytes)]  # Empaquetamos el nombre y los bytes del PDF
    else:
        # Generamos un PDF por cada llamada y los almacenamos en una lista
        pdf_files = [
            (f"call_report_{call['call_id']}.pdf", generate_pdf_report([call], absolute_path("../../css/style_report.css")))
            for call in calls_info
        ]

    # Enviamos el correo en segundo plano
    background_tasks.add_task(
        send_email_with_attachment,
        os.getenv("SENDER_EMAIL"),  # Tu dirección de correo configurada en el entorno
        receiver_email,
        "Call Reports",  # El asunto del correo
        "Please find the attached call reports.",  # El cuerpo del correo
        pdf_files  # Lista de PDFs (nombre y bytes)
    )

    # Retornamos un 200 si todo salió bien
    return {"message": "Email sent successfully."}

@app.post("/api/upload_audio")
async def upload_audio(
    file: UploadFile = File(...),  # Audio file in mp3 or wav format
    model_id: str = Form(..., description="The model_id for which the audio will be used"),  # Form data to receive model_id
    filename: str = Form(..., description="The name of the audio file"),  # Form data to receive the filename
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Endpoint to upload an audio file, transcribe and diarize it, and save it to the database.
    Additionally, this endpoint will update the specified model (by model_id) with the audio details.
    """
    
    # Supported file extensions
    allowed_extensions = ["mp3", "wav"]
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file extension '{file_extension}'. Supported: {allowed_extensions}")
    
    # Read the file content in base64 format
    audio_data = await file.read()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    # Generate a UUID for the audio
    audio_id = str(uuid.uuid4())

    # Get the current time in the New York timezone
    ny_tz = timezone('America/New_York')
    timestamp = datetime.now(ny_tz)
    last_updated = timestamp.isoformat()

    # Call the diarization function to get the transcript (ai_like_assistant) and swapped version (ai_like_user)
    transcript_list, swapped_transcript_list = diarization(audio_base64, file_extension)  # This function now returns two lists
    
    # Determine if diarization was successful (i.e., not an empty list)
    diarization_successful = bool(transcript_list)  # True if transcript_list is not empty

    # Prepare the data to be saved in MongoDB for the audio document
    audio_document = {
        "audio_id": audio_id,  # Unique audio identifier (UUID)
        "filename": filename,  # Original file name
        "file_extension": file_extension,  # mp3 or wav
        "audio_base64": audio_base64,  # Base64-encoded audio
        "models": [model_id],  # Model ID to associate with this audio
        "timestamp": timestamp.isoformat(),  # Date and time of the upload in NY time, ISO format
        "ai_like_assistant": transcript_list,  # Diarization as if spoken by an assistant
        "ai_like_user": swapped_transcript_list,  # Diarization as if spoken by a user
        "diarization_successful": diarization_successful,  # Boolean indicating if diarization succeeded
        "last_updated": last_updated  # New field for the last update time
    }

    # Insert the document into the audio collection in Mongo
    audio_collection = db["audio_uploads"]
    result = audio_collection.insert_one(audio_document)

    if result.inserted_id:
        # Now update the related model's information in the models collection
        model_collection = db["models"]
        
        # Prepare the audio info to be added to the model's `audios` list
        audio_info = {
            "audio_id": audio_id,
            "filename": filename,
            "last_updated": last_updated,
            "diarization_successful": diarization_successful
        }

        # Update the model: Add the new audio information to the `audios` list
        update_result = model_collection.update_one(
            {"model_id": model_id},  # Find the model by model_id
            {
                "$push": {"audios": audio_info},  # Push the new audio info into the audios list
                "$set": {"last_updated": last_updated}  # Also update the model's last_updated field
            }
        )

        if update_result.matched_count == 0:
            # The model_id wasn’t found, raise a 404 error
            raise HTTPException(status_code=404, detail="Model not found")

        return {
            "status": "success", 
            "message": "Audio uploaded, diarized, and processed successfully", 
            "diarization_successful": diarization_successful
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to save audio data in the database")
    
@app.post("/api/create_model")
async def create_model(model_name: str = Form(...)):
    """
    Endpoint to create a new model.
    Generates a UUID for the model and stores initial metadata fields, including timestamps and empty lists for audios and trained models.
    """
    collection = db['models']

    # Generate a new UUID for the model
    model_id = str(uuid.uuid4())

    # Get the current timestamp in NY Timezone
    # Define timezone
    NY_TIMEZONE = timezone('America/New_York')
    ny_timestamp = datetime.now(NY_TIMEZONE).isoformat()

    # Prepare the document to insert into MongoDB
    model_document = {
        "model_id": model_id,
        "name": model_name,
        "created_at": ny_timestamp,  # Timestamp of creation in NY time
        "last_updated": ny_timestamp,  # Last update, same as creation time initially
        "audios": [],  # Empty list for audios related to this model
        "trained_models": []  # Empty list for trained models
    }

    # Insert the document into the models collection
    result = collection.insert_one(model_document)

    if result.inserted_id:
        return {"status": "success", "model_id": model_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to create a new model")


# 2. Endpoint: Get models with pagination, sorted by `last_updated` and without `audios` and `trained_models`
@app.get("/api/models")
async def get_models_paginated(page: int = 1, limit: int = 10):
    """
    Endpoint to get models paginated and sort by last_updated field.
    The response omits `audios` and `trained_models` from the results.
    """
    collection = db['models']

    # Total number of documents in the collection
    total_models = collection.count_documents({})

    # Fetch the sorted models paginated, exclude `audios`, `trained_models`, and `_id`
    models = collection.find({}, {"audios": 0, "_id": 0})  # Excluye también `_id`
    models = models.sort('last_updated', DESCENDING).skip((page - 1) * limit).limit(limit)

    return {
        "total_models": total_models,
        "models": list(models),
        "page": page,
        "limit": limit
    }



# 3. Endpoint: Get full details for a specific model by its `model_id`
@app.get("/api/model/{model_id}")
async def get_model(model_id: str):
    """
    Endpoint to get full information for a specific model,
    updating 'trained_models' data if fine-tuning jobs have changed status.
    """
    collection = db['models']

    # Buscar el modelo por model_id
    model = collection.find_one({"model_id": model_id}, {'_id': 0})

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Verificar si hay trabajos de fine-tuning que no estén "succeeded" o "failed"
    trained_models = model.get("trained_models", [])
    model_updated = False  # Para saber si actualizamos el modelo
    # Definir zona horaria NY
    NY_TIMEZONE = timezone('America/New_York')
    current_time = datetime.now(NY_TIMEZONE).isoformat()

    for trained_model in trained_models:
        current_status = trained_model.get("status")
        job_id = trained_model.get("job_id")  # Extraer el job_id del diccionario correspondiente

        # Revisamos solo los trabajos que no están finalizados y tienen un job_id válido
        if current_status not in ["succeeded", "failed"] and job_id:
            try:
                # Llamada a OpenAI para obtener el nuevo estado del job
                status_response = client.fine_tuning.jobs.retrieve(job_id)
                new_status = status_response.status  # Asegurar que obtenemos el campo status

                # Si el estado cambió o es diferente, actualizamos en la base de datos
                if new_status != current_status:
                    trained_model["status"] = new_status  # Actualizamos el estado en la lista
                    trained_model["updated_at"] = current_time  # Actualizamos el tiempo
                    model_updated = True

                    # Solo si el estado es "succeeded", intentamos extraer fine_tuned_model
                    if new_status == "succeeded":
                        fine_tuned_model = status_response.fine_tuned_model
                        if fine_tuned_model:
                            trained_model["output_model"] = fine_tuned_model  # Reemplazamos el campo "output_model"

            except Exception as e:
                # Si hay un error al consultar la API, actualizamos ese trabajo a "failed"
                trained_model["status"] = "failed"
                trained_model["updated_at"] = current_time
                model_updated = True
                print(f"Error updating job {job_id}: {str(e)}")

    # Si hubo algún cambio en el modelo, actualizamos la base de datos
    if model_updated:
        model["last_updated"] = current_time  # Actualizamos el campo last_updated del modelo
        collection.update_one(
            {"model_id": model_id},
            {
                "$set": {
                    "trained_models": trained_models,
                    "last_updated": current_time
                },
            }
        )

    # Retornamos el modelo actualizado (o no actualizado si no hubo cambios)
    return JSONResponse(content=model)

@app.post("/api/fine_tune")
async def fine_tune_model_api(
    model_id: str = Form(..., description="The model_id to use for fine-tuning."),
    ai_like: str = Form(..., description="The field to use (ai_like_'assistant' or ai_like_'user')."),
    openai_model: str = Form(..., description="The OpenAI model to fine-tune.")
    ):

    """
    Endpoint to fine-tune an OpenAI model given a model_id and the field to use in the audios.
    """
    # Try to call the fine-tunning function and handle errors
    try:
        result = fine_tunning_model(model_id, db, openai_model, f"ai_like_{ai_like}")  # Use the fine_tunning_model function from your script
        return {"status": "success", "message": "Fine-tuning started successfully", "result": result}
    
    except ValueError as e:
        # Handle value errors (e.g., the model doesn't exist or no audios found)
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        # Handle any other type of errors
        raise HTTPException(status_code=500, detail=f"An error occurred during fine-tuning: {str(e)}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
