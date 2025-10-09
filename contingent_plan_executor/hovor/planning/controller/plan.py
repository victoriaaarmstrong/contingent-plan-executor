from hovor.actions.action_base import ActionBase
from hovor.planning.plan_base import PlanBase
from hovor.planning.partial_state import PartialState

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

    def basic_atomify(self, entities):

        atoms = []

        only_known_entities = {k: v for k, v in entities.items() if v is not None}

        for key, value in only_known_entities.items():
            know_atom = 'Atom know__' + key + '()'
            atoms += [know_atom]

        return set(atoms)


    def get_next_node(self, next_state, outcome_name):


        candidates = []
        for child_name, child in next_state.named_children:
            if outcome_name == child_name:
                candidates.append(child)

        if len(candidates) == 0:
            raise AssertionError("Invalid state transition detected.")

        if len(candidates) > 1:
            raise AssertionError("Partial states are ambiguous.")

        candidate = candidates[0]

        # todo prp output semantic changed probably, entails is not ensured
        # if not next_state.entails(candidate.partial_state):
        #    raise AssertionError("Next state does not entail the candidate")

        return candidate


    def get_better_node(self, progress):

        ## translate context to a ps
        fluents = PartialState(self.basic_atomify(progress.actual_context.__dict__['_fields']))
        updated_complete_states = progress.actual_state.update_by(fluents)

        ## build a list of possible candidates if they are a subset of the complete_state
        new_EM_candidates = {}
        for node in self.nodes:
            node_fluents = set(node.partial_state.fluents)
            #print(f"missing fluents: {node_fluents - (node_fluents.intersection(atoms))}")
            if node_fluents.issubset(set(updated_complete_states.fluents)):
                new_EM_candidates.update({node:node._distance})

        ## sort based on distance value so that the first is the closest (i.e. lowest distance)
        sorted_EM_candidates = dict(sorted(new_EM_candidates.items(), key=lambda x: x[1]))

        ## return our better node -- if our current node is the better node, it will get returned in the else
        if len(new_EM_candidates) == 0:
            return None
        else:
            ## return the first node -- we've sorted it so we don't have to worry about splitting it further, we know it's closest
            first_key, first_value = next(iter(sorted_EM_candidates.items()))
            return first_key
