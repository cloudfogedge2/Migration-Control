"""
    The SumoXMLParser class is responsible for parsing XML files.
    These files contain data on vehicles (representing users and fog nodes), tasks, and zones.
    The parser extracts this data and formats it for use in the system, enabling the simulation to start with accurate,
    real-world-like data on node positions, movements, and tasks.
"""
import xml.etree.ElementTree as ET
import Node
from Config import Config
from ZoneManagerQLearning import ZoneManagerQlearning
from ZoneManagerRandom import ZoneManagerRandom
from ZoneManagerHeuristic import ZoneManagerHeuristic
from ZoneManagerA3C import ZoneManagerA3C


class SumoXMLParser:
    def __init__(self, file_path, mobile_file_path, task_file_path, fixed_fog_node_file_path, zone_file_path):
        self.filepath = file_path
        self.mobileFilepath = mobile_file_path
        self.taskFilePath = task_file_path
        self.zoneFilePath = zone_file_path
        self.fixedFogNodeFilePath = fixed_fog_node_file_path

    def parse(self):
        tree = ET.parse(self.filepath)
        root = tree.getroot()
        # vehicles is a mapping from time to a list of vehicles
        vehicles = {}
        self.get_vehicles(root, vehicles)

        tree = ET.parse(self.mobileFilepath)
        root = tree.getroot()
        self.get_vehicles(root, vehicles)
        return vehicles

    def get_vehicles(self, root, vehicles):
        for timestep in root.findall('timestep'):
            time = float(timestep.get('time'))
            for vehicle in timestep.findall('vehicle'):
                vehicle_id = vehicle.get('id')
                x = float(vehicle.get('x'))
                y = float(vehicle.get('y'))
                speed = float(vehicle.get('speed'))
                angle = float(vehicle.get('angle'))
                if time not in vehicles:
                    vehicles[time] = []
                type = vehicle.get('type')

                if type == 'mobileFog':
                    # vehicles[time].append(
                    node = Node.Node(
                        vehicle_id,
                        Node.Layer.Fog,
                        x=x,
                        y=y,
                        speed=speed,
                        angle=angle,
                        # coverage_radius=Config.FOG_COVERAGE_RADIUS,
                    )
                    if vehicle.get('power'):
                        node.power = float(vehicle.get('power'))
                    if vehicle.get('coverage_radius'):
                        node.coverage_radius = float(vehicle.get('coverage_radius'))
                    vehicles[time].append(node)
                else:
                    vehicles[time].append(Node.Node(
                        id=vehicle_id,
                        layer=Node.Layer.Users,
                        x=x,
                        y=y,
                        speed=speed,
                        angle=angle
                    ))

    def parse_task(self):
        tree = ET.parse(self.taskFilePath)
        root = tree.getroot()
        task_data = []
        for task in root.findall('task'):
            name = task.get('name')
            creation_time = float(task.get('creation_time'))
            deadline = float(task.get('deadline'))
            power_needed = float(task.get('power_needed'))
            size = float(task.get('size'))
            creator = task.get('creator')
            task_data.append({"name": name,
                              "power_needed": power_needed,
                              "size": size,
                              "deadline": deadline,
                              "creator": creator,
                              "creation_time": creation_time})

        return task_data

    def parse_fixed_fog_node(self):
        tree = ET.parse(self.fixedFogNodeFilePath)
        root = tree.getroot()
        nodes = []
        for n in root.findall('node'):
            id = n.get('id')
            x = float(n.get('x'))
            y = float(n.get('y'))
            type = n.get('type')
            power = float(n.get('power'))
            lane = int(n.get('lane'))
            node = Node.Node(id, Node.Layer.Fog, power=power, x=x, y=y, coverage_radius=Config.FOG_COVERAGE_RADIUS)
            if n.get('coverage_radius'):
                node.coverage_radius = float(n.get('coverage_radius'))
            nodes.append(node)
        return nodes

    def parse_zone(self):
        tree = ET.parse(self.zoneFilePath)
        root = tree.getroot()
        zones = []
        for z in root.findall('zone'):
            name = z.get('name')
            x = float(z.get('x'))
            y = float(z.get('y'))
            coverage_radius = float(z.get('coverage_radius'))
            mode = Config.RUNNING_MODE
            if mode == Config.RUNNING_MODE_Q_LEARNING:
                zones.append(ZoneManagerQlearning(x=x, y=y, coverage_radius=coverage_radius, name=name))
            elif mode == Config.RUNNING_MODE_RANDOM or mode == Config.RUNNING_MODE_FULLY_RANDOM:
                zones.append(ZoneManagerRandom(x=x, y=y, coverage_radius=coverage_radius, name=name))
            elif mode == Config.RUNNING_MODE_HEURISTIC:
                zones.append(ZoneManagerHeuristic(x=x, y=y, coverage_radius=coverage_radius, name=name))
            elif mode == Config.RUNNING_MODE_A3C:
                zones.append(ZoneManagerA3C(x=x, y=y, coverage_radius=coverage_radius, name=name))
            else:
                error = f"Invalid running mode: {mode}"
                raise ValueError(error)
        return zones
