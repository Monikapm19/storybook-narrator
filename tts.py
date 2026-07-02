from gtts import gTTS
import io

# Speed settings per mood (gTTS only supports slow=True or slow=False)
MOOD_SPEED = {
    'happy':    False,
    'sad':      True,
    'scary':    True,
    'calm':     True,
    'exciting': False,
    'neutral':  False,
}

def generate_audio(text, mood):
    slow = MOOD_SPEED.get(mood, False)
    tts = gTTS(text=text, lang='en', slow=slow)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes.read()