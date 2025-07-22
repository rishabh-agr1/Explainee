from transformers import pipeline

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def generate_summary(text, max_length=200):
    if not text.strip():
        return "No content to summarize."

    # Truncate input if too long (approx. 3500 characters ~ 1024 tokens)
    if len(text) > 3500:
        text = text[:3500]

    try:
        summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        return f"Error: {str(e)}"
