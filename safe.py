import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from services.language_service import handle_language_pipeline
from services.summary_generator import summarize_article
from services.location_extractor import extract_locations
from services.glossary_builder import build_glossary
from services.file_handler import write_temp_file, delete_temp_file

# Streamlit UI Setup
st.set_page_config(page_title="Explainee — News Article Explainer")
st.title("🧠 Explainee — News Article Explainer")

# URL input
url = st.text_input("🔗 Enter a news article URL:")

if url:
    try:
        with st.spinner("🔄 Fetching and processing article..."):
            # Step 1: Fetch the article
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")

            title = soup.title.string if soup.title else "No title found"
            st.subheader("📰 Title")
            st.write(title)

            source = urlparse(url).netloc
            st.markdown(f"📍 **Source:** `{source}`")

            paragraphs = soup.find_all("p")
            article_text = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

            # Step 2: Language detection + translation
            lang_code, lang_name, translated_path, was_translated = handle_language_pipeline(article_text)

            st.markdown(f"🌐 Detected Language: `{lang_code}` — {lang_name}" +
                        (" | Translated to English" if was_translated else ""))

        # Step 3: Toggle language view
        show_english = st.radio(
            "🈯 View processed content in:",
            options=["Original Language", "English"],
            index=1 if was_translated else 0
        )

        # Read both contents
        original_path = write_temp_file(article_text)
        with open(translated_path, 'r', encoding='utf-8') as f_en, open(original_path, 'r', encoding='utf-8') as f_orig:
            english_content = f_en.read()
            original_content = f_orig.read()

        st.subheader("📄 Full Article")
        with st.expander(f"Click to read the article in {'English' if show_english == 'English' else lang_name}"):
            content_to_show = english_content if show_english == "English" else original_content
            for para in content_to_show.split("\n\n"):
                st.markdown(
                    f"<p style='text-align: justify; line-height: 1.6; margin-bottom: 1em;'>{para.strip()}</p>",
                    unsafe_allow_html=True,
                )

        # Step 4: Summary (always in English)
        with st.spinner("✍ Generating summary..."):
            summary = summarize_article(translated_path)

        st.subheader("📝 Summary")
        st.write(summary)

        # Step 5: Extract GPE (locations)
        locations = extract_locations(translated_path)
        if locations:
            st.subheader("🌍 Locations Mentioned")
            st.write(", ".join(locations))

        # Step 6: Glossary
        st.subheader("📖 Glossary (Top 15 People & Organizations)")
        with st.spinner("📚 Building glossary..."):
            glossary = build_glossary(translated_path, max_entities=15)

        if glossary:
            for term, definition in glossary.items():
                with st.spinner(f"📖 Loading: {term}..."):
                    st.markdown(f"**{term}**: {definition}")
        else:
            st.info("No glossary-worthy entities found.")

        # Cleanup
        delete_temp_file(translated_path)
        delete_temp_file(original_path)

    except Exception as e:
        st.error(f"❌ Failed to process the article: {e}")
