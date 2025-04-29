import nltk
import spacy
#import en_core_web_sm

nltk.download('wordnet')
nltk.download('omw-1.4')

SPACY_LABELS = spacy.load("en_core_web_md").get_pipe("ner").labels
