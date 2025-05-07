import nltk
import spacy
import en_core_web_sm

nltk.download('wordnet')
nltk.download('omw-1.4')
#nltk.download('averaged_perceptron_tagger_eng')
#nltk.download('maxent_ne_chunker_tab')
#nltk.download('words')

SPACY_LABELS = spacy.load("en_core_web_md").get_pipe("ner").labels
