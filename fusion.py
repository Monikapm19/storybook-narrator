MOOD_LABELS = ['happy', 'sad', 'scary', 'calm', 'exciting', 'neutral']

# Fixed weights kept as a fallback reference (no longer used directly in fusion,
# since confidence-aware weighting replaces them dynamically per prediction)
IMAGE_WEIGHT = 0.65
TEXT_WEIGHT = 0.35

# Keywords associated with each mood, used to explain WHY the text mood was detected
MOOD_KEYWORDS = {
    'happy':    ['happy', 'joy', 'laughed', 'smile', 'fun', 'bright', 'sunny', 'excited', 'cheered'],
    'sad':      ['sad', 'alone', 'cry', 'lonely', 'lost', 'grief', 'tears', 'missing'],
    'scary':    ['dark', 'shadow', 'fear', 'scared', 'monster', 'strange', 'cold', 'howled', 'eyes'],
    'calm':     ['quiet', 'still', 'peaceful', 'gentle', 'soft', 'calm', 'evening'],
    'exciting': ['exciting', 'fast', 'thrill', 'race', 'blasted', 'cheered', 'adventure'],
    'neutral':  ['walked', 'said', 'went', 'store', 'bought'],
}


def fuse_moods(image_mood, image_score, text_mood, text_score, text=""):
    """
    Confidence-aware adaptive fusion with conflict resolution and explainability.

    Input: image_mood (str), image_score (float 0-1)
           text_mood (str), text_score (float 0-1)
           text (str, optional) — used to extract matched keywords for explanation
    Output: (final_mood: str, explanation: dict)
    """
    # Dynamic weighting: each modality's influence is proportional to its own confidence,
    # instead of a fixed 65/35 split
    total = image_score + text_score
    if total == 0:
        img_weight, text_weight = 0.5, 0.5
    else:
        img_weight = image_score / total
        text_weight = text_score / total

    conflict = image_mood != text_mood

    if not conflict:
        final_mood = image_mood
    else:
        # Conflict resolution: trust whichever modality is more confident
        final_mood = image_mood if image_score >= text_score else text_mood

    # Find which keywords in the text actually matched the winning text-side mood
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
    }

    return final_mood, explanation