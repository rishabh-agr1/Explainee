from components.extractor import extract_named_entities

def extract_locations(file_path):
    """
    Extracts and returns a list of GPE (geopolitical) entities from the article.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        article_text = f.read()

    named_entities = extract_named_entities(article_text)
    return sorted(set(named_entities.get("GPE", [])))
