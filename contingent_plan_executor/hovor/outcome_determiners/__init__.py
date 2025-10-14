import spacy

## load all of the labels for entities-idk-where-from
#SPACY_LABELS = spacy.load("./training_spacy/gold-standard/entities/").get_pipe("ner").labels
SPACY_LABELS = spacy.load("./training_spacy/banking/entities/").get_pipe("ner").labels

## load entity model
#entity_nlp = spacy.load("./training_spacy/gold-standard/entities/")
entity_nlp = spacy.load("./training_spacy/banking/entities/")

## load intent models and store
intent_nlp = spacy.load("./training_spacy/banking/confirm_intents/")
confirm_intent_nlp = spacy.load("./training_spacy/banking/confirm_intents/")
deny_intent_nlp = spacy.load("./training_spacy/banking/deny_intents/")
share_account_nlp = spacy.load("./training_spacy/banking/share_account_intents/")
share_bill_nlp = spacy.load("./training_spacy/banking/share_bill_intents/")
share_create_nlp = spacy.load("./training_spacy/banking/share_create_intents/")
share_done_nlp = spacy.load("./training_spacy/banking/share_done_intents/")
share_e_transfer_nlp = spacy.load("./training_spacy/banking/share_e_transfer_intents/")
share_request_nlp = spacy.load("./training_spacy/banking/share_request_intents/")
share_transfer_settings_nlp = spacy.load("./training_spacy/banking/share_transfer_settings_intents/")

intent_models = [confirm_intent_nlp,
                 deny_intent_nlp,
                 share_account_nlp,
                 share_bill_nlp,
                 share_create_nlp,
                 share_done_nlp,
                 share_e_transfer_nlp,
                 share_request_nlp,
                 share_transfer_settings_nlp]

"""
intent_nlp = spacy.load("./training_spacy/gold-standard/banking-old-gold-standard-intents/")
confirm_intent_nlp = spacy.load("./training_spacy/gold-standard/confirm_intents/")
deny_intent_nlp = spacy.load("./training_spacy/gold-standard/deny_intents/")
share_all_outing_preferences_intent_nlp = spacy.load("./training_spacy/gold-standard/share_all_outing_preferences_intents/")
share_allergies_intent_nlp = spacy.load("./training_spacy/gold-standard/share_allergies_intents/")
share_budget_intent_nlp = spacy.load("./training_spacy/gold-standard/share_budget_intents/")
share_cuisine_intent_nlp = spacy.load("./training_spacy/gold-standard/share_cuisine_intents/")
share_location_intent_nlp = spacy.load("./training_spacy/gold-standard/share_location_intents/")
share_outing_type_intent_nlp = spacy.load("./training_spacy/gold-standard/share_outing_type_intents/")
share_phone_number_intent_nlp = spacy.load("./training_spacy/gold-standard/share_phone_number_intents/")

intent_models = [confirm_intent_nlp,
                 deny_intent_nlp,
                 share_all_outing_preferences_intent_nlp,
                 share_allergies_intent_nlp,
                 share_budget_intent_nlp,
                 share_cuisine_intent_nlp,
                 share_location_intent_nlp,
                 share_outing_type_intent_nlp,
                 share_phone_number_intent_nlp]
"""