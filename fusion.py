MOOD_LABELS = ['happy', 'sad', 'scary', 'calm', 'exciting', 'neutral']

IMAGE_WEIGHT = 0.65
TEXT_WEIGHT = 0.35

MOOD_VALENCE = {
    'happy': 'positive',
    'calm': 'positive',
    'exciting': 'positive',
    'sad': 'negative',
    'scary': 'negative',
    'neutral': 'neutral'
}

CONFLICT_CONFIDENCE_THRESHOLD = 0.5

MOOD_KEYWORDS = {
    'happy':    ['happy', 'joy', 'laughed', 'smile', 'fun', 'bright', 'sunny', 'excited', 'cheered'],
    'sad':      ['sad', 'alone', 'cry', 'lonely', 'lost', 'grief', 'tears', 'missing'],
    'scary':    ['dark', 'shadow', 'fear', 'scared', 'monster', 'strange', 'cold', 'howled', 'eyes'],
    'calm':     ['quiet', 'still', 'peaceful', 'gentle', 'soft', 'calm', 'evening'],
    'exciting': ['exciting', 'fast', 'thrill', 'race', 'blasted', 'cheered', 'adventure'],
    'neutral':  ['walked', 'said', 'went', 'store', 'bought'],
}


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


def fuse_moods(image_mood, image_score, text_mood, text_score, text=""):
    total = image_score + text_score
    if total == 0:
        img_weight, text_weight = 0.5, 0.5
    else:
        img_weight = image_score / total
        text_weight = text_score / total

    conflict = image_mood != text_mood
    special_label = detect_conflict(image_mood, image_score, text_mood, text_score)

    if special_label:
        final_mood = special_label
    elif not conflict:
        final_mood = image_mood
    else:
        final_mood = image_mood if image_score >= text_score else text_mood

    matched_keywords = []
    if text:
        lower_text = text.lower()
        for word in MOOD_KEYWORDS.get(text_mood, []):
            if word in lower_text:
                matched_keywords.append(word)

    explanation = {
        'img_mood': image_mood,
        'text_mood': text_mood,
        'img_contribution_pct': round(img_weight * 100),
        'text_contribution_pct': round(text_weight * 100),
        'matched_keywords': matched_keywords[:3],
        'conflict': conflict,
        'special_label': special_label,
    }

    return final_mood, explanation