from components.translation.translator import detect_language, get_language_name, translate_to_english
from services.file_handler import write_temp_file

def handle_language_pipeline(article_text):
    """
    Detects language, translates to English (if needed), and writes the result to a temp file.
    Returns:
        - language_code
        - language_name
        - translated_path
        - was_translated (bool)
    """
    lang_code = detect_language(article_text)
    lang_name = get_language_name(lang_code)

    was_translated = lang_code != "en"
    translated_text = translate_to_english(article_text, lang_code) if was_translated else article_text
    translated_path = write_temp_file(translated_text)

    return lang_code, lang_name, translated_path, was_translated
