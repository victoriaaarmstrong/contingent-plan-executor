import spacy

## load all of the labels for entities-idk-where-from
#SPACY_LABELS = spacy.load("./training_spacy/gold-standard/entities/").get_pipe("ner").labels
SPACY_LABELS = spacy.load("./training_spacy/banking/entities/").get_pipe("ner").labels
#SPACY_LABELS = spacy.load("./training_spacy/bartender/entities/").get_pipe("ner").labels

## load entity model
#entity_nlp = spacy.load("./training_spacy/gold-standard/entities/")
entity_nlp = spacy.load("./training_spacy/banking/entities/")
#entity_nlp = spacy.load("./training_spacy/bartender/entities/")
"""
intent_nlp = spacy.load("./training_spacy/bartender/share_drink_intents/")
share_drink_nlp = spacy.load("./training_spacy/bartender/share_drink_intents/")
share_glass_nlp = spacy.load("./training_spacy/bartender/share_glass_intents/")
share_liquor_nlp = spacy.load("./training_spacy/bartender/share_liquor_intents/")
share_mixer_nlp = spacy.load("./training_spacy/bartender/share_mixer_intents/")
share_payment_nlp = spacy.load("./training_spacy/bartender/share_payment_intents/")
share_size_nlp = spacy.load("./training_spacy/bartender/share_size_intents/")
share_descriptors_nlp = spacy.load("./training_spacy/bartender/share_descriptors_intents/")

intent_models = [share_drink_nlp,
                 share_glass_nlp,
                 share_liquor_nlp,
                 share_mixer_nlp,
                 share_payment_nlp,
                 share_size_nlp,
                 share_descriptors_nlp]
"""
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
intent_nlp = spacy.load("./training_spacy/gold-standard/confirm_intents/")
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