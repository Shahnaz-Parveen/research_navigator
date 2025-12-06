import spacy

nlp = None

def load_model():
    global nlp
    if nlp is None:
        print("Loading spaCy model...")
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading model...")
            from spacy.cli import download
            download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    """
    Extracts entities from text using spaCy and simple rules.
    Returns a list of tuples: (text, label)
    """
    load_model()
    doc = nlp(text)
    
    entities = []
    
    # 1. Standard spaCy entities
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PERSON', 'GPE', 'DATE', 'EVENT']:
            entities.append((ent.text, ent.label_))
            
    # 2. Custom Rule-based extraction (Simulation for now)
    # In a real scenario, we would train a custom NER model.
    keywords = {
        'METHOD': ['Neural Network', 'Deep Learning', 'Transformer', 'CNN', 'RNN', 'LSTM', 'SVM', 'Algorithm'],
        'TASK': ['Classification', 'Regression', 'Segmentation', 'Detection'],
        'METRIC': ['Accuracy', 'F1 Score', 'Precision', 'Recall'],
        'DATASET': ['ImageNet', 'COCO', 'MNIST', 'CIFAR']
    }
    
    lower_text = text.lower()
    for label, terms in keywords.items():
        for term in terms:
            if term.lower() in lower_text:
                # Find the actual case in text if possible, or just use title case
                start = lower_text.find(term.lower())
                if start != -1:
                    original_text = text[start:start+len(term)]
                    entities.append((original_text, label))
                    
    # Deduplicate based on text
    unique_entities = {}
    for text, label in entities:
        if text not in unique_entities:
            unique_entities[text] = label
            
    return list(unique_entities.items())

def generate_summary(text, num_sentences=3):
    """
    Generates a simple extractive summary by scoring sentences based on word frequency.
    """
    load_model()
    doc = nlp(text)
    
    # Calculate word frequencies (excluding stop words)
    word_frequencies = {}
    for token in doc:
        if not token.is_stop and not token.is_punct:
            word_frequencies[token.text] = word_frequencies.get(token.text, 0) + 1
            
    # Normalize frequencies
    max_freq = max(word_frequencies.values()) if word_frequencies else 1
    for word in word_frequencies:
        word_frequencies[word] /= max_freq
        
    # Score sentences
    sentence_scores = {}
    for sent in doc.sents:
        for word in sent:
            if word.text in word_frequencies:
                if sent not in sentence_scores:
                    sentence_scores[sent] = word_frequencies[word.text]
                else:
                    sentence_scores[sent] += word_frequencies[word.text]
                    
    # Select top N sentences
    import heapq
    summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    return " ".join([sent.text for sent in summary_sentences])
