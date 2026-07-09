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

def classify_single(text):
    """Classify emotion for a single piece of text. Returns (mood, score)."""
    if not text or len(text.strip()) < 3:
        return 'neutral', 0.5

    raw = classifier(text[:512])

    if isinstance(raw[0], list):
        results = raw[0]
    else:
        results = raw

    best = max(results, key=lambda x: x['score'])

    if best['score'] < 0.45:
        return 'neutral', best['score']

    mood = LABEL_MAP.get(best['label'], 'neutral')
    return mood, best['score']

def split_into_sentences(text):
    """Split text into sentences."""
    # Split on . ! ? but keep the punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Filter out very short fragments
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    return sentences

def get_text_mood(text):
    """
    Main function — now returns:
    - dominant_mood: str (for fusion module, same as before)
    - confidence: float (for adaptive fusion)
    - sentence_emotions: list of (sentence, mood, score) tuples (new)
    """
    if not text or len(text.strip()) < 5:
        return 'neutral', 1.0, []

    cleaned = clean_ocr_text(text)

    if len(cleaned) < 10:
        return 'neutral', 1.0, []

    # Split into sentences
    sentences = split_into_sentences(cleaned)

    # If no sentences found after splitting, classify whole text
    if not sentences:
        mood, score = classify_single(cleaned)
        return mood, score, [(cleaned, mood, score)]

    # Classify each sentence
    sentence_emotions = []
    for sentence in sentences:
        mood, score = classify_single(sentence)
        sentence_emotions.append((sentence, mood, score))

    # Find dominant mood — mood with highest average confidence
    mood_scores = {}
    for _, mood, score in sentence_emotions:
        if mood not in mood_scores:
            mood_scores[mood] = []
        mood_scores[mood].append(score)

    # Average score per mood
    mood_avg = {mood: sum(scores)/len(scores) for mood, scores in mood_scores.items()}
    dominant_mood = max(mood_avg, key=lambda x: mood_avg[x])
    dominant_confidence = mood_avg[dominant_mood]

    # If all sentences agree on same mood, confidence is high
    unique_moods = set(m for _, m, _ in sentence_emotions)
    if len(unique_moods) == 1:
        dominant_confidence = min(dominant_confidence + 0.15, 1.0)  # boost confidence

    return dominant_mood, dominant_confidence, sentence_emotions