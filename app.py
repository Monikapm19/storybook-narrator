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
st.write('Upload a storybook page (image) or a PDF to hear it narrated with matching emotion.')

st.markdown('---')

uploaded_file = st.file_uploader(
    'Choose a file',
    type=['jpg', 'jpeg', 'png', 'pdf'],
    help='Supports JPG, PNG, or PDF storybook pages'
)


def show_explanation(explanation, final_mood):
    """Displays a transparent breakdown of why a mood was chosen."""
    with st.expander("ℹ️ Why was this mood chosen?"):
        st.write(
            f"**Image** contributed **{explanation['img_contribution_pct']}%** "
            f"(predicted *{explanation['img_mood']}*)."
        )
        if explanation['matched_keywords']:
            keywords_str = ', '.join(f'"{w}"' for w in explanation['matched_keywords'])
            st.write(
                f"**Text** contributed **{explanation['text_contribution_pct']}%** "
                f"(predicted *{explanation['text_mood']}*, triggered by words like {keywords_str})."
            )
        else:
            st.write(
                f"**Text** contributed **{explanation['text_contribution_pct']}%** "
                f"(predicted *{explanation['text_mood']}*)."
            )
        if explanation.get('special_label'):
            st.info(
                f"🎭 Detected narrative contrast: **{explanation['special_label'].upper()}** "
                f"(image and text convey opposing emotional tones)"
            )
        elif explanation['conflict']:
            st.warning(
                f"⚠️ Image and text disagreed — the system resolved this by trusting "
                f"the more confident signal, choosing **{final_mood}**."
            )
        else:
            st.info("✅ Image and text agreed on the mood.")


if uploaded_file:
    st.caption(f"📄 {uploaded_file.name} — {uploaded_file.size / 1024:.1f} KB")

    is_pdf = uploaded_file.name.lower().endswith('.pdf')

    if is_pdf:
        pdf = fitz.open(stream=uploaded_file.read(), filetype='pdf')
        uploaded_file.seek(0)
        total_pages = len(pdf)

        st.info(f"This PDF has **{total_pages} pages**. Choose the story range below — "
                f"skip title/author/copyright pages and only narrate the actual story.")

        col1, col2 = st.columns(2)
        with col1:
            start_page = st.number_input('Start page', min_value=1, max_value=total_pages, value=1)
        with col2:
            end_page = st.number_input('End page', min_value=1, max_value=total_pages, value=total_pages)

        if start_page > end_page:
            st.error('Start page must be less than or equal to end page.')
            st.stop()

        preview_img = load_as_image(uploaded_file, page_number=start_page - 1)
        uploaded_file.seek(0)
        page_display = st.empty()
        page_display.image(preview_img, caption=f'Page {start_page} of {total_pages}', width='stretch')

    else:
        image = load_as_image(uploaded_file, page_number=0)
        st.image(image, caption='Uploaded Page', width='stretch')

    narrate_clicked = st.button('🎙️ Narrate', use_container_width=True)

    if narrate_clicked:
        combined_audio = b''
        full_text_display = []

        if is_pdf:
            page_range = range(start_page - 1, end_page)
            progress_bar = st.progress(0, text='Starting narration...')
            results_area = st.container()

            for i, page_idx in enumerate(page_range):
                uploaded_file.seek(0)
                page_image = load_as_image(uploaded_file, page_number=page_idx)

                # "Turn the page" — update the same image placeholder in place
                page_display.image(
                    page_image,
                    caption=f'📖 Now narrating — Page {page_idx + 1} of {total_pages}',
                    width='stretch'
                )

                progress_bar.progress(
                    (i + 1) / len(page_range),
                    text=f'Processing page {page_idx + 1} of {end_page}...'
                )

                text = extract_text(page_image)
                if not text or len(text.strip()) < 3:
                    continue  # skip blank/illustration-only pages

                img_mood, img_score = get_image_mood(page_image)
                text_mood, text_score, sentence_emotions = get_text_mood(text)
                final_mood, explanation = fuse_moods(img_mood, img_score, text_mood, text_score, text)

                audio_bytes = generate_audio(text, final_mood)
                combined_audio += audio_bytes

                full_text_display.append(f"**Page {page_idx + 1}** ({final_mood}): {text}")

                with results_area:
                    st.markdown(f"**Page {page_idx + 1} — Mood: {final_mood.upper()}**")
                    show_explanation(explanation, final_mood)

            progress_bar.empty()
            page_display.image(preview_img, caption=f'Finished — showing page {start_page}', width='stretch')

        else:
            with st.spinner('Reading the page...'):
                text = extract_text(image)

            img_mood, img_score = get_image_mood(image)
            text_mood, text_score, sentence_emotions = get_text_mood(text)
            final_mood, explanation = fuse_moods(img_mood, img_score, text_mood, text_score, text)

            combined_audio = generate_audio(text, final_mood)
            full_text_display.append(f"**Mood: {final_mood}**: {text}")

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
            show_explanation(explanation, final_mood)

        st.markdown('---')
        st.markdown('### Extracted Story Text')
        st.text_area(
            'Full extracted text',
            '\n\n'.join(full_text_display),
            height=250,
            disabled=True,
            label_visibility='collapsed'
        )

        st.markdown('### Narration')
        st.audio(combined_audio, format='audio/mp3')