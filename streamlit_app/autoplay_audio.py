import streamlit as st
import base64
def play(audio):
    # Play audio in Streamlit immediately (hack)
    b64 = base64.b64encode(audio).decode()

    # HTML autoplay audio
    autoplay_html = f"""
    <audio autoplay>
    <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    Your browser does not support the audio element.
    </audio>
    """
    st.markdown(autoplay_html, unsafe_allow_html=True)