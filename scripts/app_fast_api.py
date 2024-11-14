from fastapi import FastAPI, HTTPException, Request, status, Query, BackgroundTasks  
from typing import List
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from pymongo import MongoClient
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import os
import json
from bson import json_util, ObjectId
from io import BytesIO

# Local imports
from components.call_calification import calificate_call, calificate_call_from_direct_audio, get_current_time_ny, save_calification_mongo
from components.auxiliar_functions import absolute_path, convert_timestamp_to_date
from components.reports_for_email import generate_pdf_report
from components.send_emails import send_email_with_attachment


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

@app.get("/trained_models")
async def get_data():
    collection = db["TrainingDialerDB"]["trained_models"]
    documents = list(collection.find({}))
    return JSONResponse(content=json.loads(json_util.dumps(documents)))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
