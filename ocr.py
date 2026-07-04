import easyocr
import numpy as np
from PIL import Image

# Initialize reader once (slow to load, fast to use)
reader = easyocr.Reader(['en'], gpu=False)

def extract_text(pil_image):
    """
    Input: PIL Image
    Output: string — all text found on the page
    """
    # Always upscale 2x for better OCR accuracy on small/low-res text
    pil_image = pil_image.resize(
        (pil_image.width * 2, pil_image.height * 2),
        Image.LANCZOS
    )

    img_array = np.array(pil_image)
    results = reader.readtext(img_array, detail=0)
    text = ' '.join(results)
    text = ' '.join(text.split())
    return text