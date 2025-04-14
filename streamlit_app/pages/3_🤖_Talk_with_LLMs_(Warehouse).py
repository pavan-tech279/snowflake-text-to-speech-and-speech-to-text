import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from models.speech_to_text import SpeechToText
from models.text_to_speech import TextToSpeech, TEXT_TO_SPEECH_LANGUAGES
from autoplay_audio import play
from models.snowflake_llms import SNOWFLAKE_LLMS
from connection import create_snowflake_session
from snowflake.cortex import complete

# Create Snowflake Session
if 'session' not in st.session_state:
    st.session_state['session'] = create_snowflake_session()

# Create a history
if 'llm_history' not in st.session_state:
    st.session_state['llm_history'] = [{'role':'ai','type':'text','content':"Let's talk! 😊"}]
history = st.session_state['llm_history']

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

# Other stateful variables
if 'multilanguage' not in st.session_state:
    st.session_state['multilanguage'] = False

def toggle_multilanguage():
    st.session_state["multilanguage"] = (
        False if st.session_state["multilanguage"] else True
    )

def dropdown_change():
    # avoid ingesting existing recording to chat
    st.session_state["do_not_run"] = True

session = st.session_state['session']

# Title + Sidebar
st.title("🤖 Talk to LLMs (Warehouse)")
with st.sidebar:
    if st.button('Clear History'):
        del st.session_state['llm_history']
        st.rerun()
    auto_play = st.toggle('Autoplay Responses', value=st.session_state["auto_play_toggle"], on_change=toggle_auto_play, help='Automatically play Speech once it is ready.')
    output_language = st.selectbox('Output Language:', options=TEXT_TO_SPEECH_LANGUAGES.keys(), index=0, help='Final voice output language.', on_change=dropdown_change)
    llm = st.selectbox('LLM:', options=SNOWFLAKE_LLMS, index=0, help='The LLM you want to talk to.', on_change=dropdown_change)
    model_size = st.selectbox('Speech-To-Text-Model:', ['tiny','base','small','medium','large-v3-turbo','large-v3'], index=0, on_change=dropdown_change)
    if model_size not in ['large-v3-turbo','large-v3']:
        multilanguage = st.toggle('Multilingual Model', value=st.session_state["multilanguage"], on_change=toggle_multilanguage)
    else:
        multilanguage = st.toggle('Multilingual Model', value=True, disabled=True, help='Large models always support multilanguage.')
# Load models
#model_size = 'base'
text_to_speech = TextToSpeech(lang_code=TEXT_TO_SPEECH_LANGUAGES[output_language]['tts'])
speech_to_text = SpeechToText(model_id=f'openai/whisper-{model_size}')

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

# Dummy st.chat_input (needed for autoscrolling)
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
    text = speech_to_text.transform(audio.read())
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
        audio_output = text_to_speech.transform(llm_response)
        if auto_play:
            play(audio_output)
        history.append({'role':'ai','type':'combined', 'content':[llm_response,audio_output]})
    
    # print to UI
    with st.chat_message('ai'):
        st.write(llm_response)
        st.audio(audio_output)

st.session_state["do_not_run"] = False