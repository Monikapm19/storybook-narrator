MOOD_LABELS = ['happy', 'sad', 'scary', 'calm', 'exciting', 'neutral']

# Weights --- image gets more weight since it is our novelty
IMAGE_WEIGHT = 0.65
TEXT_WEIGHT = 0.35

def fuse_moods(image_mood, image_score, text_mood, text_score):
    """
    Input: image_mood (str), image_score (float 0-1)
           text_mood (str), text_score (float 0-1)
    Output: final_mood (str)
    """
    # If both agree, return immediately
    if image_mood == text_mood:
        return image_mood

    # Build a weighted score vector across all 6 moods
    scores = {label: 0.0 for label in MOOD_LABELS}
    scores[image_mood] += IMAGE_WEIGHT * image_score
    scores[text_mood] += TEXT_WEIGHT * text_score

    final_mood = max(scores, key=scores.get)
    return final_mood