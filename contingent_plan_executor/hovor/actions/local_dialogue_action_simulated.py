import random
import re
import rstr
import json

from hovor.actions.local_dialogue_action import LocalDialogueAction

with open("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/local_data/bank_bot/filled_utterance_bank.json", "r") as file:
    AC_DATA = json.load(file)

class LocalDialogueActionSimulated(LocalDialogueAction):
    """Dialogue type of action - simulated version."""

    _apply_message_grouping = False

    def __init__(self, *args):
        super().__init__(*args)
        self.is_external = False
        self._utterance = "HOVOR: " + \
            random.choice(self.config["message_variants"])
        self._utterance = LocalDialogueActionSimulated.replace_pattern_entities(
            self._utterance, self.context)
        # This is used in the process of generating a response
        self.data_for_sim = args[0]['data_for_sim']

    def example_spacy_entity(self, category):
        """
        Since Spacy won't generate a given entity type from nothing,
        I made this function which can generate a random example for
        each category of named entities-idk-where-from.
        """
        examples = {
            "GPE": ['Kingston', 'Toronto'],
            "NORP": ['The Liberal Party of Canada', 'The Conservative Party of Canada'],
            "FAC": ['Toronto Pearson Airport', 'Golden Gate Bridge'],
            "ORG": ['Amazon', "Queen's University"],
            "PERSON": ['Ryan Reynolds', 'Harry Potter'],
            "LOC": ['Africa', 'Mount Everest'],
            "PRODUCT": ['Mazda 3', 'Smartphone'],
            "EVENT": ['Olympic Games', 'Christmas'],
            "WORK_OF_ART": ['Mona Lisa', 'The Starry Night'],
            "LAW": ['The Civil Rights Act', 'The Patriot Act'],
            "LANGUAGE": ['English', 'French'],
            "DATE": ['16th Janurary 2017', 'November 12th'],
            "TIME": ['ten minutes', 'four hours'],
            "PERCENT": ['sixty percent', '20%'],
            "MONEY": ['fifty dollars', '5 cents'],
            "QUANTITY": ['Several kilometers', '60kg'],
            "ORDINAL": ['9th', 'Ninth'],
            "CARDINAL": ['2', 'Three'],
        }
        if category.upper() not in examples:
            return None
        return random.choice(examples[category.upper()])
    
    def example_regex_entity(self, regex):
        """
        This function uses the rstr library to generate a
        random string matching the given regex. 
        """
        
        return rstr.xeger(regex)

    def get_random_value_for_var(self, var_name):
        cv = self.data_for_sim['context_variables'][var_name]
        if cv['type'] == 'enum':
            if type(cv['config']) == list:
                return random.choice(cv['config'])
            return random.choice(list(cv['config'].keys()))
        elif cv['type'] == 'json':
            if cv['config']['extraction']['method'] == 'spacy':
                return self.example_spacy_entity(cv['config']['extraction']['config_method'])
            elif cv['config']['extraction']['method'] == 'regex':
                return self.example_regex_entity(cv['config']['extraction']['pattern'])
            else:
                raise TypeError(
                "Tried to fill in a json var with an unknown method. Only spacy and regex extraction methods are currently supported.")
        else:
            raise TypeError(
                "Tried to fill in a non-enum or json var. Only enums and jsons are currently supported.")

    def fill_dollar_vars(self, s):
        if '$' not in s:
            return s
        # finds the word starting with $ without the $
        var_names = re.findall(r'\$(\w+)', s)
        # get random values for these
        random_var_values = [
            self.get_random_value_for_var(n) for n in var_names]
        # sub them into the string
        for i in range(len(var_names)):
            # only replace the first element incase there are two of same type vars
            s = s.replace('$'+var_names[i], random_var_values[i], 1)
        return s

    def add_additional_context(self, intent_name, amount):
        phrases = [random.choice(AC_DATA[intent_name]["filled_utterances"])]

        try:
            additional_context = random.sample(AC_DATA[intent_name]["possible_ac_intents"], amount)
        except:
            return phrases[0]

        for ac in additional_context:
            phrases += [random.choice(AC_DATA[ac]["filled_utterances"])]

        random.shuffle(phrases)

        final_utterance = ""
        for phrase in phrases:
            final_utterance += " " + phrase

        return final_utterance
    def generate_response_by_data(self):
        """
        A function that picks a random outcome group from self,
        and uses the information in data.json to find an appropriate response.
        It will see if the intent is named directly, otherwise it will look at
        the required entities and select an intent that has those entities.

        This works well and produces a reasonable conversation. It works for banking-old-gold-standard-intents
        which don't have entities-idk-where-from too.
        """
        current_action_name = self.name
        possible_outcomes = self.data_for_sim['actions'][current_action_name]['effect']['outcomes']
        outcome_intent_names = [outcome['intent']
                                for outcome in possible_outcomes]
        possible_intent_names = [
            intent_name for intent_name in outcome_intent_names if self.data_for_sim['intents'][intent_name]['type'] != 'fallback']
        random_outcome_intent_name = random.choice(possible_intent_names)
        if isinstance(random_outcome_intent_name, str):
            # get the intent name and find the intent in data.json
            # randomly pick an utterance
            # use regex to replace variable with random variable from enum values
            # in data.json
            # done
            random_intent = self.data_for_sim['intents'][random_outcome_intent_name]
            if len(random_intent['utterances']) != 0:
                #print(self.add_additional_context(random_outcome_intent_name, 1))
                random_utterance = self.add_additional_context(random_outcome_intent_name, 3) #random.choice(random_intent['utterances'])
                #simulated_input = self.fill_dollar_vars(random_utterance)
            else:
                # must be fallback, there are no utterances for this intent
                simulated_input = "I'm not sure."
        else:
            raise TypeError('Expected the intent to be string.')

        return random_utterance #simulated_input

    def _end_execution_callback(self, action_result, info):
        if self.action_type == "dialogue":
            LocalDialogueAction._apply_message_grouping = False

            simulated_input = self.generate_response_by_data()

            print(f'USER - SIMULATED: {simulated_input}')
            action_result.set_field("input", simulated_input)
        else:
            LocalDialogueAction._apply_message_grouping = True
