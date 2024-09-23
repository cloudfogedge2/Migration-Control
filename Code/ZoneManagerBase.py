import math
from abc import ABC, abstractmethod

from Node import Node
from Task import Task
from Evaluater import *


class ZoneManagerBase(ABC):
    @abstractmethod
    def __init__(self, x, y, coverage_radius, name):
        self.x = x
        self.y = y
        self.coverage_radius = coverage_radius
        self.name = name
        self.fog_nodes = []

    @abstractmethod
    def is_within_coverage(self, point_x, point_y):
        distance = math.sqrt((point_x - self.x) ** 2 + (point_y - self.y) ** 2)
        return distance <= self.coverage_radius

    @abstractmethod
    def add_fog_node(self, fog_node):
        if fog_node not in self.fog_nodes:
            self.fog_nodes.append(fog_node)

    @abstractmethod
    def find_assignee(self, user_node: Node, task: Task):
        pass

    @staticmethod
    @abstractmethod
    def not_enough_time(task, distance, fog_node=None, is_cloud=False, is_migrated=False):
        # todo consider the power of fog node (the formula may change)
        time_taken = Node.get_exec_time(distance, task, is_cloud, is_migrated)
        return time_taken > task.deadline_duration


    @abstractmethod
    def create_offer(self, node, task):
        if not self.is_within_coverage(node.x, node.y):
            return None
        fog = self.find_assignee(node, task)
        if fog is None:
            return None
        offer = (self.name, fog)
        return offer

    @abstractmethod
    def accept_offer(self, user_node, task, offer):
        possible_nodes = self.get_possible_fog_nodes(task, user_node)
        assignee = offer[1]
        if assignee in possible_nodes:
            assignee.append_task(task)
            return True
        return False

    @abstractmethod
    def get_possible_fog_nodes(self, task, user_node):
        possible_fog_nodes = []
        # they should be reachable and also have enough power and time to process the task
        for node in self.fog_nodes:
            if node.power >= task.power_needed \
                    and node.is_in_range(user_node.x, user_node.y):
                if not self.not_enough_time(task, node.distance(user_node), node):
                    possible_fog_nodes.append(node)
        return possible_fog_nodes

    @abstractmethod
    @timer_log
    def send_task_result_to_owner(self, task, topology):
        owner_id = task.creator.id
        owner = topology.get_node(owner_id)
        x, y = owner.x, owner.y
        owner.deliver_task_result(task)
        task.check_deadline_missed()
        print(f"Task {task.name} is sent to owner {owner_id} at ({x}, {y})")

    @abstractmethod
    def update(self, topology):
        # print(len(self.fog_nodes))
        for fog_node in self.fog_nodes:
            for task in fog_node.tasks:
                if fog_node.is_done(task):
                    fog_node.remove_task(task)
                    creator = topology.get_node(task.creator.id)
                    nearest_zone = topology.get_nearest_zone(creator.x, creator.y)
                    if self.is_within_coverage(creator.x, creator.y):
                        nearest_zone = self
                    if nearest_zone == self:
                        self.send_task_result_to_owner(task, topology)
                    else:
                        Evaluator.increment_migrations()
                        task.is_migrated = True
                        print(
                            f"The result of task {task.name} is sent to zone {nearest_zone.name} from zone {self.name}")
                        nearest_zone.send_task_result_to_owner(task, topology)

        for fog_node in self.fog_nodes:
            if not self.is_within_coverage(fog_node.x, fog_node.y):
                self.fog_nodes.remove(fog_node)
                topology.assign_fog_nodes_to_zones(fog_node, limit=True)
                # print(f"The moving fog node {fog_node.id} is now out of zone {self.name}")
