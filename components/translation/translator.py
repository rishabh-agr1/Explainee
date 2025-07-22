from googletrans import Translator
from langdetect import detect
from components.translation.language_map import LANGUAGE_MAP

translator = Translator()

def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"

def get_language_name(code):
    return LANGUAGE_MAP.get(code, "Unknown")

def translate_to_english(text, src_lang):
    try:
        if src_lang == "en":
            return text
        result = translator.translate(text, src=src_lang, dest='en')
        return result.text
    except:
        return text  # fallback

def translate_text(text, src_lang, target_lang):
    try:
        if src_lang == target_lang:
            return text
        result = translator.translate(text, src=src_lang, dest=target_lang)
        return result.text
    except:
        return text  # fallback

def translate_text_block(text, dest_lang, src_lang="en"):
    try:
        if dest_lang == src_lang:
            return text
        result = translator.translate(text, src=src_lang, dest=dest_lang)
        return result.text
    except:
        return text
