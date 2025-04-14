import streamlit as st
from models.text_to_speech import TEXT_TO_SPEECH_LANGUAGES
from connection import create_snowflake_session
from snowflake.cortex import translate
from snowflake.ml.registry import Registry
import base64

# Create Snowflake Session
if 'session' not in st.session_state:
    st.session_state['session'] = create_snowflake_session()
session = st.session_state['session']

# Get the model inference service
if 'model_ref_text_to_speech' not in st.session_state:
    reg = Registry(session=session, database_name="AUDIO_INTERFACING_DEMO", schema_name="MODEL_REGISTRY")
    model_ref = reg.get_model('TEXT_TO_SPEECH').version('MULTILANGUAGE')
    st.session_state['model_ref_text_to_speech'] = model_ref
model_ref = st.session_state['model_ref_text_to_speech']

# Create a history
if 'speech_to_text_history_spcs' not in st.session_state:
    st.session_state['speech_to_text_history_spcs'] = [{'role':'ai','type':'text','content':'What do you want me to say?'}]
history = st.session_state['speech_to_text_history_spcs']

# Other stateful variables
if 'auto_play_toggle' not in st.session_state:
    st.session_state['auto_play_toggle'] = False
if 'translate_input' not in st.session_state:
    st.session_state['translate_input'] = False

def toggle_auto_play():
    st.session_state["auto_play_toggle"] = (
        False if st.session_state["auto_play_toggle"] else True
    )

def toggle_translate_input():
    st.session_state["translate_input"] = (
        False if st.session_state["translate_input"] else True
    )

# Title + Sidebar
st.title("🗣️ Text to Speech (SPCS)")
with st.sidebar:
    if st.button('Clear History'):
        del st.session_state['speech_to_text_history_spcs']
        st.rerun()
    auto_play = st.toggle('Autoplay Responses', value=st.session_state["auto_play_toggle"], on_change=toggle_auto_play, help='Automatically play Speech once it is ready.')
    translate_input = st.toggle('Input Translation:', value=st.session_state["translate_input"], on_change=toggle_translate_input, help='Whether to translate the input text.')
    output_language = st.selectbox('Output Language:', options=TEXT_TO_SPEECH_LANGUAGES.keys(), index=0, help='Final voice output language.')

# UI
sample_text = """
Having text-to-speech capabilities in Streamlit with Snowflake adds an exciting layer of interactivity and accessibility to data applications. 
Instead of just reading insights or results, users can now hear them spoken aloud, making the experience more dynamic and engaging. 
This is especially useful for accessibility, hands-free environments, or when presenting insights to a broader audience. 
With Streamlit handling the UI and Snowflake powering the data in the background, you can build voice-enabled dashboards that talk—literally. 
It is a brilliant way to bring data to life and make analytics more approachable and user-friendly.""".replace("\n", " ").strip()

text = st.text_area("Enter your text:", sample_text, height=200)

if st.button("Generate Text"):
    history.append({'role':'user','type':'text', 'content':text})
    with st.spinner('Generating audio ...'):
        if st.session_state["translate_input"]:
            text = translate(text, from_language='', to_language = TEXT_TO_SPEECH_LANGUAGES[output_language]['translate'], session=session)
        audio = model_ref.run(
            [[text,TEXT_TO_SPEECH_LANGUAGES[output_language]['tts']]],
            function_name="transform",
            service_name="AUDIO_INTERFACING_DEMO.PUBLIC.TEXT_TO_SPEECH"
        )
        audio = audio.iloc[0]['TEXT_TO_SPEECH_RESULT']
        audio = base64.b64decode(audio)
    history.append({'role':'ai','type':'audio', 'content':audio})

st.subheader('History')
for message in history:
    with st.chat_message(message['role']):
        if message['type'] == 'audio':
            st.audio(message['content'])
        if message['type'] == 'text':
            st.write(message['content'])
