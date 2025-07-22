# helper/article_processor.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from components.translation.translator import detect_language, translate_text
from components.translation.language_map import LANGUAGE_CODE_TO_NAME
from services.file_handler import write_temp_file

def fetch_and_process_article(url, translation_enabled=True):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract title
        title = soup.title.string.strip() if soup.title else "No title found"

        # Extract article text
        paragraphs = soup.find_all("p")
        article_text = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

        # Language detection
        detected_lang = detect_language(article_text)
        detected_lang_full = LANGUAGE_CODE_TO_NAME.get(detected_lang, "Unknown")

        translated_text = article_text
        translated = False

        # Translate only if needed and user allowed it
        if translation_enabled and detected_lang != "en":
            translated_text = translate_text(article_text, src_lang=detected_lang, target_lang="en")
            translated = True

        # Save translated or original content to temp file
        temp_file_path = write_temp_file(translated_text)

        # Extract domain
        source = urlparse(url).netloc

        return {
            "title": title,
            "article_text": article_text,
            "translated_text": translated_text,
            "source": source,
            "language_code": detected_lang,
            "language_full": detected_lang_full,
            "translated": translated,
            "temp_file_path": temp_file_path
        }

    except Exception as e:
        raise RuntimeError(f"Error fetching or processing article: {e}")
