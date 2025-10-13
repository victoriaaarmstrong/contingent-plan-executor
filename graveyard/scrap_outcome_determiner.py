"""
        randomly_selected_outcome_group = random.choice(possible_outcome_groups)
        random_intent = full_outcomes_info[randomly_selected_outcome_group]['intent']

        ## Playing around with Spacy NER
        doc = nlp(input)
        ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]

        ## Playing around with regex outcome determiner
        banking-old-gold-standard-intents = self.banking-old-gold-standard-intents
        #masked_intents = self._mask_intents(banking-old-gold-standard-intents)

        self._regex_providers = {}
        for intent, utterances in banking-old-gold-standard-intents.items():
            self._regex_providers[intent] = self._parse_value_providers(utterances["utterances"])

        # Get the entities-idk-where-from associated with the random intent
        intents_entity_list = self.banking-old-gold-standard-intents[random_intent]["entities-idk-where-from"]

        # Make a data structure that tries to mimic 'r' from before
        r = {"intent_ranking": [
                {"name": random_intent, "confidence": random.random()},
            ],
            "entities-idk-where-from": []
        }

        context_variables = self.context_variables

        # Iterate over all of the entities-idk-where-from and assign values to the variables
        for e in intents_entity_list:
            e = e.replace('$','')

            if context_variables[e]["type"] == 'enum':
                if type(context_variables[e]["config"]) == list:
                    random_value = random.choice(context_variables[e]["config"])
                else:
                    random_value = random.choice(list(context_variables[e]["config"].keys()))

            elif context_variables[e]["type"] == 'json':
                if context_variables[e]["config"]["extraction"]["method"] == 'spacy':

                    if e == "location":
                        random_value = random.choice(["Kingston", "Toronto"])
                    else:
                        random_value = "unsupported_rn"
                elif context_variables[e]["config"]["extraction"]["method"] == 'regex':
                    random_value = self.example_regex_entity(context_variables[e]['config']['extraction']['pattern'])
                else:
                    raise TypeError(
                    "Tried to fill in a json var with an unknown method. Only spacy and regex extraction methods are currently supported.")

            else:
                raise TypeError(
                "Tried to fill in a non-enum or json var. Only enums and jsons are currently supported.")

            r["entities-idk-where-from"].append({
                "entity": e,
                "value": random_value,
            })
        """

## this is getting the intent rankings from the rasa model server, but this is what we want to replace
'''
r = json.loads(
    requests.post(
        "http://localhost:5006/model/parse", json={"text": input}
    ).text
)
'''

## TO DO
# Basic regex extraction so that you can use that for intent recognition and entity extraction
'''
## problem - I don't know what the expected form of r is
# problem solved! This is what it looks like:
# https://rasa.com/docs/reference/api/pro/http-api/#tag/Model/operation/parseModelMessage
'''