import edge_tts
import asyncio
import io

# edge-tts strips custom SSML (no <mstts:express-as> styles, no true emotion) —
# only rate/volume/pitch on a single <prosody> tag are honored, and pitch has
# been reported to have no audible effect on recent backend versions. So the
# only two levers we can actually rely on are rate and volume, pushed to
# deltas large enough to be clearly audible rather than a subtle nudge.
# One narrator voice is kept constant across all moods so the story doesn't
# sound like it's being read by a different person sentence to sentence —
# only the delivery (speed/loudness) shifts with mood, the way a human
# narrator would perform it.
NARRATOR_VOICE = 'en-US-JennyNeural'

MOOD_SETTINGS = {
    'happy':    {'voice': NARRATOR_VOICE, 'rate': '+3%',  'pitch': '+10Hz', 'volume': '+15%'},
    'sad':      {'voice': NARRATOR_VOICE, 'rate': '-20%', 'pitch': '-10Hz', 'volume': '-20%'},
    'scary':    {'voice': NARRATOR_VOICE, 'rate': '-18%', 'pitch': '-15Hz', 'volume': '-20%'},
    'calm':     {'voice': NARRATOR_VOICE, 'rate': '-12%', 'pitch': '+0Hz',  'volume': '-8%'},
    'exciting': {'voice': NARRATOR_VOICE, 'rate': '+15%', 'pitch': '+10Hz', 'volume': '+18%'},
    'neutral':  {'voice': NARRATOR_VOICE, 'rate': '+0%',  'pitch': '+0Hz',  'volume': '+0%'},
    'suspense': {'voice': NARRATOR_VOICE, 'rate': '-8%',  'pitch': '-18Hz', 'volume': '-25%'},
    'irony':    {'voice': NARRATOR_VOICE, 'rate': '+8%',  'pitch': '+5Hz',  'volume': '+5%'},
}

async def _generate_single(text, mood):
    settings = MOOD_SETTINGS.get(mood, MOOD_SETTINGS['neutral'])
    communicate = edge_tts.Communicate(
        text=text,
        voice=settings['voice'],
        rate=settings['rate'],
        pitch=settings['pitch'],
        volume=settings['volume']
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