import json

def text_to_speech_call(session, text:str, lang_code:str):
    text = text.replace("'","''")
    sql_stmt = f"""
    SELECT BASE64_DECODE_BINARY(
        AUDIO_INTERFACING_DEMO.PUBLIC.TEXT_TO_SPEECH!TRANSFORM('{text}', '{lang_code}'
        )['TEXT_TO_SPEECH_RESULT']) AS RESULT
    """
    audio_bytes = bytes(session.sql(sql_stmt).collect()[0]['RESULT'])
    return audio_bytes


def speech_to_text_call(session, audio_bytes, model_size):
    sql_stmt = f"SELECT AUDIO_INTERFACING_DEMO.PUBLIC.SPEECH_TO_TEXT!TRANSFORM('{audio_bytes.hex()}'::BINARY, '{model_size}') AS RESULT"
    text = session.sql(sql_stmt).collect()[0]['RESULT']
    text = json.loads(text)['TRANSCRIPTION'].strip()
    return text