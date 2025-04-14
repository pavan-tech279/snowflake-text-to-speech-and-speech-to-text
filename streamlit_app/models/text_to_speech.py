import os
# Set Hugging Face cache dir
os.environ["HF_HOME"] = '/tmp'
import streamlit as st
import torch
from transformers import AutoTokenizer, VitsModel, pipeline
import numpy as np
import scipy
import io
import base64

# Mapping of languages to codes
# translate = snowflake translate function
# tts = facebook model's code
TEXT_TO_SPEECH_LANGUAGES = {
    'English':{'translate':'en', 'tts':'eng'},
    'German':{'translate':'de', 'tts':'deu'},
    'French':{'translate':'fr', 'tts':'fra'},
    'Dutch':{'translate':'nl', 'tts':'nld'},
    'Hindi':{'translate':'nl', 'tts':'hin'},
    'Korean':{'translate':'ko', 'tts':'kor'},
    'Polish':{'translate':'po', 'tts':'pol'},
    'Portuguese':{'translate':'pt', 'tts':'por'},
    'Russian':{'translate':'ru', 'tts':'rus'},
    'Spanish':{'translate':'es', 'tts':'spa'},
    'Swedish':{'translate':'sv', 'tts':'swe'}
}

device = 0 if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

class TextToSpeech():
    def __init__(self, lang_code):
        model_id = f'facebook/mms-tts-{lang_code.lower()}'
        self.pipeline = self.load_model(model_id)

    @staticmethod
    @st.cache_resource
    def load_model(model_id):
        model = VitsModel.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        ).to(device)

        tokenizer = AutoTokenizer.from_pretrained(model_id)

        return pipeline(
            "text-to-speech",
            model=model,
            tokenizer=tokenizer,
            torch_dtype=torch_dtype,
            device=device,
        )

    def transform(self, text):
        output = self.pipeline(text)
        waveform = output["audio"]
        sampling_rate = output["sampling_rate"]
        # Ensure valid shape
        if waveform.ndim == 2:
            # Convert to mono (average channels)
            waveform = waveform.mean(axis=0)
        # Ensure waveform is float32 in range [-1.0, 1.0]
        waveform = np.asarray(waveform, dtype=np.float32)
        waveform = np.clip(waveform, -1.0, 1.0)
        # Convert to int16 for WAV format
        waveform_int16 = (waveform * 32767).astype(np.int16)
        # Write waveform to buffer
        buffer = io.BytesIO()
        scipy.io.wavfile.write(buffer, rate=sampling_rate, data=waveform_int16)
        buffer.seek(0)
        audio_bytes = buffer.getvalue()
        return audio_bytes