import fitz  # PyMuPDF
from PIL import Image
import io

def load_as_image(uploaded_file, page_number=0):
    """
    Input: uploaded file object (from Streamlit) + page number (for PDF)
    Output: PIL Image object
    """
    filename = uploaded_file.name.lower()

    if filename.endswith('.pdf'):
        pdf_bytes = uploaded_file.read()
        pdf = fitz.open(stream=pdf_bytes, filetype='pdf')
        page = pdf[page_number]
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes('png')))
    else:  # JPG or PNG
        img = Image.open(uploaded_file)

    return img