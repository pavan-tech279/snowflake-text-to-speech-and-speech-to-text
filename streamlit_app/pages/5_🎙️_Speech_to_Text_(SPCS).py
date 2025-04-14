import streamlit as st
from connection import create_snowflake_session
from snowflake.ml.registry import Registry

# Create Snowflake Session
if 'session' not in st.session_state:
    st.session_state['session'] = create_snowflake_session()
session = st.session_state['session']

# Get the model inference service
if 'model_ref_speech_to_text' not in st.session_state:
    reg = Registry(session=session, database_name="AUDIO_INTERFACING_DEMO", schema_name="MODEL_REGISTRY")
    model_ref = reg.get_model('SPEECH_TO_TEXT').version('MULTIPLE')
    st.session_state['model_ref_speech_to_text'] = model_ref
model_ref = st.session_state['model_ref_speech_to_text']

# Create a history
if 'text_to_speech_history_spcs' not in st.session_state:
    st.session_state['text_to_speech_history_spcs'] = [{'role':'ai','type':'text','content':'Let me transcribe your your speech.'}]
history = st.session_state['text_to_speech_history_spcs']

if 'translate_input_spcs' not in st.session_state:
    st.session_state['translate_input_spcs'] = False

def toggle_multilanguage():
    st.session_state["multilanguage"] = (
        False if st.session_state["multilanguage"] else True
    )

# Title + Sidebar
st.title("🎙️ Speech to Text (SPCS)")
with st.sidebar:
    if st.button('Clear History'):
        del st.session_state['text_to_speech_history_spcs']
        st.rerun()
    model_size = st.selectbox('Speech-To-Text-Model:', ['tiny','base','small','medium','large-v3-turbo'], index=0)
    _ = st.toggle('Multilingual Model', value=True, disabled=True, help='SPCS models are all multilanguage models.')

# UI
audio = st.audio_input("🎙️ Speak to me")

if st.button("Generate Text"):
    history.append({'role':'user','type':'audio', 'content':audio})
    with st.spinner('Transcribing ...'):
        text = model_ref.run(
            [[audio.read(),model_size]],
            function_name="transform",
            service_name="AUDIO_INTERFACING_DEMO.PUBLIC.SPEECH_TO_TEXT"
        )
        text = text.iloc[0]['TRANSCRIPTION']
    history.append({'role':'ai','type':'text', 'content':text})

st.subheader('History')
for message in history:
    with st.chat_message(message['role']):
        if message['type'] == 'audio':
            st.audio(message['content'])
        if message['type'] == 'text':
            st.write(message['content'])