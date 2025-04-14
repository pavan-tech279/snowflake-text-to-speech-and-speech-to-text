import os
# Set Hugging Face cache dir
os.environ["HF_HOME"] = '/tmp'
import streamlit as st
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import numpy as np
import soundfile as sf
from scipy.signal import resample
import io
from streamlit.runtime.uploaded_file_manager import UploadedFile

device = 0 if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

class SpeechToText():
    def __init__(self, model_id):
        self.pipeline = self.load_model(model_id)

    @staticmethod
    @st.cache_resource
    def load_model(model_id):
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        ).to(device)
    
        processor = AutoProcessor.from_pretrained(model_id)
    
        return pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
        )

    def transform(self, audio):
        # Load with soundfile
        audio_data, sample_rate = sf.read(io.BytesIO(audio))

        # Convert stereo to mono if needed
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)

        # Resample to 16000 Hz if needed
        target_rate = 16000
        if sample_rate != target_rate:
            num_samples = int(len(audio_data) * target_rate / sample_rate)
            audio_data = resample(audio_data, num_samples)
            sample_rate = target_rate

        # Transcribe
        result = self.pipeline({"array": audio_data.astype(np.float32), "sampling_rate": sample_rate})
        return result['text']
    
