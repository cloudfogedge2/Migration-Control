"""
    Class representing the Fog Layer, which contains and manages fog nodes in the system.
    The fog layer is responsible for handling nodes that are closer to the users and can provide computational resources.

    Attributes:
        graph (MobilityGraph): The mobility graph representing the current state of the simulation.
        nodes (list): A list of nodes that belong to the fog layer.
"""

from Node import Layer


class FogLayer:
    def __init__(self, graph) -> None:
        """
        Initializes the FogLayer with a reference to the mobility graph.
        
        Args:
            graph (MobilityGraph): The mobility graph used to track and manage fog nodes.
        """
        self.graph = graph
        self.nodes = self.graph.get_moving_fog_nodes()

    def add_node(self, node):
        """
        Adds a new node to the fog layer and assigns its layer to Fog.
        
        Args:
            node (Node): The node to be added to the fog layer.
        """
        node.layer = Layer.Fog
        self.nodes.append(node)

    def get_nodes(self):
        """
        Retrieves the list of nodes currently in the fog layer.
        
        Returns:
            list: A list of nodes in the fog layer.
        """
        return self.nodes
