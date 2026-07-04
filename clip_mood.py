import clip
import torch
from PIL import Image

# Load CLIP model once
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model, preprocess = clip.load('ViT-B/32', device=device)

# Your 6 mood prompts --- these are your classification labels
MOOD_PROMPTS = [
    'a happy and joyful illustration',
    'a sad and emotional illustration',
    'a scary and dark tense illustration',
    'a calm and peaceful illustration',
    'an exciting and action-filled illustration',
    'a neutral and plain illustration'
]

MOOD_LABELS = ['happy', 'sad', 'scary', 'calm', 'exciting', 'neutral']

def get_image_mood(pil_image):
    """
    Input: PIL Image
    Output: (mood_label: str, confidence_score: float)
    """
    image = preprocess(pil_image).unsqueeze(0).to(device)
    text = clip.tokenize(MOOD_PROMPTS).to(device)

    with torch.no_grad():
        logits_per_image, _ = model(image, text)
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

    best_idx = probs.argmax()
    return MOOD_LABELS[best_idx], float(probs[best_idx])