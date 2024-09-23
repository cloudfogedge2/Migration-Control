import time
import os
import Node
from Learner import Learner
from Visualizer import Visualizer
from Topology import Topology
from UsersLayer import UsersLayer
from FogLayer import FogLayer
from CloudLayer import CloudLayer
from Node import Node, Layer
from Graph import MobilityGraph
from Clock import Clock
from Evaluater import Evaluator
from Config import Config

global user_layer, fog_layer, cloud_layer, zone_broadcaster, topology, task_data

is_iman = Config.IS_IMAN

data_dir = './data'
if is_iman:
    data_dir = 'Code/data/'

if not os.path.exists(data_dir):
    os.makedirs(data_dir)


def get_file_paths():
    base_dir = 'Code/' if is_iman else './'
    offline_suffix = '_offline' if Config.OFFLINE_MODE else ''
    file_paths = {
        'xml_path': f"{base_dir}vehicles_data{offline_suffix}.xml",
        'mobile_xml_path': f"{base_dir}mobileFogNodes_data{offline_suffix}.xml",
        'task_file_path': f"{base_dir}tasks_data{offline_suffix}.xml",
        'fixed_fog_node_file_path': f"{base_dir}fixedFogNodes_data{offline_suffix}.xml",
        'zone_file_path': f"{base_dir}zones_data{offline_suffix}.xml",
    }
    return file_paths


def init_system():
    global user_layer, fog_layer, cloud_layer, topology, task_data

    file_paths = get_file_paths()

    graph = MobilityGraph(
        xml_path=file_paths['xml_path'],
        mobile_xml_path=file_paths['mobile_xml_path'],
        task_file_path=file_paths['task_file_path'],
        fixed_fog_node_file_path=file_paths['fixed_fog_node_file_path'],
        zone_file_path=file_paths['zone_file_path']
    )

    task_data = graph.get_tasks()
    user_layer = UsersLayer(graph)
    fog_layer = FogLayer(graph)
    cloud_layer = CloudLayer()

    for fixed_fog_node in graph.get_fixed_fog_node():
        fog_layer.add_node(fixed_fog_node)
    cloud_layer.add_node(
        Node(0,
             Layer.Cloud,
             power=Config.CLOUD_POWER,
             x=Config.CLOUD_X,
             y=Config.CLOUD_Y,
             coverage_radius=Config.CLOUD_COVERAGE_RADIUS))
    topology = Topology(user_layer, fog_layer, cloud_layer, graph)
    zones = graph.get_zones()
    topology.set_zones(zones)

    for fixed_fog_node in graph.get_fixed_fog_node():
        fog_layer.add_node(fixed_fog_node)
    cloud_layer.add_node(
        Node(0,
             Layer.Cloud,
             power=Config.CLOUD_POWER,
             x=Config.CLOUD_X,
             y=Config.CLOUD_Y,
             coverage_radius=Config.CLOUD_COVERAGE_RADIUS))
    topology = Topology(user_layer, fog_layer, cloud_layer, graph)
    zones = []
    for zone in graph.get_zones():
        zones.append(zone)
    topology.set_zones(zones)
    for fog_node in fog_layer.get_nodes():
        topology.assign_fog_nodes_to_zones(fog_node)

    for zone in zones:
        print(
            f"{zone.name} x:{zone.x} y:{zone.y} coverage_radius:{zone.coverage_radius} covers nodes: {zone.fog_nodes}")

    if Config.OFFLINE_MODE:
        save_path = f'Code/data/' if is_iman else './data/'
        for zone in zones:
            file_path = f'{save_path}{zone.name}_q_table.txt'
            if os.path.exists(file_path):
                os.remove(file_path)


def step():
    global task_data
    log_current_state()
    topology.process_task_queue()
    for i in task_data:
        if i["creation_time"] == Clock.time:
            node: Node = user_layer.get_nodes_by_id(i["creator"])
            task = node.generate_task(i)
            topology.assign_task(node, task)

    topology.update_topology()
    Evaluator.track_step_metrics()
    if Config.ENABLE_VISUALIZATION:
        visualizer.visualize_mobility(graph=topology.graph, title=f"Time: {Clock.time}")


def log_current_state():
    Evaluator.log_short_evaluation()
    if len(topology.task_queue) > 0:
        print(len(topology.task_queue), "Tasks in Queue")
    for node in cloud_layer.get_nodes():
        if len(node.tasks) > 0:
            print("Cloud Node", node.id, "Tasks", len(node.tasks))


init_system()
visualizer = Visualizer(x_range=Config.X_RANGE, y_range=Config.Y_RANGE)
start = time.perf_counter()
for i in range(Config.SIMULATION_DURATION):
    print("\nIteration", i)
    step()

request_time = time.perf_counter() - start
print(f"\nProcess time: {request_time}")
Evaluator.log_evaluation()
if Config.ENABLE_VISUALIZATION_METRICS:
    visualizer.plot_metrics(Evaluator.migration_counts_per_step, Evaluator.deadline_misses_per_step)


def save_all_q_tables():
    for zone in topology.zones:
        if is_iman:
            zone.learner.save_q_table(f'Code/data/{zone.name}_q_table.txt')
        else:
            zone.learner.save_q_table(f'./data/{zone.name}_q_table.txt')


if Config.OFFLINE_MODE:
    save_all_q_tables()
