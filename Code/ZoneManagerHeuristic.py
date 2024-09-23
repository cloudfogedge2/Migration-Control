import math

from Node import Node
from Task import Task
from ZoneManagerBase import ZoneManagerBase
from Evaluater import timer_log


class ZoneManagerHeuristic(ZoneManagerBase):
    def __init__(self, x, y, coverage_radius, name):
        super().__init__(x, y, coverage_radius, name)

    @timer_log
    def is_within_coverage(self, point_x, point_y):
        return super().is_within_coverage(point_x, point_y)

    @timer_log
    def add_fog_node(self, fog_node):
        return super().add_fog_node(fog_node)

    @timer_log
    def find_assignee(self, user_node: Node, task: Task):
        possible_fog_nodes = self.get_possible_fog_nodes(task, user_node)
        if len(possible_fog_nodes) == 0:
            return None
        assignee = self.iterate_over_outputs(possible_fog_nodes, user_node, task)
        return assignee

    def iterate_over_outputs(self, possible_fog_nodes, user_node, task):
        # sort the fog nodes based on the distance from the user node, to consider the worst case
        possible_fog_nodes = sorted(possible_fog_nodes, key=lambda fog_node: -fog_node.distance(user_node))
        branching_factor = 10
        assignee = None
        best_value = +math.inf
        for fog_node in possible_fog_nodes:
            branching_factor -= 1
            distance = fog_node.distance(user_node)
            future_distance = fog_node.distance_in_future(user_node, task.exec_time)
            if distance + future_distance < best_value:
                assignee = fog_node
                best_value = distance + future_distance
            if branching_factor == 0:
                break
        return assignee

    @timer_log
    def get_possible_fog_nodes(self, task, user_node):
        return self.fog_nodes
        # return super().get_possible_fog_nodes(task, user_node)

    @staticmethod
    @timer_log
    def not_enough_time(task, distance, fog_node=None, is_cloud=False, is_migrated=False):
        return ZoneManagerBase.not_enough_time(task, distance, fog_node, is_cloud, is_migrated)

    @timer_log
    def create_offer(self, node, task):
        return super().create_offer(node, task)

    @timer_log
    def accept_offer(self, user_node, task, offer):
        return super().accept_offer(user_node, task, offer)

    @timer_log
    def send_task_result_to_owner(self, task, topology):
        return super().send_task_result_to_owner(task, topology)

    @timer_log
    def update(self, topology):
        return super().update(topology)
