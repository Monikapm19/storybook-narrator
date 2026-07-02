from transformers import pipeline

# Load once — slow first time (downloading model), fast after that
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

def get_text_mood(text):
    if not text or len(text.strip()) < 5:
        return 'neutral', 1.0

    raw = classifier(text[:512])
    
    # handle both list-of-list and list-of-dict formats
    if isinstance(raw[0], list):
        results = raw[0]
    else:
        results = raw

    best = max(results, key=lambda x: x['score'])
    mood = LABEL_MAP.get(best['label'], 'neutral')
    return mood, best['score']