from transformers import pipeline
import re

classifier = pipeline(
    'text-classification',
    model='j-hartmann/emotion-english-distilroberta-base',
    return_all_scores=True
)

# j-hartmann model labels
LABEL_MAP = {
    'joy':      'happy',
    'sadness':  'sad',
    'fear':     'scary',
    'anger':    'scary',
    'surprise': 'exciting',
    'disgust':  'neutral',
    'neutral':  'neutral'
}

def clean_ocr_text(text):
    text = re.sub(r'\b[A-Z0-9]{1,4}\b', '', text)
    text = re.sub(r'[^a-zA-Z\s\.,!?\'"]', '', text)
    text = ' '.join(w for w in text.split() if len(w) > 2)
    return text.strip()

def get_text_mood(text):
    if not text or len(text.strip()) < 5:
        return 'neutral', 1.0

    cleaned = clean_ocr_text(text)

    if len(cleaned) < 10:
        return 'neutral', 1.0

    raw = classifier(cleaned[:512])

    if isinstance(raw[0], list):
        results = raw[0]
    else:
        results = raw

    best = max(results, key=lambda x: x['score'])

    if best['score'] < 0.50:
        return 'neutral', best['score']

    mood = LABEL_MAP.get(best['label'], 'neutral')
    return mood, best['score']