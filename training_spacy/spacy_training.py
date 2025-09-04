import random
import re
import spacy
import pandas as pd

from spacy.training.example import Example
from spacy.util import minibatch
from spacy.language import Language

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

    df = pd.read_excel(data)
    df = df.fillna('')
    entities = df.columns[2:]

    formatted_data = []

    for index, row in df.iterrows():
        utterance = row['utterance'].strip('"')
        values = row['values'].split(",")

        if row['entities']:

            if "(" not in values[0]:

                for value in values:
                    value = value.replace(" ", "")
                    start = utterance.index('$')
                    end = start + len(value)

                    formatted_data.append((utterance.replace("$", value), {'entities': [(start, end, row['entities'])]}))

            else:
                for value in values:

                    value = value.replace("(", "")
                    value = value.replace(")", "")
                    value_tuple = value.split(" ")

                    value_1 = value_tuple[0]
                    value_2 = value_tuple[1]
                    entities = row['entities'].split(",")

                    entity_1 = entities[0]
                    start_1 = utterance.index('$1')
                    end_1 = start_1 + len(value_1)

                    ## need to split it up this way or else our indices are wrong
                    temp = (utterance.replace("$1", value_1))

                    start_2 = temp.index('$2')
                    end_2 = start_2 + len(value_2)
                    entity_2 = entities[1]

                    formatted_data.append((temp.replace("$2", value_2), {'entities': [(start_1, end_1, entity_1), (start_2, end_2, entity_2)]}))

        else:
            formatted_data.append((utterance, {'entities': []}))

    return entities, formatted_data

def train_ner_model(data_path):

    entities, data = prep_entity_data(data_path)

    nlp = spacy.load("en_core_web_sm")

    nlp.vocab.vectors.name = 'example_model_training'  # give a name to our list of vectors

    ner = nlp.get_pipe("ner")

    for entity in entities:
        ner.add_label(entity)

    optimizer = nlp.resume_training()

    # Training loop
    for i in range(250):
        losses = {}
        for text, annotations in data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], sgd=optimizer, losses=losses)

        if i % 50 == 0:
            print(f"Losses at iteration {i}: {losses}")

    return nlp


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

def train_custom():
    print("Training Intent Model...")
    nlp_1 = train_intent_model("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/intent_data.xlsx")
    nlp_1.to_disk("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/intents/")

    #print("\nTraining NER Model...")
   # nlp_2 = train_ner_model("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/entity_data.xlsx")
   # nlp_2.to_disk("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/entities/")

    return

train_custom()

"""
intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/intents/")
entity_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/entities/")

test_text = "I want to go to a relaxing place and I am operating within a high budget."

intent_doc = intent_nlp(test_text)
print(max(intent_doc.cats, key=intent_doc.cats.get))

entity_doc = entity_nlp(test_text)
print([(ent.text, ent.label_) for ent in entity_doc.ents])
"""
