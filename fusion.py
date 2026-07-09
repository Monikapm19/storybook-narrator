MOOD_LABELS = ['happy', 'sad', 'scary', 'calm', 'exciting', 'neutral']

MOOD_VALENCE = {
    'happy': 'positive',
    'calm': 'positive',
    'exciting': 'positive',
    'sad': 'negative',
    'scary': 'negative',
    'neutral': 'neutral'
}

IMAGE_WEIGHT = 0.65
TEXT_WEIGHT = 0.35

CONFLICT_CONFIDENCE_THRESHOLD = 0.5


def detect_conflict(image_mood, image_score, text_mood, text_score):
    if image_mood == text_mood:
        return None

    image_valence = MOOD_VALENCE.get(image_mood)
    text_valence = MOOD_VALENCE.get(text_mood)

    if image_valence == 'neutral' or text_valence == 'neutral':
        return None

    if image_score < CONFLICT_CONFIDENCE_THRESHOLD or text_score < CONFLICT_CONFIDENCE_THRESHOLD:
        return None

    if image_valence == 'negative' and text_valence == 'positive':
        return 'suspense'
    elif image_valence == 'positive' and text_valence == 'negative':
        return 'irony'

    return None


def fuse_moods(image_mood, image_score, text_mood, text_score):
    conflict_label = detect_conflict(image_mood, image_score, text_mood, text_score)
    if conflict_label:
        return conflict_label

    if image_mood == text_mood:
        return image_mood

    scores = {label: 0.0 for label in MOOD_LABELS}
    scores[image_mood] += IMAGE_WEIGHT * image_score
    scores[text_mood] += TEXT_WEIGHT * text_score

    return max(scores, key=scores.get)