from Node import Layer

"""
    UsersLayer class interacts with the MobilityGraph to retrieve information about all user nodes or specific
     ones by their ID. This class abstracts the user layer, making it easier to manage and retrieve user-specific data
     within the system.
"""

from Graph import MobilityGraph


class UsersLayer:
    def __init__(self, graph) -> None:
        self.graph = graph

    def get_nodes(self):
        return self.graph.get_user_nodes()

    def get_nodes_by_id(self, id):
        return self.graph.get_node(id)
