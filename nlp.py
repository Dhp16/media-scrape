import spacy
from collections import Counter

# Load the English NLP model with NER capabilities
# Use a larger model like 'en_core_web_md' or 'en_core_web_lg' for potentially better results
nlp = spacy.load("en_core_web_sm")

def find_org_counts(transcript: str):
    # Process the text with the spaCy model
    doc = nlp(transcript)

    org_counts = Counter()

    for entity in doc.ents:
        # Check if the entity's label is 'ORG' (Organization)
        if entity.label_ == "ORG":
            # Use the entity text as the key and increment the count
            org_counts[entity.text] += 1

    # Print the resulting dictionary
    print("\nOrganization Counts:")
    print(org_counts)

    return org_counts
