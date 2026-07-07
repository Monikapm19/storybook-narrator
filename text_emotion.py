from transformers import pipeline
import re

# Load once
classifier = pipeline(
    'text-classification',
    model='bhadresh-savani/distilbert-base-uncased-emotion',
    return_all_scores=True
)

# Map DistilBERT's labels to your 6 mood categories
LABEL_MAP = {
    'joy':      'happy',
    'love':     'happy',
    'sadness':  'sad',
    'anger':    'scary',
    'fear':     'scary',
    'surprise': 'exciting'
}

def clean_ocr_text(text):
    # Remove tokens that are all caps and short (OCR noise like VI, NWAI)
    text = re.sub(r'\b[A-Z0-9]{1,4}\b', '', text)
    # Remove special characters except basic punctuation
    text = re.sub(r'[^a-zA-Z\s\.,!?\'"]', '', text)
    # Remove very short leftover words (1-2 chars)
    text = ' '.join(w for w in text.split() if len(w) > 2)
    return text.strip()

def get_text_mood(text):
    if not text or len(text.strip()) < 5:
        return 'neutral', 1.0

    cleaned = clean_ocr_text(text)

    # If after cleaning text is too short, return neutral
    if len(cleaned) < 10:
        return 'neutral', 1.0

    raw = classifier(cleaned[:512])

    if isinstance(raw[0], list):
        results = raw[0]
    else:
        results = raw

    best = max(results, key=lambda x: x['score'])
    mood = LABEL_MAP.get(best['label'], 'neutral')
    return mood, best['score']