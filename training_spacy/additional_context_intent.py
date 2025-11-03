import random
import json
import pandas as pd

def add_additional_context(data, intent_name, amount):
    phrases = [random.choice(data[intent_name]["filled_utterances"])]

    try:
        additional_context = random.sample(data[intent_name]["possible_ac_intents"], amount)
    except:
        return phrases[0]

    for ac in additional_context:
        phrases += [random.choice(data[ac]["filled_utterances"])]

    random.shuffle(phrases)

    final_utterance = ""
    for phrase in phrases:
        final_utterance += " " + phrase

    return final_utterance

def add_additional_context_excluding_intent(data, forbidden_intent_name, amount):
    possible_intents = set(data.keys()) - {forbidden_intent_name}
    random_intent = random.choice(list(possible_intents))
    phrases = [random.choice(data[random_intent]["filled_utterances"])]

    if amount != 0:
        other_intents = list(set(data[random_intent]["possible_ac_intents"]) - {forbidden_intent_name})
        additional_context = random.sample(other_intents, amount)
    else:
        return phrases[0]

    for ac in additional_context:
        phrases += [random.choice(data[ac]["filled_utterances"])]

    random.shuffle(phrases)

    final_utterance = ""
    for phrase in phrases:
        final_utterance += " " + phrase

    return final_utterance
def construct_intent_file(file_name, out_file, primary_intent):

    with open(file_name, "r") as file:
        ac_data = json.load(file)

    df = pd.DataFrame(columns=["utterance", primary_intent, "fallback"])

    for i in range(20):
        utterance_none = add_additional_context(ac_data, primary_intent, 0)
        utterance_one = add_additional_context(ac_data, primary_intent, 1)
        utterance_two = add_additional_context(ac_data, primary_intent, 2)

        new_df = pd.DataFrame([[utterance_none, 1, 0], [utterance_one, 1, 0], [utterance_two, 1, 0]], columns=df.columns)

        df = pd.concat([df, new_df], ignore_index=True)

    for j in range(60):
        utterance_f_none = add_additional_context_excluding_intent(ac_data, primary_intent, 0)
        utterance_f_one = add_additional_context_excluding_intent(ac_data, primary_intent, 1)
        utterance_f_two = add_additional_context_excluding_intent(ac_data, primary_intent, 2)

        new_f_df = pd.DataFrame([[utterance_f_none, 0, 1], [utterance_f_one, 0, 1], [utterance_f_two, 0, 1]], columns=df.columns)

        df = pd.concat([df, new_f_df], ignore_index=True)


    df.to_excel(out_file + ".xlsx", index=False)

    return

construct_intent_file("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/local_data/bartender_bot/filled_utterance_bank.json",
                      "./training_spacy/bartender/share_descriptors_intent_data",
                      "share_descriptors")
