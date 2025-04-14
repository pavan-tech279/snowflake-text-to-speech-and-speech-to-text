import streamlit as st
from connection import create_snowflake_session

st.title('Audio Interfaces in SiS')
st.subheader('Talk to LLMs and have SiS read the responses for you.')

st.image('https://github.com/michaelgorkow/snowflake-text-to-speech-and-speech-to-text/resources/header.jpg')

# Variables
if 'session' not in st.session_state:
    st.session_state['session'] = create_snowflake_session()

session = st.session_state['session']


st.markdown("""
This app let's you explore the deployed text-to-speech and speech-to-text capabilities in an interactive way.
It also allows you to have a conversation with an LLM by actually talking to it and listen to its responses.

## Text to Speech Models
The text-to-speech functionality is powered by models from Facebook's [Massive Multilingual Speech project](https://research.facebook.com/publications/scaling-speech-technology-to-1000-languages/).
These model's either run locally inside of the Streamlit App or they connect to inference services that were setup earlier.

The following models are available inside SiS:
| Model | Language |
|:--------------------:|:----------:|
| facebook/mms-tts-eng | English    |
| facebook/mms-tts-deu | German     |
| facebook/mms-tts-fra | French     |
| facebook/mms-tts-nld | Dutch      |
| facebook/mms-tts-hin | Hindi      |
| facebook/mms-tts-kor | Korean     |
| facebook/mms-tts-pol | Polish     |
| facebook/mms-tts-por | Portuguese |
| facebook/mms-tts-rus | Russian    |
| facebook/mms-tts-spa | Spanish    |
| facebook/mms-tts-swe | Swedish    |
            
The same list of models is hosted in the inference service.

## Speech to Text Models
The speech-to-text functionality is powered by Whisper models.
These model's either run locally inside of the Streamlit App or they connect to inference services that were setup earlier.

The following models are available inside SiS:
| Size           | Parameters | English-only | Multilingual |
|:--------------:|:----------:|:------------:|:------------:|
| tiny           | 39 M       | ✓            | ✓            |
| base           | 74 M       | ✓            | ✓            |
| small          | 244 M      | ✓            | ✓            |
| medium         | 769 M      | ✓            | ✓            |
| large-v3-turbo | 809 M      | x            | ✓            |

""")