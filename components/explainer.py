import wikipedia
import re

def is_trivial(term):
    if re.fullmatch(r"\d+([a-zA-Z]*)?", term):
        return True
    if term.lower() in {
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "january", "february", "march", "april", "may", "june", "july", "august",
        "september", "october", "november", "december", "us", "uk", "india", "president", "document"
    }:
        return True
    if len(term.strip()) <= 2 and not term.isupper():
        return True
    return False

def get_glossary_definitions(persons, orgs):
    glossary = {}
    for term in persons + orgs:
        if is_trivial(term):
            continue
        try:
            summary = wikipedia.summary(term, sentences=2)
            glossary[term] = summary  # ✅ Only include when a valid summary is returned
        except (wikipedia.DisambiguationError, wikipedia.PageError, Exception):
            continue  # ❌ Skip ambiguous or missing or error terms
    return glossary
