import random
import re
import spacy
import pandas as pd
import ast
import itertools

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
    entity_labels = df.columns[2:]

    df['values'] = df['values'].dropna().apply(ast.literal_eval)
    filled_sentences = []
    formatted_data = []

    for index, row in df.iterrows():
        utterance = row['utterance'].strip('"')
        values = row['values']

        if row['entities']:
            keys = list(values.keys())

            for combo in itertools.product(*[values[k] for k in keys]):
                sentence = utterance
                entities = []

                for k, v in zip(keys, combo):
                    # find where the placeholder is in the sentence
                    start = sentence.index(k)
                    end = start + len(v)

                    # replace the placeholder with the value
                    sentence = sentence[:start] + v + sentence[start + len(k):]

                    # grab the entity label from your row['entities'] dict
                    #print(k)
                    #label = row['entities'][k]
                    entities.append((start, end, k))

                filled_sentences += [sentence]
                formatted_data.append((sentence, {"entities": entities}))

        else:
            formatted_data.append((utterance, {'entities': []}))

    #for sentence in filled_sentences:
        #print(sentence)

    return entity_labels, formatted_data

def old_prep_entity_data(data):

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

def train_custom_intent(data_path, storage_path):
    print("Training Intent Model...")
    nlp_1 = train_intent_model(data_path)
    nlp_1.to_disk(storage_path)
    return

def train_custom_entity(data_path, storage_path):
    print("\nTraining NER Model...")
    nlp_2 = train_ner_model(data_path)
    nlp_2.to_disk(storage_path)

    return

"""
## Train All Intent Models
train_custom_intent("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/confirm_intent_data.xlsx",
                    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/confirm_intents/")

train_custom_intent("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/deny_intent_data.xlsx",
                    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/deny_intents/")

train_custom_intent(
    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_all_outing_preferences_intent_data.xlsx",
    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_all_outing_preferences_intents/")

## high losses for this guy -- check!!
train_custom_intent(
    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_allergies_intent_data.xlsx",
    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_allergies_intents/")

train_custom_intent("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_budget_intent_data.xlsx",
                    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_budget_intents/")

train_custom_intent("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_cuisine_intent_data.xlsx",
                    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_cuisine_intents/")

train_custom_intent(
    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_location_intent_data.xlsx",
    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_location_intents/")

train_custom_intent(
    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_outing_type_intent_data.xlsx",
    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_outing_type_intents/")

train_custom_intent(
    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_phone_number_intent_data.xlsx",
    "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_phone_number_intents/")

#"/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/entity_data.xlsx")
#"/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/entities/")
"""

"""
test_text = "My phone number is 6139216005. I have a low budget and would prefer a fun atmosphere. "

confirm_intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/confirm_intents/")
confirm_intent_doc = confirm_intent_nlp(test_text)
print("confirm:")
print(f"\t{confirm_intent_doc.cats}")
print(f"\t{max(confirm_intent_doc.cats, key=confirm_intent_doc.cats.get)}")

deny_intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/deny_intents/")
deny_intent_doc = deny_intent_nlp(test_text)
print("deny:")
print(f"\t{deny_intent_doc.cats}")
print(f"\t{max(deny_intent_doc.cats, key=deny_intent_doc.cats.get)}")

share_all_outing_preferences_intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_all_outing_preferences_intents/")
share_all_outing_preferences_intent_doc = share_all_outing_preferences_intent_nlp(test_text)
print("share_all_outing_preferences:")
print(f"\t{share_all_outing_preferences_intent_doc.cats}")
print(f"\t{max(share_all_outing_preferences_intent_doc.cats, key=share_all_outing_preferences_intent_doc.cats.get)}")

share_allergies_intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_allergies_intents/")
share_allergies_intent_doc = share_allergies_intent_nlp(test_text)
print("share_allergies:")
print(f"\t{share_allergies_intent_doc.cats}")
print(f"\t{max(share_allergies_intent_doc.cats, key=share_allergies_intent_doc.cats.get)}")

share_budget_intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_budget_intents/")
share_budget_intent_doc = share_budget_intent_nlp(test_text)
print("share_budget:")
print(f"\t{share_budget_intent_doc.cats}")
print(f"\t{max(share_budget_intent_doc.cats, key=share_budget_intent_doc.cats.get)}")

share_cuisine_intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_cuisine_intents/")
share_cuisine_intent_doc = share_cuisine_intent_nlp(test_text)
print("share_cuisine:")
print(f"\t{share_cuisine_intent_doc.cats}")
print(f"\t{max(share_cuisine_intent_doc.cats, key=share_cuisine_intent_doc.cats.get)}")

share_location_intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_location_intents/")
share_location_intent_doc = share_location_intent_nlp(test_text)
print("share_location:")
print(f"\t{share_location_intent_doc.cats}")
print(f"\t{max(share_location_intent_doc.cats, key=share_location_intent_doc.cats.get)}")

share_outing_type_intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_outing_type_intents/")
share_outing_type_intent_doc = share_outing_type_intent_nlp(test_text)
print("share_outing_type:")
print(f"\t{share_outing_type_intent_doc.cats}")
print(f"\t{max(share_outing_type_intent_doc.cats, key=share_outing_type_intent_doc.cats.get)}")

share_phone_number_intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/gold-standard/share_phone_number_intents/")
share_phone_number_intent_doc = share_phone_number_intent_nlp(test_text)
print("share_phone_number:")
print(f"\t{share_phone_number_intent_doc.cats}")
print(f"\t{max(share_phone_number_intent_doc.cats, key=share_phone_number_intent_doc.cats.get)}")
"""

"""
intent_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/banking/intents/")
entity_nlp = spacy.load("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/training_spacy/banking/entities/")

test_text = "I am located in Kingston."

intent_doc = intent_nlp(test_text)
print(max(intent_doc.cats, key=intent_doc.cats.get))

entity_doc = entity_nlp(test_text)
print([(ent.text, ent.label_) for ent in entity_doc.ents])
"""
