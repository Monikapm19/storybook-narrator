MOOD_LABELS = ['happy', 'sad', 'scary', 'calm', 'exciting', 'neutral']

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


def fuse_single(image_mood, image_score, text_mood, text_score, text=""):
    """
    Confidence-aware fusion for one (image_mood, text_mood) pair.
    Weights are proportional to each modality's own confidence for this pair
    (not a fixed split) — a low-confidence CLIP prediction contributes less
    than a high-confidence one, and likewise for text.

    Returns (final_mood, fused_confidence, explanation_dict).
    """
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

    fused_confidence = img_weight * image_score + text_weight * text_score

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

    return final_mood, fused_confidence, explanation


def fuse_moods(image_mood, image_score, text_mood, text_score, text=""):
    """Page-level fusion (kept for the page's overall mood badge / summary)."""
    final_mood, _, explanation = fuse_single(image_mood, image_score, text_mood, text_score, text)
    return final_mood, explanation


def fuse_sentence_level(image_mood, image_score, sentence_emotions):
    """
    Novelty 1 + 2 + 3:
    Fuses the page illustration's mood with EACH sentence's own text emotion
    individually (confidence-aware weighting = Novelty 2), flagging
    visual-textual conflicts per sentence with narrative labels like
    'suspense' / 'irony' where applicable (Novelty 3). Driving narration off
    this list — instead of one mood for the whole page — is what makes the
    narration dynamically shift mood sentence to sentence (Novelty 1).

    image_mood/image_score: from the page illustration (CLIP), constant
        across every sentence on that page.
    sentence_emotions: list of (sentence, text_mood, text_score) from
        text_emotion.get_text_mood().

    Returns: list of dicts, one per sentence:
        {sentence, mood, confidence, text_mood, text_score, explanation}
    """
    results = []
    for sentence, text_mood, text_score in sentence_emotions:
        final_mood, fused_confidence, explanation = fuse_single(
            image_mood, image_score, text_mood, text_score, sentence
        )
        results.append({
            'sentence': sentence,
            'mood': final_mood,
            'confidence': fused_confidence,
            'text_mood': text_mood,
            'text_score': text_score,
            'explanation': explanation,
        })
    return results