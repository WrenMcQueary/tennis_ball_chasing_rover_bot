"""Definition of a directed graph for a deterministic finite state machine.
"""


from typing import Set, List, Callable, Union


class Transition:
    """Transition edge between 2 nodes."""

    def __init__(self, symbol: str, node_destination_name: str) -> None:
        """:param symbol: the name of the symbol that causes this transition.
        :param node_destination_name: the name of the destination node
        """
        self.symbol = symbol
        self.node_destination_name = node_destination_name


class Node:
    """Node with a name and a list of transitions."""

    def __init__(self, name: str, transitions: Set[Transition], func: Callable) -> None:
        """:param name: the name of the node
        :param transitions: all Transition objects pointing *away* from the node
        :param func: the helper function that should be called while this node is active.  func must return a transition symbol (ie string).
        """
        self.name = name
        self.transitions = transitions
        self.func = func


class DFSM:
    """Deterministic finite state machine."""

    def __init__(self, nodes: List[Node], active_node: Node) -> None:
        """:param nodes: all nodes in the finite state machine
        :param active_node: the node currently being executed upon
        """
        self.nodes = nodes
        self.active_node = active_node

    def traverse_symbol(self, symbol: str) -> None:
        """Based on the DFSM's active node and the argument symbol, change the active node to whatever the symbol points
        to.
        :param symbol: the symbol of a single transition
        """
        # Transition to the new node.
        for transition in self.active_node.transitions:
            if transition.symbol == symbol:
                self.active_node = transition.node_destination_name
                return None
        # If we reach this part of the code, then the node was not found.  Raise an error.
        raise RuntimeError("no node to transition to from node " + self.active_node.name + " on transition symbol " + symbol)

    def run_dfsm(self) -> None:
        """Begin running the DFSM.  Repeatedly call the function of the active state, then transition based on the
        symbol returned.
        """
        while True:
            # Call the function of the active state and save the transition symbol it returns
            print("Running " + str(self.active_node.func) + "...")
            transition_symbol = self.active_node.func()
            print(transition_symbol)
            # State-transition based on the symbol returned
            self.traverse_symbol(transition_symbol)