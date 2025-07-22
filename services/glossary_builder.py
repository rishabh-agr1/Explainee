from components.extractor import extract_named_entities
from components.explainer import get_glossary_definitions

def build_glossary(file_path, max_entities=15):
    """
    Extracts PERSON and ORG entities from the article and returns a glossary (up to max_entities terms).
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        article_text = f.read()

    named_entities = extract_named_entities(article_text)
    persons = named_entities.get("PERSON", [])
    orgs = named_entities.get("ORG", [])

    combined = persons + orgs
    top_entities = combined[:max_entities]

    # Partition back to persons and orgs
    filtered_persons = [e for e in top_entities if e in persons]
    filtered_orgs = [e for e in top_entities if e in orgs]

    glossary = get_glossary_definitions(filtered_persons, filtered_orgs)
    return glossary
