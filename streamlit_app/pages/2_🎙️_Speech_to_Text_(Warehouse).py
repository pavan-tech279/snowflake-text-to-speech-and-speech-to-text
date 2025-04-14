import streamlit as st
import time
from models.speech_to_text import SpeechToText

# Create a history
if 'text_to_speech_history' not in st.session_state:
    st.session_state['text_to_speech_history'] = [{'role':'ai','type':'text','content':'Let me transcribe your your speech.'}]
history = st.session_state['text_to_speech_history']

if 'translate_input' not in st.session_state:
    st.session_state['translate_input'] = False

# Other stateful variables
if 'multilanguage' not in st.session_state:
    st.session_state['multilanguage'] = False

def toggle_multilanguage():
    st.session_state["multilanguage"] = (
        False if st.session_state["multilanguage"] else True
    )

# Title + Sidebar
st.title("🎙️ Speech to Text (Warehouse)")
with st.sidebar:
    if st.button('Clear History'):
        del st.session_state['text_to_speech_history']
        st.rerun()
    model_size = st.selectbox('Speech-To-Text-Model:', ['tiny','base','small','medium','large-v3-turbo','large-v3'], index=0)
    if model_size not in ['large-v3-turbo','large-v3']:
        multilanguage = st.toggle('Multilingual Model', value=st.session_state["multilanguage"], on_change=toggle_multilanguage)
    else:
        multilanguage = st.toggle('Multilingual Model', value=True, disabled=True, help='Large models always support multilanguage.')

# Load model
model_id = f'openai/whisper-{model_size}'
if not st.session_state["multilanguage"] and model_size not in ['large-v3-turbo','large-v3']:
    model_id = f'{model_id}.en'

speech_to_text = SpeechToText(model_id=model_id)

# UI
audio = st.audio_input("🎙️ Speak to me")

if st.button("Generate Text"):
    history.append({'role':'user','type':'audio', 'content':audio})
    with st.spinner('Transcribing ...'):
        start_time = time.time()
        text = speech_to_text.transform(audio.read())
        st.write(f"Execution time (seconds): {round(time.time()-start_time,2)}")
    history.append({'role':'ai','type':'text', 'content':text})

st.subheader('History')
for message in history:
    with st.chat_message(message['role']):
        if message['type'] == 'audio':
            st.audio(message['content'])
        if message['type'] == 'text':
            st.write(message['content'])