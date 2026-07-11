import edge_tts
import asyncio
import io

# Each mood gets a different voice + rate + pitch
MOOD_SETTINGS = {
    'happy':    {'voice': 'en-US-JennyNeural', 'rate': '-5%',  'pitch': '+5Hz'},
    'sad':      {'voice': 'en-US-JennyNeural', 'rate': '-20%', 'pitch': '-10Hz'},
    'scary':    {'voice': 'en-US-JennyNeural', 'rate': '-15%', 'pitch': '-15Hz'},
    'calm':     {'voice': 'en-US-JennyNeural', 'rate': '-10%', 'pitch': '+0Hz'},
    'exciting': {'voice': 'en-US-JennyNeural', 'rate': '+5%',  'pitch': '+5Hz'},
    'neutral':  {'voice': 'en-US-JennyNeural', 'rate': '+0%',  'pitch': '+0Hz'},
    'suspense': {'voice': 'en-US-JennyNeural', 'rate': '-12%', 'pitch': '-8Hz'},
    'irony':    {'voice': 'en-US-JennyNeural', 'rate': '+0%',  'pitch': '-3Hz'},
}


async def _generate_single(text, mood):
    """Generate audio for a single sentence with given mood."""
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
    """Generate audio for each sentence with its own mood and stitch together."""
    all_audio = b''
    for sentence, mood, score in sentence_emotions:
        if not sentence.strip():
            continue
        clip = await _generate_single(sentence, mood)
        all_audio += clip
    return all_audio


async def _generate_whole(text, mood):
    """Fallback — generate audio for whole text with one mood."""
    return await _generate_single(text, mood)


def generate_audio(text, mood, sentence_emotions=None):
    """
    Main TTS function.
    - If sentence_emotions provided: generate per-sentence audio and stitch
    - If not provided: fallback to whole text with one mood (backward compatible)
    """
    if sentence_emotions and len(sentence_emotions) > 1:
        # Sentence-level dynamic narration
        return asyncio.run(_generate_sentences(sentence_emotions))
    else:
        # Fallback to whole text
        return asyncio.run(_generate_whole(text, mood))