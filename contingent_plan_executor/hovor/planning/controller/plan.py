from hovor.actions.action_base import ActionBase
from hovor.planning.plan_base import PlanBase


class Plan(PlanBase):
    """
    Plan that selects next node according to node connections coming from the planner.
    It does not look at partial state matching quality.
    """

    def __init__(self, nodes, edges, domain):
        super(Plan, self).__init__(domain)
        self._nodes = list(nodes)
        self._edges = list(edges)

        # create some indexes for fast node lookups
        self._node_id_to_node = {}
        for node in self._nodes:
            self._node_id_to_node[node.node_id] = node

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    def get_initial_node(self):
        """Finds initial state in the plan"""
        for node in self._nodes:
            if node.is_initial:
                return node

        return None

    def get_node_from_id(self, nid):
        return self._node_id_to_node[nid]

    def get_children(self, node):
        children = []
        for edge in self._edges:
            if edge.src == node:
                children.append(edge.dst)

        return children

    def atomify(self, entities):

        ## Need a better way of knowing when to add know etc to these
        atoms = []

        no_update_list = ["goal", "have-message", "force-statement"]

        for key, value in entities.items():
            ## if we have a general statement
            if ("allow" in key) or (key in no_update_list) or ("forcing" in key):
                ## don't have a value
                if (value == None) or (value == False):
                    atoms += ['NegatedAtom ' + key + '()']
                ## do have a value
                else:
                    atoms += ['Atom ' + key + '()']
            elif ("conflict" in key):
                ## don't have value
                if (value == None):
                    atoms += ['NegatedAtom ' + key + '()']
                    atoms += ['NegatedAtom know__' + key + '()']
                ## the value is False
                elif (value == False):
                    atoms += ['NegatedAtom ' + key + '()']
                    atoms += ['Atom know__' + key + '()']
                ## the value is True
                else:
                    atoms += ['Atom ' + key + '()']
                    atoms += ['Atom know__' + key + '()']
            elif ("have_" in key):
                ## don't have value
                if (value == None):
                    atoms += ['NegatedAtom ' + key + '()']
                    atoms += ['NegatedAtom know__' + key + '()']
                ## the value is False
                elif (value == False):
                    atoms += ['NegatedAtom ' + key + '()']
                    atoms += ['Atom know__' + key + '()']
                ## the value is True
                else:
                    atoms += ['Atom ' + key + '()']
                    atoms += ['Atom know__' + key + '()']
            ## it's specific to the problem and needs a "know"
            else:
                ## we don't have a value so we don't know it
                if value == None:
                    maybe_atom = 'NegatedAtom maybe-know__' + key + '()'
                    know_atom = 'NegatedAtom know__' + key + '()'
                    atoms += [maybe_atom, know_atom]
                ## we know the value so we do know it
                else:
                    maybe_atom = 'NegatedAtom maybe-know__' + key + '()'
                    know_atom = 'Atom know__' + key + '()'
                    atoms += [maybe_atom, know_atom]

        return set(atoms)

    def update_cs(self, entity_values, complete_state):
        updated_complete_state = []

        for ev in entity_values:
            print(ev)

        for state in complete_state:
            print(state)

        return updated_complete_state
    def get_next_node(self, current_node, outcome_name, complete_state): #next_state, outcome_name):


        ## I think next_state here is actually the current state, based on the usage in in_memory_session.py
        ## So that means it's our /cs potentially? Must confirm, and also confirm that it's being updated correctly
        ## That being said, you CAN iterate over all of the nodes and check if the cs entails it's ps
        ## You will want to be sure that you're not selecting fall back?

        """
        print(complete_state_fluents)
        print(current_node.partial_state.fluents)

        print(current_node.node_id)

        for node in self._nodes:
            print(f"Is node {node.node_id}'s ps entailed by the cs? {complete_state.entails(node._partial_state)}")
            print(f"Is it the goal node? {node.is_goal}")
            print(f"Is it the initial node? {node.is_initial}")


        print(self._nodes)
        print(f"What is current node?: {type(current_node)}")
        print(f"What is current node._partial_state?: {type(current_node._partial_state)}")
        print(f"Is our current node semantically entailed by the complete state? {current_node._partial_state.entails(current_node._partial_state)}")
        """
        ## maybe I don't want to atomify here, maybe I want the cs and then augment it with something true?
        atoms = self.atomify(complete_state.__dict__['_fields'])

        candidates = []
        for child_name, child in current_node.named_children:
            if outcome_name == child_name:
                candidates.append(child)

        if len(candidates) == 0:
            raise AssertionError("Invalid state transition detected.")

        if len(candidates) > 1:
            raise AssertionError("Partial states are ambiguous.")

        candidate = candidates[0]

        new_EM_candidates = {}
        for node in self.nodes:
            node_fluents = set(node.partial_state.fluents)
            #print(f"missing fluents: {node_fluents - (node_fluents.intersection(atoms))}")
            if node_fluents.issubset(atoms):
                new_EM_candidates.update({node:node._distance})

        sorted_EM_candidates = dict(sorted(new_EM_candidates.items(), key=lambda x: x[1]))

        if len(new_EM_candidates) == 0:
                raise AssertionError("No node possible")
        else:
            first_key, first_value = next(iter(sorted_EM_candidates.items()))
            return first_key
            ## return the first node -- we've sorted it so we don't have to worry about splitting it further

        ## Checking that things are working as they should
        #candidate_fluents = set(candidate.partial_state.fluents)
        #print(f"\t{candidate_fluents.issubset(atoms)}")
        #print(f"missing nodes = {candidate_fluents - (candidate_fluents.intersection(atoms))}")
        # todo prp output semantic changed probably, entails is not ensured
        # if not next_state.entails(candidate.partial_state):
        #    raise AssertionError("Next state does not entail the candidate")

        #return candidate


