import edge_tts
import asyncio
import io

MOOD_SETTINGS = {
    'happy':    {'voice': 'en-US-JennyNeural', 'rate': '-5%',  'pitch': '+5Hz'},
    'sad':      {'voice': 'en-US-JennyNeural', 'rate': '-20%', 'pitch': '-10Hz'},
    'scary':    {'voice': 'en-US-JennyNeural', 'rate': '-15%', 'pitch': '-15Hz'},
    'calm':     {'voice': 'en-US-JennyNeural', 'rate': '-10%', 'pitch': '+0Hz'},
    'exciting': {'voice': 'en-US-JennyNeural', 'rate': '+5%',  'pitch': '+5Hz'},
    'neutral':  {'voice': 'en-US-JennyNeural', 'rate': '+0%',  'pitch': '+0Hz'},
    'suspense': {'voice': 'en-US-JennyNeural', 'rate': '-25%', 'pitch': '-20Hz'},
    'irony':    {'voice': 'en-US-JennyNeural', 'rate': '+0%',  'pitch': '+0Hz'},
}

async def _generate_single(text, mood):
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

async def _generate_sentences(sentence_emotions):
    all_audio = b''
    for sentence, mood, score in sentence_emotions:
        if not sentence.strip():
            continue
        clip = await _generate_single(sentence, mood)
        all_audio += clip
    return all_audio

def generate_audio(text, mood, sentence_emotions=None):
    if sentence_emotions and len(sentence_emotions) > 1:
        return asyncio.run(_generate_sentences(sentence_emotions))
    else:
        return asyncio.run(_generate_single(text, mood))