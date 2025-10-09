from dataclasses import dataclass
from typing import Dict
from operator import attrgetter
from hovor.outcome_determiners import SPACY_LABELS
from hovor.outcome_determiners import intent_nlp, intent_models, entity_nlp #, model
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
import llm

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


class SpacyDynamicOutcomeDeterminer(OutcomeDeterminerBase):
    """Determiner"""

    def __init__(self, action_name, full_outcomes, context_variables, intents):
        self.action_name\
            = action_name
        self.full_outcomes = {outcome["name"]: outcome for outcome in full_outcomes}
        self.context_variables = context_variables
        self.intents = intents
        # cache the extracted entities so we don't have to extract anything multiple times
        self.extracted_entities = {}
        self._regex_providers = []

    @staticmethod
    def parse_synset_name(synset):
        return synset.name().split(".")[0]

    def find_spacy_entity(self, entity: str):
        """
        Return the entity if it exists.

        Create one of these for every extraction type (i.e. spacy) used

        Args:
            entity (str): The entity to retrieve

        Returns:
            Optional[Dict]: The entity, if it exists, or None.
        """
        if entity in self.spacy_entities:
            return self.spacy_entities[entity]

    def initialize_extracted_entities(self, entities: Dict):
        """
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

            if extracted["entity"] in SPACY_LABELS:
                if extracted["entity"] in self.spacy_entities:
                    self.spacy_entities[extracted["entity"]].update(extracted)
                else:
                    self.spacy_entities[extracted["entity"]] = extracted
            else:
                raise AssertionError("We managed to extract an entity that Spacy doesn't recognize")

    # TODO: turn into stub
    def extract_regex(self, entity):
        """For regexes, it doesn't matter whether what extracted it
        ("regex" is its own category). Just try with all relevant extraction methods--
        results will always be "found" or "didnt-find".
        """

        extracted = None
        certainty = None

        try:
            pattern = self.context_variables[entity]["config"]["extraction"]["pattern"]
        except:
            pattern = r"\b\w+\s"

        if self.spacy_entities:
            for ext_ent in self.spacy_entities:
                match = re.fullmatch(pattern, self.spacy_entities[ext_ent]["value"])

                if match:
                    extracted = ext_ent
                    break

        else:
            match = re.fullmatch(pattern, entity)

        if match:
            extracted = {'entity': entity, 'value': match[0]}
            certainty = "found"

        return extracted, certainty

    def extract_spacy(self, entity: str):
        extracted = self.find_spacy_entity(entity.upper()
            # I don't know if this will always work, may need a try catch for enum versus json
            #self.context_variables[entity].upper() #["config"]["extraction"]["spacy"]
        )

        if not extracted:
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
                extracted, certainty = self.extract_regex(entity)#self.extract_spacy(entity)

        ## this is if it is enum
        else:
            extracted, certainty = self.extract_spacy(entity)

        if extracted:

            return {
                "extracted": extracted,
                "value": extracted["value"],
                "certainty": certainty,
            }


    def extract_entities(self, intent):
        """Attempts to extract all entities from an intent.

        Args:
            intent (Intent): The intent to extract from.

        Returns:
            Dict: The entities extracted.
        """
        entities = {}
        # get entity requirements

        ## updated version where I actually iterate over all possible entities to add what has been updated
        for entity in self.context_variables.keys():

        # this is the original where I want to iterate through all of the intent requirements
        #for entity in {f[0] for f in intent.entity_reqs}:
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

                ## The difference here is we change it from strict equality to subset
                if intent.entity_reqs.issubset(frozenset(
                    {entity: entities[entity]["certainty"]
                        for entity in entities
                        if entities[entity]["certainty"] != "didnt-find"
                    }.items()
                )):
                    extracted_intent = intent
                    break ## because of this, other might have non-zero confidences
                else:
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
                if intent.entity_reqs == None:
                    pass
                elif (
                    intent.name == extracted_intent.name
                    #and intent.entity_reqs != extracted_intent.entity_reqs
                    and (intent.entity_reqs.issubset(extracted_intent.entity_reqs) == False)
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

        intents.sort()

        return intents

    def get_raw_rankings(self, input, outcome_groups):
        """Gets the raw intent rankings given the user input.

        Args:
            input (str): The user utterance.
            outcome_groups (List): The outcome groups for this action (these determine
                which intents are in our scope).

        Returns:
            intents (List[Intents]): The intent ranking.
        """
        predicted_intents = []
        for nlp in intent_models:
            doc = nlp(input)
            predicted_intents += [doc.cats]

        spacy_ents_doc = entity_nlp(input)

        labeled_ents = [(ent.text, ent.label_) for ent in spacy_ents_doc.ents]

        ## create an r datastructure to match what rasa had been giving us
        r = {"intent_ranking": [],
            "entities": []
        }

        ## fill in the spacy-detected intents -- no longer sums to 0!
        for pred_i in predicted_intents:
            for key, value in pred_i.items():
                if key != "fallback":
                    r["intent_ranking"].append({
                        "name": key,
                        "confidence": value,
                    })

        ## fill in the spacy-detected entities
        for entity_tuple in labeled_ents:
            r["entities"].append({
                "entity": entity_tuple[1],
                "value": entity_tuple[0],
            })

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

        already_updated = []
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
                    already_updated += [update_var]
                    progress.add_detected_entity(update_var, value)

        ## this might cause problems as we progress so subsequent states because this continuously gets updated
        for entity in self.spacy_entities.keys():
            if entity.lower() not in already_updated:
                progress.add_extra_entity(entity.lower(), self.spacy_entities[entity]['value'])

        #DEBUG("\t top random ranking for group '%s'" % (chosen_intent.name))

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

        ## if we have options/variations for our entity
        spacy_w_opts = False
        if type(entity_config) != list and entity_type != "json":
            spacy_w_opts = True

        ## adjust the possible options and sort things into the appropriate master category if we have variations
        if spacy_w_opts:
            try:
                categories = entity_config["options"]
                entity_config = entity_config["options"]
            except:
                categories = entity_config

            for key, value in categories.items():
                if entity_value in value["variations"]:
                    entity_value = key

        ## now we can make the sample types with the propety formatted configs & values
        if spacy_w_opts or entity_type == "enum":
            # lowercase all strings in entity_config, map back to original casing
            entity_config = {e.lower(): e for e in entity_config}
            entity_value = entity_value.lower()

            if entity_value in entity_config:
                extracted_info["sample"] = entity_config[entity_value]
                return extracted_info
            else:
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
                                hyp = SpacyDynamicOutcomeDeterminer.parse_synset_name(
                                    hyp
                                ).lower()
                                if hyp in entity_config:
                                    extracted_info["sample"] = entity_config[hyp]
                                    return extracted_info
                            for hyp in syn.hyponyms():
                                hyp = SpacyDynamicOutcomeDeterminer.parse_synset_name(
                                    hyp
                                ).lower()
                                if hyp in entity_config:
                                    extracted_info["sample"] = entity_config[hyp]
                                    return extracted_info
                            for hol in syn.member_holonyms():
                                hol = SpacyDynamicOutcomeDeterminer.parse_synset_name(
                                    hol
                                ).lower()
                                if hol in entity_config:
                                    extracted_info["sample"] = entity_config[hol]
                                    return extracted_info
                            for hol in syn.root_hypernyms():
                                hol = SpacyDynamicOutcomeDeterminer.parse_synset_name(
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
