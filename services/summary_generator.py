from components.summarizer import generate_summary
from services.file_handler import read_temp_file

def summarize_article(file_path):
    """
    Reads the translated article text from a temporary file and generates a summary.
    """
    try:
        article_text = read_temp_file(file_path)
        return generate_summary(article_text)
    except Exception as e:
        return f"❌ Error generating summary: {e}"
