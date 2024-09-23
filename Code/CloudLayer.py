"""
    Class representing the Cloud Layer! The CloudLayer class manages the cloud nodes. Cloud nodes are typically
    more powerful and are used when fog nodes cannot handle a task.
    This class provides methods to add new cloud nodes and to retrieve the current list of cloud nodes,
    ensuring that tasks have a fallback option when fog resources are insufficient.
"""
from Node import Layer


class CloudLayer:
    def __init__(self) -> None:
        self.nodes = []

    def add_node(self, node):
        node.layer = Layer.Cloud
        self.nodes.append(node)

    def get_nodes(self):
        return self.nodes
