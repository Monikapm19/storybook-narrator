import torch
import numpy as np
from bark import generate_audio as bark_generate
from bark import SAMPLE_RATE
import soundfile as sf
import io

# Bark voice presets per mood
MOOD_VOICE_PRESETS = {
    'happy':    'v2/en_speaker_9',
    'sad':      'v2/en_speaker_3',
    'scary':    'v2/en_speaker_6',
    'calm':     'v2/en_speaker_2',
    'exciting': 'v2/en_speaker_5',
    'neutral':  'v2/en_speaker_1',
    'suspense': 'v2/en_speaker_6',
    'irony':    'v2/en_speaker_1',
}

MOOD_PROMPTS = {
    'happy':    '[laughs] ',
    'sad':      '[sighs] ',
    'scary':    '[whispers] ',
    'calm':     '',
    'exciting': '[gasps] ',
    'neutral':  '',
    'suspense': '[whispers] ',
    'irony':    '',
}

def generate_single_clip(text, mood):
    """Generate audio for a single text with given mood using Bark."""
    prompt = MOOD_PROMPTS.get(mood, '')
    voice = MOOD_VOICE_PRESETS.get(mood, MOOD_VOICE_PRESETS['neutral'])
    full_text = prompt + text

    audio_array = bark_generate(
        full_text,
        history_prompt=voice
    )

    # Save as WAV using soundfile
    buffer = io.BytesIO()
    sf.write(buffer, audio_array, SAMPLE_RATE, format='WAV')
    buffer.seek(0)
    return buffer.read()

def generate_audio(text, mood, sentence_emotions=None):
    """
    Main TTS function.
    - If sentence_emotions provided: generate per-sentence audio and stitch
    - If not: fallback to whole text with one mood
    """
    if sentence_emotions and len(sentence_emotions) > 1:
        all_audio = b''
        for sentence, sent_mood, score in sentence_emotions:
            if not sentence.strip():
                continue
            clip = generate_single_clip(sentence, sent_mood)
            all_audio += clip
        return all_audio
    else:
        return generate_single_clip(text, mood)