import random

from Node import Node
from Task import Task
from ZoneManagerBase import ZoneManagerBase


class ZoneManagerRandom(ZoneManagerBase):
    def __init__(self, x, y, coverage_radius, name):
        super().__init__(x, y, coverage_radius, name)

    def is_within_coverage(self, point_x, point_y):
        return super().is_within_coverage(point_x, point_y)

    def add_fog_node(self, fog_node):
        return super().add_fog_node(fog_node)

    def find_assignee(self, user_node: Node, task: Task):
        # possible_ones = []
        # for node in self.fog_nodes:
        #     if node.is_in_range(user_node.x, user_node.y):
        #         possible_ones.append(node)
        #         break
        # if len(possible_ones) == 0:
        #     return None
        # return random.choice(possible_ones)
        if len(self.fog_nodes) == 0:
            return None
        return random.choice(self.fog_nodes)

    def get_possible_fog_nodes(self, task, user_node):
        return super().get_possible_fog_nodes(task, user_node)

    @staticmethod
    def not_enough_time(task, distance, fog_node=None, is_cloud=False, is_migrated=False):
        return ZoneManagerBase.not_enough_time(task, distance, fog_node, is_cloud, is_migrated)

    def create_offer(self, node, task):
        return super().create_offer(node, task)

    def accept_offer(self, user_node, task, offer):
        return super().accept_offer(user_node, task, offer)

    def send_task_result_to_owner(self, task, topology):
        return super().send_task_result_to_owner(task, topology)

    def update(self, topology):
        return super().update(topology)
