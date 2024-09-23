import random
from collections import deque

from Clock import Clock
from ZoneManagerBase import *
from ZoneBroadcaster import ZoneBroadcaster

"""
    The Topology class serves as the central management component of the system, integrating different layers: 
    user, fog, and cloud. It manages the assignment of computational tasks to nodes based on their capabilities and 
    current positions. It handles tasks by broadcasting them to the relevant zones and ensures 
    that tasks are processed efficiently, whether by fog nodes or, if necessary, by cloud nodes. 
    The Topology class also updates the state of the network as nodes move and tasks are completed.
"""

from Node import Node


class Topology:
    def __init__(self, user_layer, fog_layer, cloud_layer, graph, timeslot_length=1):
        self.user_layer = user_layer
        self.fog_layer = fog_layer
        self.cloud_layer = cloud_layer
        self.graph = graph
        self.TIMESLOT_LENGTH = timeslot_length
        self.zones = []
        self.zone_broadcaster = ZoneBroadcaster()
        self.task_queue = deque()

    def set_zones(self, zones):
        self.zone_broadcaster.set_zones(zones)
        self.zones = zones

    def update_topology(self):
        self.graph.update_graph()
        for zone_manager in self.zones:
            zone_manager.update(self)
        for node in self.cloud_layer.get_nodes():
            for task in node.tasks:
                if node.is_done(task):
                    node.remove_task(task)
                    self.send_cloud_task_result_to_owner(task)

    def send_cloud_task_result_to_owner(self, task: Task):
        owner_id = task.creator.id
        owner = self.get_node(owner_id)
        x, y = owner.x, owner.y
        owner.deliver_task_result(task)
        print(f"Task {task.name} is sent to owner {owner_id} at ({x}, {y})")

    def assign_fog_nodes_to_zones(self, fog_node, limit=False):
        assigned_count = 0
        for zone in self.zones:
            if zone.is_within_coverage(fog_node.x, fog_node.y):
                zone.add_fog_node(fog_node)
                assigned_count += 1
                if limit:
                    if assigned_count >= 3:
                        break

    def assign_task(self, user_node: Node, task):
        if Config.RUNNING_MODE == Config.RUNNING_MODE_FULLY_RANDOM:
            self.assign_task_random(user_node, task)
            return

        zone_broadcaster = self.zone_broadcaster
        target_zones = self.get_target_zones(task.exec_time, user_node, zone_broadcaster)
        offers = zone_broadcaster.broadcast_to_zones(target_zones, user_node, task)

        cloud = self.cloud_layer.get_nodes()[0]
        cloud_distance = cloud.distance(user_node)

        is_successful = False
        while not is_successful and len(offers) > 0:
            min_distance = float('inf')
            best_zone = None
            best_offer = None
            for offer in offers:
                zone_name, fog_node = offer
                zone = zone_broadcaster.get_zone(zone_name)
                distance = fog_node.distance(user_node)
                if distance < min_distance:
                    min_distance = distance
                    best_zone = zone
                    best_offer = offer
            # accept offer
            if min_distance < 0.5 * cloud_distance:
                is_successful = best_zone.accept_offer(user_node, task, best_offer)
                if not is_successful:
                    offers.remove(best_offer)
            else:
                break

        if len(offers) == 0 and not is_successful:
            cloud = self.cloud_layer.get_nodes()[0]

            if cloud.power >= task.power_needed and cloud.is_in_range(user_node.x, user_node.y) \
                    and ZoneManagerBase.not_enough_time(task, cloud.distance(user_node), is_cloud=True):
                cloud.append_task(task)
                Evaluator.cloud_tasks += 1
                return
            else:
                self.task_queue.append(task)

    def get_target_zones(self, exec_time_estimate, user_node, zone_broadcast):
        new_x = user_node.x + user_node.speed * exec_time_estimate * math.cos(user_node.angle)
        new_y = user_node.y + user_node.speed * exec_time_estimate * math.sin(user_node.angle)
        current_zones = zone_broadcast.get_zones_by_position(user_node.x, user_node.y)
        if Config.RUNNING_MODE == Config.RUNNING_MODE_FULLY_RANDOM:
            return current_zones
        predicted_zones = zone_broadcast.get_zones_by_position(new_x, new_y)
        ideal_zones = set(current_zones).intersection(set(predicted_zones))
        if ideal_zones:
            target_zones = ideal_zones
        else:
            target_zones = current_zones
        return target_zones

    def get_node(self, node_id):
        return self.graph.get_node(node_id)

    def get_nearest_zone(self, x, y):
        nearest_zone = None
        min_distance = float('inf')
        for zone in self.zones:
            distance = math.sqrt((x - zone.x) ** 2 + (y - zone.y) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_zone = zone
        return nearest_zone

    def process_task_queue(self):
        queue_length = len(self.task_queue)
        if queue_length > Config.TASK_QUEUE_SIZE:
            for _ in range(queue_length - Config.TASK_QUEUE_SIZE):
                task = self.task_queue.popleft()
                Evaluator.increment_deadline_misses()
                print("Task missed:", task.name, "due to queue overflow.")
        for _ in range(queue_length):
            task = self.task_queue.popleft()
            task.creation_time = Clock.time
            user_node = task.creator
            self.assign_task(user_node, task)

    def assign_task_random(self, user_node, task):
        fog_nodes = self.fog_layer.get_nodes()
        if len(fog_nodes) == 0:
            cloud = self.cloud_layer.get_nodes()[0]
            if cloud.power >= task.power_needed and cloud.is_in_range(user_node.x, user_node.y) \
                    and ZoneManagerBase.not_enough_time(task, cloud.distance(user_node), is_cloud=True):
                cloud.append_task(task)
                Evaluator.cloud_tasks += 1
                return
            else:
                self.task_queue.append(task)
                return
        else:
            fog_node = random.choice(fog_nodes)
            if fog_node.power >= task.power_needed and fog_node.is_in_range(user_node.x, user_node.y) \
                    and not ZoneManagerBase.not_enough_time(task, fog_node.distance(user_node), fog_node):
                fog_node.append_task(task)
            else:
                self.task_queue.append(task)
                return
