import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from models.speech_to_text import SpeechToText
from models.text_to_speech import TextToSpeech, TEXT_TO_SPEECH_LANGUAGES
from autoplay_audio import play
from models.snowflake_llms import SNOWFLAKE_LLMS
from connection import create_snowflake_session
from snowflake.cortex import complete
from snowflake.ml.registry import Registry
import base64
import pandas as pd
from model_calling import speech_to_text_call
from model_calling import text_to_speech_call


# Create Snowflake Session
if 'session' not in st.session_state:
    st.session_state['session'] = create_snowflake_session()
session = st.session_state['session']

# Get the model inference service
if 'model_ref_text_to_speech' not in st.session_state:
    reg = Registry(session=session, database_name="AUDIO_INTERFACING_DEMO", schema_name="MODEL_REGISTRY")
    model_ref = reg.get_model('TEXT_TO_SPEECH').version('MULTILANGUAGE')
    st.session_state['model_ref_text_to_speech'] = model_ref
model_ref_text_to_speech = st.session_state['model_ref_text_to_speech']

# Get the model inference service
if 'model_ref_speech_to_text' not in st.session_state:
    reg = Registry(session=session, database_name="AUDIO_INTERFACING_DEMO", schema_name="MODEL_REGISTRY")
    model_ref = reg.get_model('SPEECH_TO_TEXT').version('MULTIPLE')
    st.session_state['model_ref_speech_to_text'] = model_ref
model_ref_speech_to_text = st.session_state['model_ref_speech_to_text']

# Create a history
if 'llm_history_spcs' not in st.session_state:
    st.session_state['llm_history_spcs'] = [{'role':'ai','type':'text','content':"Let's talk! 😊"}]
history = st.session_state['llm_history_spcs']

# Other stateful variables
if 'auto_play_toggle' not in st.session_state:
    st.session_state['auto_play_toggle'] = False
if 'do_not_run' not in st.session_state:
    st.session_state['do_not_run'] = False

def toggle_auto_play():
    st.session_state["auto_play_toggle"] = (
        False if st.session_state["auto_play_toggle"] else True
    )
    # avoid ingesting existing recording to chat
    st.session_state["do_not_run"] = True

def dropdown_change():
    # avoid ingesting existing recording to chat
    st.session_state["do_not_run"] = True

# Title + Sidebar
st.title("🤖 Talk to LLMs (SPCS)")
with st.sidebar:
    if st.button('Clear History'):
        del st.session_state['llm_history_spcs']
        st.rerun()
    auto_play = st.toggle('Autoplay Responses', value=st.session_state["auto_play_toggle"], on_change=toggle_auto_play, help='Automatically play Speech once it is ready.')
    output_language = st.selectbox('Output Language:', options=TEXT_TO_SPEECH_LANGUAGES.keys(), index=0, help='Final voice output language.', on_change=dropdown_change)
    llm = st.selectbox('LLM:', options=SNOWFLAKE_LLMS, index=0, help='The LLM you want to talk to.', on_change=dropdown_change)
    model_size = st.selectbox('Speech-To-Text-Model:', ['tiny','base','small','medium','large-v3-turbo'], index=0, on_change=dropdown_change)
    _ = st.toggle('Multilingual Model', value=True, disabled=True, help='SPCS models are all multilanguage models.')

# UI
# Audio input container (fixed to bottom, z-index to overlay st.chat_input)
with stylable_container(
        key="bottom_content",
        css_styles="""
            {
                position: fixed;
                bottom: 10px;
                z-index: 9999;
            }
            """,
    ):
    # Audio input
    audio = st.audio_input("🎙️ Ask a question!")

# Hidden dummy st.chat_input (needed for autoscrolling)
st.chat_input('Dummy')
st.markdown(
    """
    <style>
    div[data-testid="stChatInput"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

for message in history:
    if message['type'] == 'combined':
        with st.chat_message(message['role']):
            st.write(message['content'][0])
            st.audio(message['content'][1])

if audio and not st.session_state['do_not_run']:
    # Convert User Input to Text
    with st.spinner('Transcribing ...'):
        text = speech_to_text_call(session=session, audio_bytes=audio.read(), model_size=model_size.replace('-','_'))
    history.append({'role':'user','type':'combined', 'content':[text,audio]})
    # print to UI
    with st.chat_message('user'):
        st.write(text)
        st.audio(audio)

    # Send input to LLM and get response
    with st.spinner('Generating LLM Response ...'):
        prompt = f"Answer the following question but make sure to spell out all numbers. Respond in {output_language}. {text}"
        llm_response = complete(llm, prompt, session=session)

    # Turn LLM output into Speech
    with st.spinner('Generating audio ...'):
        audio_output = text_to_speech_call(session=session, text=llm_response, lang_code=TEXT_TO_SPEECH_LANGUAGES[output_language]['tts'])
        if auto_play:
            play(audio_output)
        history.append({'role':'ai','type':'combined', 'content':[llm_response,audio_output]})
    
    # print to UI
    with st.chat_message('ai'):
        st.write(llm_response)
        st.audio(audio_output)

st.session_state["do_not_run"] = False