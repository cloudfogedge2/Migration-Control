import Learner

from Task import Task
from Evaluater import Evaluator
from Node import Node
from ZoneManagerBase import ZoneManagerBase
from Evaluater import timer_log


class ZoneManagerQlearning(ZoneManagerBase):
    def __init__(self, x, y, coverage_radius, name):
        super().__init__(x, y, coverage_radius, name)
        self.learner = Learner.Learner(name)

    @timer_log
    def is_within_coverage(self, point_x, point_y):
        return super().is_within_coverage(point_x, point_y)

    @timer_log
    def add_fog_node(self, fog_node):
        super().add_fog_node(fog_node)

    @timer_log
    def find_assignee(self, user_node: Node, task: Task):
        possible_fog_nodes = self.get_possible_fog_nodes(task, user_node)
        if len(possible_fog_nodes) == 0:
            return None
        assignee = self.learner.get_suggested_assignee(
            all_fog_nodes=self.fog_nodes,
            possible_fog_nodes=possible_fog_nodes,
            task=task
        )
        if assignee is None:
            # in this case, we should assign the task to fog node with least predicted + current distance
            assignee = min(possible_fog_nodes,
                           key=lambda fog_node: fog_node.distance(user_node) + fog_node.distance_in_future(user_node,
                                                                                                           task.exec_time))
        return assignee

    @timer_log
    def get_possible_fog_nodes(self, task, user_node):
        return super().get_possible_fog_nodes(task, user_node)

    @staticmethod
    @timer_log
    def not_enough_time(task, distance, fog_node=None, is_cloud=False, is_migrated=False):
        return ZoneManagerBase.not_enough_time(task, distance, fog_node, is_cloud, is_migrated)

    @timer_log
    def create_offer(self, node, task):
        return super().create_offer(node, task)

    @timer_log
    def accept_offer(self, user_node, task, offer):
        possible_nodes = self.get_possible_fog_nodes(task, user_node)
        assignee = offer[1]
        if assignee in possible_nodes:
            assignee.append_task(task)
            state = self.get_state(task)
            task.set_creation_state(state)
            return True
        return False

    @timer_log
    def get_state(self, task):
        return self.learner.get_from_fog_nodes_and_task(self.fog_nodes, task)

    @timer_log
    def update(self, topology):
        return super().update(topology)

    @timer_log
    def send_task_result_to_owner(self, task: Task, topology):
        owner_id = task.creator.id
        owner = topology.get_node(owner_id)
        x, y = owner.x, owner.y
        owner.deliver_task_result(task)

        next_state = self.get_state(task)
        task.check_deadline_missed()
        reward = self.learner.get_reward(is_deadline_missed=task.is_deadline_missed, is_migrated=task.is_migrated)
        self.learner.update_q_table_by_finished_task(task, next_state, reward)
        print(f"Task {task.name} is sent to owner {owner_id} at ({x}, {y})")
