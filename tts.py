import edge_tts
import asyncio
import io

# Each mood gets a different voice + rate + pitch
MOOD_SETTINGS = {
    'happy':    {'voice': 'en-US-JennyNeural',   'rate': '+20%', 'pitch': '+10Hz'},
    'sad':      {'voice': 'en-US-AriaNeural',     'rate': '-20%', 'pitch': '-10Hz'},
    'scary':    {'voice': 'en-US-GuyNeural',      'rate': '-15%', 'pitch': '-15Hz'},
    'calm':     {'voice': 'en-US-SaraNeural',     'rate': '-10%', 'pitch': '0Hz'},
    'exciting': {'voice': 'en-US-DavisNeural',    'rate': '+30%', 'pitch': '+15Hz'},
    'neutral':  {'voice': 'en-US-ChristopherNeural', 'rate': '+0%', 'pitch': '0Hz'},
}

async def _generate(text, mood):
    settings = MOOD_SETTINGS.get(mood, MOOD_SETTINGS['neutral'])
    communicate = edge_tts.Communicate(
        text=text,
        voice=settings['voice'],
        rate=settings['rate'],
        pitch=settings['pitch']
    )
    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk['type'] == 'audio':
            audio_buffer.write(chunk['data'])
    audio_buffer.seek(0)
    return audio_buffer.read()

def generate_audio_clip(text, mood):
    return asyncio.run(_generate(text, mood))