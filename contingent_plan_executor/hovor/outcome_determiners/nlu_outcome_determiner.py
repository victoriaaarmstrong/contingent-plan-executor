from dataclasses import dataclass
from typing import Dict
from operator import attrgetter
from hovor.outcome_determiners import SPACY_LABELS
from hovor.outcome_determiners import nlp, intent_nlp, entity_nlp
from hovor.outcome_determiners.outcome_determiner_base import OutcomeDeterminerBase
from hovor.planning.outcome_groups.deterministic_outcome_group import (
    DeterministicOutcomeGroup,
)
from hovor import DEBUG
from hovor.outcome_determiners.random_outcome_determiner import RandomOutcomeDeterminer
import requests
import json
import random
from nltk.corpus import wordnet, stopwords
import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.classify import NaiveBayesClassifier

from typing import Union
from textblob import TextBlob
import re

import rstr
import spacy

@dataclass
class Intent:
    name: str
    entity_reqs: Union[frozenset, None]
    outcome: DeterministicOutcomeGroup
    confidence: float

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.entity_reqs == other.entity_reqs
            and self.outcome == other.outcome
            and self.confidence == other.confidence
        )

    def __lt__(self, other):
        return self.confidence > other.confidence


class NLUOutcomeDeterminer(OutcomeDeterminerBase):
    """Determiner"""

    def __init__(self, action_name, full_outcomes, context_variables, intents):
        self.action_name = action_name
        self.full_outcomes = {outcome["name"]: outcome for outcome in full_outcomes}
        self.context_variables = context_variables
        self.intents = intents
        # cache the extracted entities so we don't have to extract anything multiple times
        self.extracted_entities = {}
        self._regex_providers = []

    @staticmethod
    def parse_synset_name(synset):
        return synset.name().split(".")[0]

    #def find_spacy_entity(self, method: str):
        #if method in self.spacy_entities:
            #if self.spacy_entities[method]:
                #return self.spacy_entities[method].pop()

    def find_spacy_entity(self, entity: str):
        """
        **TODO: REPLACE THIS STUB**

        Return the entity if it exists.

        Create one of these for every extraction type (i.e. spacy) used

        Args:
            entity (str): The entity to retrieve

        Returns:
            Optional[Dict]: The entity, if it exists, or None.
        """
        if entity in self.spacy_entities:
            return self.spacy_entities[entity]

        #raise NotImplementedError("Implement this function.")

    def initialize_extracted_entities(self, entities: Dict):
        """
        **TODO: REPLACE THIS STUB**

        Initialize the entities into their respective categories.
        You want to do this so you can extract entities according to their extraction
        specifications, as well as set "orderings" for extraction types. for example,
        for a "number" entity (with allowed "maybe" knowledge) set to be extracted with
        rasa, it was extracted with rasa, and if that failed an extraction was
        attempted with spacy's "CARDINAL" with the "maybe" knowledge setting.

        Args:
            entities (Dict): The raw entities extracted.
        """
        self.spacy_entities = {}

        for extracted in entities:

            ## We also need spacy not in spacy_labels -- how am I adding this in
            if extracted["entity"] in SPACY_LABELS:
                ## something funky is going on when I'm setting these I think -- the format is off when I'm trying to use it in extract_regex
                if extracted["entity"] in self.spacy_entities:
                    # I think there's something weird going on with these appends
                    self.spacy_entities[extracted["entity"]].append(extracted)
                else:
                    self.spacy_entities[extracted["entity"]] = extracted ## maybe need to remove []
            """
            else:
                if extracted["entity"] in self.randomly_selected_entities:
                    self.randomly_selected_entities[extracted["entity"]].append(extracted)
                    #self.randomly_selected_entities.append(extracted)
                else:
                    self.randomly_selected_entities[extracted["entity"]] = extracted
                #raise NotImplementedError("Implement this.")
            """


    # TODO: replace with general "execute with ordering" function
    def determine_extraction_ordering(self, entity: str):
        """Determines the extraction ordering of the entity based on its
        extraction settings.

        For reference, these were the orderings previously used when Rasa
        was used for NLU (feel free to use these or make your own).
        - if specified to use "spacy":
            - try extracting with spacy, then rasa.
        - if there is no specification (i.e. rasa):
            - try extracting with rasa, then spacy.
        - if it is a regex:
            - try extracting with rasa first and checking the pattern.
              otherwise, try with spacy and checking the pattern against
              any extracted CARDINAL values. (since this extraction is
              different, it has its own function, so specify this with "regex").

        Args:
            entity (str): The name of the entity.

        Returns (List[str]): List of strings that represents the ordering.
        """

        """
        extracted = self.find_randomly_selected_entity(entity)
        if not extracted:
            return None, None
        else:
            certainty = "found"

        return extracted, certainty
        """

        ## YOU CAN HARD CODE This
        return ["spacy", "regex"]

        ## just always do regex for now
        #raise NotImplementedError("Implement this function.")

    # TODO: turn into stub
    def extract_regex(self, entity):
        """For regexes, it doesn't matter whether what extracted it
        ("regex" is its own category). Just try with all relevant extraction methods--
        results will always be "found" or "didnt-find".
        """

        extracted = None

        try:
            pattern = self.context_variables[entity]["config"]["extraction"]["pattern"]
        except:
            pattern = r"\b\w+\s"

        ## Extracted entities is Null here
        # but I think that makes sense if this is the first loop

        ## don't have spacy entities rn, so we can ignore this block, we enter the else
        '''
        if self.spacy_entities:
            if "CARDINAL" in self.spacy_entities:
                # iterate through all CARDINAL entities and see if any match
                for ext_ent in self.spacy_entities["CARDINAL"]:
                    match = re.fullmatch(pattern, ext_ent["value"])
                    if match:
                        extracted = ext_ent
                        break
            else:
                return None
        '''

        if self.spacy_entities: #self.randomly_selected_entities:
            for ext_ent in self.spacy_entities: #self.randomly_selected_entities:
                ## this is what spacy_entities looks like: {'OUTING_TYPE':[{'entity':'OUTING_TYPE', 'value':'fun'}]}

                match = re.fullmatch(pattern, self.spacy_entities[ext_ent]["value"])#self.randomly_selected_entities[ext_ent]["value"])

                if match:
                    extracted = ext_ent
                    break

        else:
            ## I need the value, not the entity to extract here
            match = re.fullmatch(pattern, entity)


        if match:
            extracted = entity
            certainty = 1.0

            #raise NotImplementedError( "Search other extraction types for numbers we \can check against the regex (optional).")
        return extracted, certainty

    def extract_spacy(self, entity: str):
        extracted = self.find_spacy_entity(entity.upper()
            # I don't know if this will always work, may need a try catch for enum versus json
            #self.context_variables[entity].upper() #["config"]["extraction"]["spacy"]
        )

        if not extracted:
            ## this is where you might want to try another method
            return None, None
        else:
            certainty = "found"

        return extracted, certainty


    def extract_entity(self, entity: str):
        """Extract an entity according to the extraction ordering.

        Args:
            entity (str): The name of the entity.

        Returns:
            Optional[Dict]: Contains the extraction information if extracted;
                otherwise None.
        """
        if self.context_variables[entity]["type"] == "json":
            method = self.context_variables[entity]["config"]["extraction"]["method"]

            if method == "spacy":
                extracted, certainty = self.extract_spacy(entity)
            elif method == "regex":
                extracted, certainty = self.extract_regex(entity)

        ## this is if it is enum
        else:
            extracted, certainty = self.extract_spacy(entity)

        if extracted:

            return {
                "extracted": extracted,
                "value": extracted["value"],
                "certainty": certainty,
            }

        """
        ordering = self.determine_extraction_ordering(entity)

        for i in range(len(ordering)):
            # attempt to extract the entity
            if ordering[i] == "regex":
                extracted = self.extract_regex(entity)
            ## Need to change this specifically for random
            elif ordering[i] == "spacy":

                ## this is not the right input
                extracted = self.context_variables[entity]["config"]["extraction"][
                        "config_method"
                    ].upper()
                    #self.find_spacy_entity(entity)
            else:
                raise NotImplementedError("Implement this.")

            ## But we will enter this
            if extracted:
                # certainty won't be "known" if we didn't extract with our first pick
                # ignore this with regexes though (don't really care where we get it
                # from as long as we get a match)
                
                if ordering[i] == "regex":
                    certainty = "known"#"found"
                else:
                    if i == 0:
                        certainty = "known" #"found"
                    else:
                        certainty = "known" #"maybe-found"
                
                
                        ## Unknown
                certainty = ("known" if i == 0 else "maybe-known") \
                             if ordering != "regex" else "known"
                break
        """


    def extract_entities(self, intent):
        """Attempts to extract all entities from an intent.

        Args:
            intent (Intent): The intent to extract from.

        Returns:
            Dict: The entities extracted.
        """
        entities = {}
        # get entity requirements

        # iterate through all of the intent requirements
        for entity in {f[0] for f in intent.entity_reqs}:
            if entity in self.extracted_entities:
                entities[entity] = self.extracted_entities[entity]
            else:
                # raw extract single entity, then validate
                extracted_info = self.extract_entity(entity)

                if extracted_info:
                    extracted_info = self._make_entity_type_sample(
                        entity,
                        self.context_variables[entity]["type"],
                        self.context_variables[entity]["config"],
                        extracted_info,
                    )
                    if extracted_info["sample"] != None:
                        entities[entity] = extracted_info

                    self.extracted_entities[entity] = extracted_info

        return entities

    def filter_intents(self, r, outcome_groups):
        """Filters the intents based on the entities extracted.
        We do this because we don't want to waste computation validating an intent
        if any of the entities it needs were not extracted in any capacity and it
        will ultimately be thrown out.

        Note that we only look at the raw extractions in this step.

        Args:
            r (Dict): The JSON response from the NLU call
            outcome_groups (List): The outcome groups for this action (these determine
                which intents are in our scope).

        Returns:
            (List[Intent]): The list of filtered Intents to attempt extractions from.
        """
        # make outcome groups accessible by name
        outcome_groups = {out.name: out for out in outcome_groups}
        intents_detected = {
            ranking["name"]: ranking["confidence"] for ranking in r["intent_ranking"]
        }

        intents = []

        for out, out_cfg in self.full_outcomes.items():
            # check to make sure this intent was at least DETECTED
            intent_name = out_cfg["intent"] ## now you can replace nonsense

            if intent_name in intents_detected:

                if self.intents[intent_name]["entities"]:
                    # we only want to consider assignments that are variables of the
                    # intent, as outcomes often have other updates for existing entities.
                    entity_reqs = {
                        e[1:]: cert
                        for e, cert in out_cfg["assignments"].items()
                        if e in self.intents[out_cfg["intent"]]["entities"]
                    }

                    intents.append(
                        Intent(
                            name = out_cfg["intent_cfg"]
                            if "intent_cfg" in out_cfg
                            else out_cfg["intent"],
                            # use the assignments key so we get the required certainty
                            # for each entity
                            entity_reqs = frozenset(entity_reqs.items()),
                            outcome = outcome_groups[out],
                            confidence = intents_detected[intent_name],
                        )
                    )
                else:
                    intents.append(
                        Intent(
                            name = intent_name,
                            entity_reqs = None,
                            outcome = outcome_groups[out],
                            confidence = intents_detected[intent_name],
                        )
                    )
            elif out_cfg["intent"] == "fallback":
                intents.append(Intent("fallback", None, outcome_groups[out], 0))

            ## put an else fail and spit a bunch of stuff out

        ## high confidence is earlier on in the list
        intents.sort()

        return intents

    def extract_intents(self, intents):
        """Extracts the intents by iterating through the filtered intents and selecting
        the first one where all entities are extracted correctly.

        Args:
            intents (List[Intents]): The filtered intents.

        Returns:
            intents (List[Intents]): The intent ranking, adjusted by the updated
                confidences.
        """

        ## you've already sorted it so it'll go through most to least confidence, this then finds the first one

        extracted_intent = None

        for intent in intents:
            # if this intent expects entities, make sure we extract them
            if intent.entity_reqs != None:

                entities = self.extract_entities(intent)

                if intent.entity_reqs == frozenset(
                    {entity: entities[entity]["certainty"]
                        for entity in entities
                        if entities[entity]["certainty"] != "didnt-find"
                    }.items()
                ):
                    extracted_intent = intent
                    break ## because of this, other might have non-zero confidences

                # need to reassign to None because we only get here if for some reason we weren't
                # able to extract the intent correctly
                extracted_intent = None
                # an intent with entities we were not able to extract gets a confidence of 0
                intent.confidence = 0 ## slam confidence to 0
            else:
                # stop looking for a suitable intent if the intent extracted doesn't require entities
                extracted_intent = intent
                break
        if extracted_intent:
            # in the case that there are multiple intents with the same name and confidence
            # because we're going by entity assignment, we only want the intent that reflects
            # our extracted entity assignment to be chosen. i.e. at this point, an intent share_cuisine where
            # cuisine is "found" and the sister intent share_cuisine where cuisine is "maybe-found" will
            # have the same confidence, but we only want the right one to be chosen.
            for intent in intents:
                if (
                    intent.name == extracted_intent.name
                    and intent.entity_reqs != extracted_intent.entity_reqs
                ):
                    intent.confidence = 0

        ## silent failure, what happens if you haven't?

        for intent in intents:
            if intent.name == "fallback":
                intent.confidence = (
                    1 - max(intents, key=attrgetter("confidence")).confidence
                )
                break
        ## guarantee that the one that you matched and broke for because you already sorted and zero-ed out everything
        ## add the sort back
        intents.sort()

        return intents


    ## From Jacob's code to randomly generate an example regex value
    def example_regex_entity(self, regex):
        """
        This function uses the rstr library to generate a
        random string matching the given regex.
        """

        return rstr.xeger(regex)

    def mask_utterance(self, utterance):
        return re.sub(r'\$([a-zA-Z_]+)', r'(?P<\1>.+)', utterance)
        #return re.sub(r"\$\w+", "something", utterance)
        #return re.sub("(\[regex\]\{[^}]*\})", " something ", utterance)

    def extract_values(self, patterns, input_sentence):
        for pattern in patterns:
            match = re.fullmatch(pattern, input_sentence)
            if match:
                return {k: v.strip() for k, v in match.groupdict().items() if v}
        return {}

    def match_intent_from_entities(self, requirements, extracted_values):
        for intent, reqs in requirements.items():
            # Check if all required entities are in values
            if all(entity in extracted_values for entity in reqs):
                return intent
        return 'fallback'  # default if no match

    def get_raw_rankings(self, input, outcome_groups):
        """Gets the raw intent rankings given the user input.

        Args:
            input (str): The user utterance.
            outcome_groups (List): The outcome groups for this action (these determine
                which intents are in our scope).

        Returns:
            intents (List[Intents]): The intent ranking.
        """
        ## Just testing to see what spacy says at each time step...
        spacy_intent_doc = intent_nlp(input)
        spacy_ents_doc = entity_nlp(input)

        labeled_ents = [(ent.text, ent.label_) for ent in spacy_ents_doc.ents]
        #print(labeled_ents)

        #print(f"What spacy got: {max(spacy_intent_doc.cats, key=spacy_intent_doc.cats.get)}, {[(ent.text, ent.label_) for ent in spacy_ents_doc.ents]}.")

        """
        ## Get the intents first to play around with extracting stuff with regex
        possible_outcome_groups = []
        for out in outcome_groups:
            possible_outcome_groups.append(out.name)

        full_outcomes_info = self.full_outcomes

        ## for all possible outcomes, get the intent names to make a list of all of the utterances and all of the entity requirements
        dummy_intents = {}
        for out in possible_outcome_groups:
            info = full_outcomes_info[out]
            dummy_intents.update({info['intent'] : info['entity_requirements']})

        intents = self.intents

        ## now that we have all of the possible intents from the outcomes, I want to get all of the utterances for each of those intents
        utterances_to_check = []
        for intent, utterances in intents.items():
            if intent in dummy_intents:
                utterances_to_check += utterances["utterances"]

        patterns = [self.mask_utterance(u) for u in utterances_to_check]

        values = self.extract_values(patterns, input)

        ## Something for confirm and deny intents
        confirm_utterances = intents['confirm']['utterances']
        deny_utterances = intents['deny']['utterances']
                                                        #deny] else "neither"
        if len(values) != 0:
            selected_intent = self.match_intent_from_entities(dummy_intents, values)

        else:
            ## Replace with something to see if it's confirm or deny in a more dynamic way
            if input.lower() in [c.lower() for c in confirm_utterances]:
                selected_intent = "confirm"
            elif input.lower() in [d.lower() for d in deny_utterances]:
                selected_intent = "deny"
            else:
                selected_intent = "fallback"

        ## This is what had matched the original rasa extraction
        r = {"intent_ranking": [
            {"name": selected_intent, "confidence": 0.99},
        ],
            "entities": []
        }
        """

        ## create an r datastructure to match what rasa had been giving us
        r = {"intent_ranking": [],
            "entities": []
        }

        ## fill in the spacy-detected intents
        for key, value in spacy_intent_doc.cats.items():
            r["intent_ranking"].append({
                "name": key,
                "confidence": value
            })

        ## fill in the spacy-detected entities
        for entity_tuple in labeled_ents:
            r["entities"].append({
                "entity": entity_tuple[1],
                "value": entity_tuple[0],
            })

        """
        for key, value in values.items():
            r["entities"].append({
                "entity": key,
                "value": value,
            })
        """

        intents = self.filter_intents(r, outcome_groups)
        self.initialize_extracted_entities(r["entities"])
        return self.extract_intents(intents)

    def rank_groups(self, outcome_groups, progress):
        """Ranks the outcome groups and updates the progress.

        Args:
            outcome_groups (List): The outcome groups for this action (these determine
                which intents are in our scope).
            progress (OutcomeDeterminationProgress): Keeps track of the context.

        Raises:
            ValueError: Raised if you tried to assign an entity to a value we don't have yet

        Returns:
            List[tuple]: The ranked outcome groups.
            OutcomeDeterminationProgress: The updated progress.
        """
        intents = self.get_raw_rankings(
            progress.json["action_result"]["fields"]["input"], outcome_groups
        )

        chosen_intent = intents[0]
        ranked_groups = [(intent.outcome, intent.confidence) for intent in intents]
        # entities required by the extracted intent
        if chosen_intent.entity_reqs:
            ci_ent_reqs = [er[0] for er in chosen_intent.entity_reqs]
        # note we shouldn't only add samples for extracted entities; some outcomes don't
        # extract entities themselves but update the values of existing entities

        for update_var, update_config in progress.get_description(
            chosen_intent.outcome.name
        )["updates"].items():
            if "value" in update_config:
                if progress.get_entity_type(update_var) in ["json", "enum"]:
                    value = update_config["value"]

                    # if value is not null
                    if value:

                        # if the value is a variable (check without the $)
                        if value[1:] in progress.actual_context.field_names:
                            value = value[1:]
                            if progress.actual_context._fields[value]:
                                value = progress.actual_context._fields[value]
                            else:
                                # if it is not part of the progress yet and we just extracted entities,
                                if chosen_intent.entity_reqs:
                                    # check if we just extracted it
                                    if value in ci_ent_reqs:
                                        value = self.extracted_entities[value]["sample"]
                                    # otherwise, we tried to assign an entity to a value we don't have yet
                                    else:
                                        raise ValueError(
                                            "Tried to assign an entity to \
                                                        an unknown variable value."
                                        )
                    progress.add_detected_entity(update_var, value)

        DEBUG("\t top random ranking for group '%s'" % (chosen_intent.name))

        return ranked_groups, progress

    def _make_entity_type_sample(
        self, entity, entity_type, entity_config, extracted_info
    ):
        """Extracts the actual value of the entity.
        Fixes spelling errors if they exist and attempts to map it to similar words
        if it is not an exact match to the entity configuration.

        Args:
            entity (str): Name of the entity.
            entity_type (str): Type of the entity.
            entity_config (Dict): The possible values for the entity.
            extracted_info (Dict): The raw extraction data for the entity.

        Raises:
            NotImplementedError: Raised if we tried to sample from an unknown entity
            type.

        Returns:
            (Dict): The extraction info for the entity.
        """
        entity_value = extracted_info["value"]

        # entity is extracted with spacy and has options specified
        spacy_w_opts = (
            (
                entity_config["extraction"]["method"] == "spacy"
                and "options" in entity_config
            )
            if entity_type == "json"
            else False
        )

        ## will need to update this to handle location case?
        if type(entity_config) != list:
            variations = []
            for entity, details in entity_config.items():
                #print(details['variations'])
                #config = details.get("config", {})
                #if "options" in config:  # the 'location' style
                    #for option in config["options"].values():
                        #entity_config += [option.get("variations", [])]
                #else:  # the 'outing_type' style
                variations += details["variations"]

            entity_config = variations

        if spacy_w_opts:
            entity_config = entity_config["options"]
        if spacy_w_opts or entity_type == "enum":
            # lowercase all strings in entity_config, map back to original casing
            entity_config = {e.lower(): e for e in entity_config}
            entity_value = entity_value.lower()

            if entity_value in entity_config:
                extracted_info["sample"] = entity_config[entity_value]
                return extracted_info
            else:
                ## never going to enter this loop because we have known not found
                if "known" in self.context_variables[entity]:
                    if self.context_variables[entity]["known"]["type"] == "fflag":
                        extracted_info["certainty"] = "maybe-found"
                        # first try correcting spelling
                        spell_corrected_e_val = (
                            TextBlob(entity_value).correct().raw.lower()
                        )
                        if spell_corrected_e_val != entity_value:
                            entity_value = spell_corrected_e_val

                            if entity_value in entity_config:
                                extracted_info["sample"] = entity_config[entity_value]
                                return extracted_info

                        # as a last ditch effort, try to use wordnet to decipher what the user meant
                        for syn in wordnet.synsets(entity_value):
                            for option in entity_config:
                                if option in syn._definition.lower():
                                    extracted_info["sample"] = entity_config[option]
                                    return extracted_info
                            for lemma in syn.lemmas():
                                for p in lemma.pertainyms():
                                    p = p.name().lower()
                                    if p in entity_config:
                                        extracted_info["sample"] = entity_config[p]
                                        return extracted_info
                                for d in lemma.derivationally_related_forms():
                                    d = d.name().lower()
                                    if d in entity_config:
                                        extracted_info["sample"] = entity_config[d]
                                        return extracted_info
                            for hyp in syn.hypernyms():
                                hyp = NLUOutcomeDeterminer.parse_synset_name(
                                    hyp
                                ).lower()
                                if hyp in entity_config:
                                    extracted_info["sample"] = entity_config[hyp]
                                    return extracted_info
                            for hyp in syn.hyponyms():
                                hyp = NLUOutcomeDeterminer.parse_synset_name(
                                    hyp
                                ).lower()
                                if hyp in entity_config:
                                    extracted_info["sample"] = entity_config[hyp]
                                    return extracted_info
                            for hol in syn.member_holonyms():
                                hol = NLUOutcomeDeterminer.parse_synset_name(
                                    hol
                                ).lower()
                                if hol in entity_config:
                                    extracted_info["sample"] = entity_config[hol]
                                    return extracted_info
                            for hol in syn.root_hypernyms():
                                hol = NLUOutcomeDeterminer.parse_synset_name(
                                    hol
                                ).lower()
                                if hol in entity_config:
                                    extracted_info["sample"] = entity_config[hol]
                                    return extracted_info
        elif entity_type == "json":
            # note: regex would have been checked already, and for spacy w/o options specified just
            # set the entity value
            extracted_info["sample"] = entity_value
            return extracted_info
        else:
            raise NotImplementedError("Cant sample from type: " + entity_type)

        extracted_info["certainty"] = "didnt-find"
        extracted_info["sample"] = None

        return extracted_info

    """
    def _report_entities(self, response, progress):
        super()._report_entities(response, progress)

        for intent_info in response['intents']:
            intent = intent_info["intent"]

            for provider in self._regex_providers.get(intent, []):
                updates = provider(progress.action_result.get_field("input"))
                for entity_name, entity_value in updates.items():
                    progress.add_detected_entity(entity_name, entity_value)

    def _parse_value_providers(self, utterances):
        value_providers = []
        for utterance in utterances:
            value_provider = self._parse_value_provider(utterance)
            value_providers.append(value_provider)

        return value_providers
   
    def _parse_value_provider(self, utterance):
        matchers = []

        for groups in re.findall(r"(\$\w+)|([^\$]+)+", utterance):#"(\[regex\]\{[^}]*\})|([^\[\{]+)+", utterance):
            regex = groups[0]
            text = groups[1]

            if regex:
                match = re.search(r"\(\s*'([^']*)'\s*,\s*'([^']*)'\s*\)", regex)#"\{([^:]+):=([^}]+)\}", regex)

                if match == None:
                    pass
                else:
                    target = match.group(1)
                    pattern = match.group(2)
                    matchers.append((target, pattern))
            else:
                if text.strip() == "":
                    continue

                matchers.extend(text.split(' '))

        def value_provider(input):
            collected_values = {}

            current_input = input.split(' ')
            for matcher in matchers:
                if isinstance(matcher, str):
                    if len(current_input) and current_input[0].lower() == matcher.lower():
                        current_input.pop(0)
                else:
                    regex_input = " ".join(current_input)
                    target_var, regex_pattern = matcher
                    match = re.search(regex_pattern, regex_input)

                    if not match:
                        continue

                    value = match.group(0)
                    collected_values[target_var] = value

                    # remove the recognized part and continue for case multiple regexes is defined
                    regex_input = regex_input[0:match.span(0)[0]] + regex_input[match.span(0)[1]:]
                    current_input = regex_input.split(' ')

            return collected_values

        return value_provider

    def _mask_intents(self, intents):
        masked_intents = {}
        for intent, utterances in intents.items():
            masked_intents[intent] = masked_utterances = []
            for utterance in utterances['utterances']:
                masked_utterance = self._mask_utterance(utterance)
                masked_utterances.append(masked_utterance)

        return masked_intents

    """