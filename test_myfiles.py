from input_handler import load_as_image
from ocr import extract_text
import fitz  # PyMuPDF

class FakeUpload:
    def __init__(self, path):
        self.name = path
        self._file = open(path, 'rb')
    def read(self):
        return self._file.read()

pdf_path = 'test_pages/sample_book.pdf'

# First, find out how many pages the PDF has
pdf = fitz.open(pdf_path)
total_pages = len(pdf)
pdf.close()
print(f'Total pages in PDF: {total_pages}')
print()

full_story_text = []

for page_num in range(total_pages):
    fake_file = FakeUpload(pdf_path)  # new file object each time
    img = load_as_image(fake_file, page_number=page_num)
    text = extract_text(img)

    print(f'--- Page {page_num} ---')
    print(text)
    print()

    full_story_text.append(text)

# Combine all pages into one continuous string
combined = ' '.join(full_story_text)
print('=== FULL COMBINED TEXT ===')
print(combined)