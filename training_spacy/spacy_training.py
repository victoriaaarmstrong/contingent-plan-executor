import random
import re
import spacy
import pandas as pd

from spacy.training.example import Example
from spacy.util import minibatch

def prep_intent_data(data):

    df = pd.read_excel(data)
    intents = df.columns[1:]

    formatted_data = []

    for index, row in df.iterrows():
        utterance = row['utterance'].strip('"')
        cats = {intent: float(row[intent]) for intent in intents}
        formatted_data.append((utterance, {"cats": cats}))

    return intents, formatted_data

def prep_entity_data(data):

    return

def train_ner_model(data_path):

    return


def train_intent_model(data_path):

    intents, data = prep_intent_data(data_path)

    nlp = spacy.load("en_core_web_sm")

    if "textcat" not in nlp.pipe_names:
        textcat = nlp.add_pipe("textcat", last=True)
    else:
        textcat = nlp.get_pipe("textcat")

    for intent in intents:
        textcat.add_label(intent)

    optimizer = nlp.begin_training()

    # make it quieter?
    nlp.remove_pipe("lemmatizer")
    nlp.remove_pipe("attribute_ruler")

    for i in range(250):  # epochs
        random.shuffle(data)
        losses = {}
        batches = minibatch(data, size=2)

        for batch in batches:
            examples = []
            for text, annotations in batch:
                doc = nlp.make_doc(text)  # create Doc without running full pipeline
                examples.append(Example.from_dict(doc, annotations))

            nlp.update(
                examples,
                sgd=optimizer,
                losses=losses
            )

        if i % 50 == 0:
            print(f"Losses at iteration {i}: {losses}")

    return nlp

nlp = train_intent_model("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/intent_data.xlsx")

## figure out how to save it to load it in again

doc = nlp("I have a high budget.")
print(doc.cats)