import streamlit as st
from input_handler import load_as_image
from ocr import extract_text
from clip_mood import get_image_mood
from text_emotion import get_text_mood
from fusion import fuse_moods
from tts import generate_audio
import fitz

st.set_page_config(page_title='Storybook Narrator', layout='centered')
st.title('Storybook Narrator')
st.write('Upload a storybook page or PDF to hear it narrated expressively.')

uploaded_file = st.file_uploader(
    'Upload storybook page or PDF',
    type=['jpg', 'jpeg', 'png', 'pdf']
)

if uploaded_file:
    page_num = 0
    if uploaded_file.name.lower().endswith('.pdf'):
        pdf = fitz.open(stream=uploaded_file.read(), filetype='pdf')
        uploaded_file.seek(0)  # reset file pointer so it can be read again
        total_pages = len(pdf)
        page_num = st.slider('Select page', 1, total_pages, 1) - 1

    image = load_as_image(uploaded_file, page_number=page_num)
    st.image(image, caption='Uploaded Page', use_column_width=True)

    if st.button('Narrate This Page'):
        with st.spinner('Reading the page...'):
            text = extract_text(image)
        st.write(f'Extracted Text: {text}')

        with st.spinner('Detecting mood...'):
            img_mood, img_score = get_image_mood(image)
            text_mood, text_score = get_text_mood(text)
            final_mood = fuse_moods(img_mood, img_score, text_mood, text_score)

        st.write(f'Image Mood: {img_mood} ({img_score:.0%})')
        st.write(f'Text Mood: {text_mood} ({text_score:.0%})')
        st.success(f'Final Mood: {final_mood.upper()}')

        with st.spinner('Generating narration...'):
            audio_bytes = generate_audio(text, final_mood)
        st.audio(audio_bytes, format='audio/mp3')