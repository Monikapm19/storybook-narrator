import streamlit as st
from input_handler import load_as_image
from ocr import extract_text
from clip_mood import get_image_mood
from text_emotion import get_text_mood
from fusion import fuse_moods
from tts import generate_audio
import fitz

st.set_page_config(page_title='Storybook Narrator', layout='centered')
st.title('📖 Storybook Narrator')
st.write('Upload a storybook page (image or PDF) to hear it narrated with matching emotion.')

st.markdown('---')

uploaded_file = st.file_uploader(
    'Choose a file',
    type=['jpg', 'jpeg', 'png', 'pdf'],
    help='Supports JPG, PNG, or PDF storybook pages'
)

if uploaded_file:
    st.caption(f"📄 {uploaded_file.name} — {uploaded_file.size / 1024:.1f} KB")

    page_num = 0
    if uploaded_file.name.lower().endswith('.pdf'):
        pdf = fitz.open(stream=uploaded_file.read(), filetype='pdf')
        uploaded_file.seek(0)  # reset file pointer so it can be read again
        total_pages = len(pdf)

        col1, col2 = st.columns([3, 1])
        with col1:
            page_num = st.slider('Select page', 1, total_pages, 1) - 1
        with col2:
            st.metric('Total Pages', total_pages)

    image = load_as_image(uploaded_file, page_number=page_num)

    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption='Uploaded Page', use_column_width=True)

    narrate_clicked = st.button('🎙️ Narrate This Page', use_container_width=True)

    if narrate_clicked:
        with st.spinner('Reading the page...'):
            text = extract_text(image)

        with col2:
            st.markdown('**Extracted Text**')
            st.text_area('Extracted text', text, height=200, disabled=True, label_visibility='collapsed')

        with st.spinner('Detecting mood...'):
            img_mood, img_score = get_image_mood(image)
            text_mood, text_score = get_text_mood(text)
            final_mood = fuse_moods(img_mood, img_score, text_mood, text_score)

        st.markdown('---')
        st.markdown('### Mood Detection')

        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.write(f"🖼️ Image Mood: **{img_mood}**")
            st.progress(img_score)
        with mcol2:
            st.write(f"📝 Text Mood: **{text_mood}**")
            st.progress(text_score)

        st.success(f"🎭 Final Mood: **{final_mood.upper()}**")

        # Temporary fallback: tts.py doesn't yet have voice styles for the
        # new 'suspense'/'irony' moods from fusion.py's conflict detection.
        # Map them to the closest existing supported mood until Kruthika
        # adds dedicated voice styles for these two.
        TTS_FALLBACK_MAP = {
            'suspense': 'scary',
            'irony': 'sad'
        }
        tts_mood = TTS_FALLBACK_MAP.get(final_mood, final_mood)

        with st.spinner('Generating narration...'):
            audio_bytes = generate_audio(text, tts_mood)

        st.markdown('### Narration')
        st.audio(audio_bytes, format='audio/mp3')