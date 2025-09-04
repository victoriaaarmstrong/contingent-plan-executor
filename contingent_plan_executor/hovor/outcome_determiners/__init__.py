import nltk
import spacy
import en_core_web_sm

nltk.download('wordnet')
nltk.download('omw-1.4')
#nltk.download('averaged_perceptron_tagger_eng')
#nltk.download('maxent_ne_chunker_tab')
#nltk.download('words')

SPACY_LABELS = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/entities/").get_pipe("ner").labels
nlp = spacy.load("en_core_web_md")

intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/intents/")
entity_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/entities/")
