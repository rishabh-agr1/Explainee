import spacy
from collections import defaultdict, Counter

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_named_entities(text):
    doc = nlp(text)
    categorized_ents = defaultdict(set)

    for ent in doc.ents:
        categorized_ents[ent.label_].add(ent.text.strip())

    # Convert sets to sorted lists
    return {label: sorted(list(entities)) for label, entities in categorized_ents.items()}

def extract_keywords(text, top_n=10):
    doc = nlp(text.lower())
    words = [
        token.lemma_ for token in doc
        if token.pos_ in ["NOUN", "PROPN", "ADJ"]
        and not token.is_stop
        and not token.is_punct
    ]
    most_common = Counter(words).most_common(top_n)
    return [word for word, _ in most_common]
