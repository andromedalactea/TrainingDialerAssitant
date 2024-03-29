
import os
from dotenv import load_dotenv
load_dotenv()

from pyannote.audio import Pipeline
import speechbrain
HF_TOKEN = os.getenv("HF_TOKEN")

from pyannote.audio import Pipeline

diarization_pipeline =  Pipeline.from_pretrained(
  "pyannote/speaker-diarization-3.1",
  use_auth_token=HF_TOKEN)

# import torch

# input_tensor = torch.from_numpy(sample["audio"]["array"][None, :]).float()
# outputs = diarization_pipeline(
#     {"waveform": input_tensor, "sample_rate": sample["audio"]["sampling_rate"]}
# )

# outputs.for_json()["content"]

from transformers import pipeline

asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small",
    language='en'
)

from speechbox import ASRDiarizationPipeline

pipeline = ASRDiarizationPipeline(
    asr_pipeline=asr_pipeline, diarization_pipeline=diarization_pipeline
)

pipeline('audios_train_assistant/20240313-180141_8436612990-all.wav')