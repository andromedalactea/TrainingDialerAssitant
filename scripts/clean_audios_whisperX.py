import os
import json
from dotenv import load_dotenv
load_dotenv()

from process_audio_to_openai_training_format import process_audio_to_openai_training_format
import whisperx
import gc

# Environment variables
HF_TOKEN = os.getenv("HF_TOKEN")

def  speaker_transcription_and_identify(audio_file):
    """
    This function takes an audio file and returns the transcription of the audio
    and the speaker identification of the audio.

    Parameters:
    audio_file (str): The path to the audio file.

    Returns:
    dict: A dictionary containing the transcription and speaker identification of the audio.
    """
    # Configuration parameters
    device = "cpu"
    batch_size = 3 # reduce if low on GPU mem
    compute_type = "float32" # change to "int8" if low on GPU mem (may reduce accuracy)

    # Whisper procesing
    audio = whisperx.load_audio(audio_file)
    model = whisperx.load_model("tiny", device, compute_type=compute_type)
    result = model.transcribe(audio, batch_size=batch_size)

    # 2. Align whisper output
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)


    ## Diarization of the text
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=HF_TOKEN,
                                                device=device)

    diarize_segments = diarize_model(audio, min_speakers=2, max_speakers=2)
    result = whisperx.assign_word_speakers(diarize_segments, result)
    print(result)
    # Process the audio to OpenAI training format
    result = process_audio_to_openai_training_format(result["segments"])

    final_format = {"messages": result}
    print(final_format)
    return final_format

def process_directory(audio_directory, output_file):
    """
    Processes all audio files in the given directory and writes the results
    to a JSONL file, one line per audio file.

    Parameters:
    audio_directory (str): The path to the directory containing audio files.
    output_file (str): The path to the JSONL file where results will be saved.
    """
    # Filtrar para obtener solo archivos .wav y .mp3
    audio_files = [f for f in os.listdir(audio_directory)
                   if os.path.isfile(os.path.join(audio_directory, f)) and f.endswith(('.wav', '.mp3'))]

    with open(output_file, 'a') as jsonl_file:
        for audio_file in audio_files:
            audio_path = os.path.join(audio_directory, audio_file)
            print('The audio will process is: ', audio_path)
            result = speaker_transcription_and_identify(audio_path)
            # Escribir el resultado como una nueva línea en el archivo JSONL
            jsonl_file.write(json.dumps(result) + '\n')
            print(f"Processed and added to JSONL: {audio_file}")

if __name__ == "__main__":
    # audio_directory = "audios_train_assistant"
    # output_file = "output_files/training_dialer.jsonl"
    # process_directory(audio_directory, output_file)

    result = speaker_transcription_and_identify('audios_train_assistant/20240325-184022_8605638886-all.mp3')
    with open('output_files/training_dialer.jsonl', 'a') as jsonl_file:
        jsonl_file.write(json.dumps(result) + '\n')
