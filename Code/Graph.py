"""
    MobilityGraph class representing the mobility graph used in the simulation.
    This graph tracks the movement of nodes (e.g., vehicles, fog nodes) over time and updates their positions accordingly.

    Attributes:
        nodes (list): A list of nodes currently in the graph.
        graph (dict): A dictionary mapping time steps to nodes' positions.
        xml_path (str): Path to the XML file containing static vehicle data.
        mobile_xml_path (str): Path to the XML file containing mobile fog node data.
        task_file_path (str): Path to the XML file containing task data.
        fixed_fog_node_file_path (str): Path to the XML file containing fixed fog node data.
        zone_file_path (str): Path to the XML file containing zone data.

    Methods:
        init_graph(): Initializes the graph by parsing XML files.
        update_graph(): Updates the graph by moving to the next time step.
        get_tasks(): Retrieves tasks from the task file.
        get_fixed_fog_node(): Retrieves fixed fog nodes from the XML file.
        get_zones(): Retrieves zones from the XML file.
        get_user_nodes(): Retrieves user nodes currently in the graph.
        get_moving_fog_nodes(): Retrieves moving fog nodes currently in the graph.
        get_node(node_id): Retrieves a specific node by its ID.
"""

from SumoXMLParser import SumoXMLParser
from Clock import Clock
from Node import Layer


class MobilityGraph:
    def __init__(self, xml_path, mobile_xml_path, task_file_path, fixed_fog_node_file_path, zone_file_path) -> None:
        """
        Initializes the MobilityGraph with the paths to various XML files.

        Args:
            xml_path (str): Path to the XML file containing static vehicle data.
            mobile_xml_path (str): Path to the XML file containing mobile fog node data.
            task_file_path (str): Path to the XML file containing task data.
            fixed_fog_node_file_path (str): Path to the XML file containing fixed fog node data.
            zone_file_path (str): Path to the XML file containing zone data.
        """
        self.nodes = []
        self.graph = {}
        self.xml_path = xml_path
        self.mobile_xml_path = mobile_xml_path
        self.task_file_path = task_file_path
        self.fixed_fog_node_file_path = fixed_fog_node_file_path
        self.zone_file_path = zone_file_path
        self.init_graph()

    def init_graph(self):
        """
        Initializes the graph by parsing the XML files and setting up the initial state.
        """
        parser = SumoXMLParser(file_path=self.xml_path, mobile_file_path=self.mobile_xml_path,
                               task_file_path=self.task_file_path,
                               fixed_fog_node_file_path=self.fixed_fog_node_file_path,
                               zone_file_path=self.zone_file_path)
        self.graph = parser.parse()
        Clock.time = min(self.graph.keys())
        self.nodes = self.graph[Clock.time]

    def update_graph(self):
        """
        Updates the graph to the next time step and moves nodes accordingly.

        Returns:
            list: A list of nodes after updating their positions.
        """
        Clock.time += 1
        new_nodes = self.graph[Clock.time]
        for node in self.nodes:
            new_node = next((n for n in new_nodes if n.id == node.id), None)
            if new_node is not None:
                node.x = new_node.x
                node.y = new_node.y
                node.angle = new_node.angle
                node.speed = new_node.speed
        return self.nodes

    def get_tasks(self):
        parser = SumoXMLParser(file_path=self.xml_path, mobile_file_path=self.mobile_xml_path,
                               task_file_path=self.task_file_path,
                               fixed_fog_node_file_path=self.fixed_fog_node_file_path,
                               zone_file_path=self.zone_file_path)
        return parser.parse_task()

    def get_fixed_fog_node(self):
        parser = SumoXMLParser(file_path=self.xml_path, mobile_file_path=self.mobile_xml_path,
                               task_file_path=self.task_file_path,
                               fixed_fog_node_file_path=self.fixed_fog_node_file_path,
                               zone_file_path=self.zone_file_path)
        return parser.parse_fixed_fog_node()

    def get_zones(self):
        parser = SumoXMLParser(file_path=self.xml_path, mobile_file_path=self.mobile_xml_path,
                               task_file_path=self.task_file_path,
                               fixed_fog_node_file_path=self.fixed_fog_node_file_path,
                               zone_file_path=self.zone_file_path)
        return parser.parse_zone()

    def get_user_nodes(self):
        return [node for node in self.nodes if node.layer == Layer.Users]

    def get_moving_fog_nodes(self):
        return [node for node in self.nodes if node.layer == Layer.Fog]

    def get_node(self, node_id):
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
