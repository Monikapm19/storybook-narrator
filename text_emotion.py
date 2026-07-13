from transformers import pipeline
import re

classifier = pipeline(
    'text-classification',
    model='j-hartmann/emotion-english-distilroberta-base',
    return_all_scores=True
)

LABEL_MAP = {
    'joy':      'happy',
    'sadness':  'sad',
    'fear':     'scary',
    'anger':    'scary',
    'surprise': 'exciting',
    'disgust':  'neutral',
    'neutral':  'neutral'
}

# Keywords that strongly indicate a specific mood
MOOD_KEYWORDS = {
    'exciting': ['race', 'adventure', 'blast', 'zoomed', 'sprint', 'victory',
             'champion', 'won', 'scored', 'jumped', 'cheered', 'excited',
             'tournament', 'competition', 'rocket', 'explode', 'rush',
             'amusement', 'roller coaster', 'rides', 'heart raced', 'thrilling',
             'fastest', 'spinning', 'soaring', 'wild', 'spectacular',
             'sports day', 'finish line', 'medal', 'trophy', 'gold medal',
             'running race', 'never forget', 'great success', 'hard work'],
    'neutral':  ['walked', 'went', 'said', 'asked', 'told', 'looked',
                 'school', 'home', 'morning', 'afternoon', 'bought',
                 'classroom', 'rules', 'lunch', 'routine', 'daily'],
    'calm':     ['peaceful', 'quiet', 'still', 'gentle', 'breeze', 'relaxed',
                 'serene', 'soft', 'silence', 'lake', 'evening', 'sunset'],
    'scary':    ['dark', 'haunted', 'ghost', 'monster', 'shadow', 'creep',
                 'frightened', 'terror', 'scream', 'midnight', 'graveyard'],
    'sad':      ['cried', 'tears', 'lonely', 'missing', 'lost', 'goodbye',
                 'alone', 'sad', 'grief', 'hurt', 'broken', 'left behind'],
    'happy':    ['laughed', 'smiled', 'joy', 'happiness', 'birthday',
                 'celebrate', 'fun', 'sunshine', 'friend', 'love', 'wonderful']
}

def clean_ocr_text(text):
    text = re.sub(r'\b[A-Z0-9]{1,4}\b', '', text)
    text = re.sub(r'[^a-zA-Z\s\.,!?\'"]', '', text)
    text = ' '.join(w for w in text.split() if len(w) > 2)

    # Remove repeated words at end (OCR duplication artifact)
    words = text.split()
    if len(words) > 10:
        cutoff = int(len(words) * 0.8)
        main_words = words[:cutoff]
        tail_words = [w for w in words[cutoff:] if w.lower() not in [x.lower() for x in main_words]]
        text = ' '.join(main_words) + (' ' + ' '.join(tail_words) if tail_words else '')

    return text.strip()

def keyword_boost(text, base_mood, base_score):
    """Check if keywords strongly indicate a different mood than base."""
    text_lower = text.lower()
    keyword_hits = {}
    
    for mood, keywords in MOOD_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text_lower)
        if hits > 0:
            keyword_hits[mood] = hits

    if not keyword_hits:
        return base_mood, base_score

    top_keyword_mood = max(keyword_hits, key=keyword_hits.get)
    top_hits = keyword_hits[top_keyword_mood]

    # Only override if keyword signal is strong (3+ hits) and different from base
    if top_hits >= 3 and top_keyword_mood != base_mood:
        # Boost score slightly for keyword-matched mood
        return top_keyword_mood, min(base_score + 0.1, 1.0)

    return base_mood, base_score

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
    
    # Apply keyword boosting
    mood, score = keyword_boost(text, mood, best['score'])
    
    return mood, score

def split_into_sentences(text):
    """Split text into sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    return sentences

def get_text_mood(text):
    """
    Main function — returns:
    - dominant_mood: str (for fusion module)
    - confidence: float (for adaptive fusion)
    - sentence_emotions: list of (sentence, mood, score) tuples
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
        dominant_confidence = min(dominant_confidence + 0.15, 1.0)

    return dominant_mood, dominant_confidence, sentence_emotions