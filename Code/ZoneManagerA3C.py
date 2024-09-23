from ZoneManagerBase import ZoneManagerBase
from LearnerA3C import LearnerA3C
from Learner import *


class ZoneManagerA3C(ZoneManagerBase):
    def __init__(self, x, y, coverage_radius, name):
        super().__init__(x, y, coverage_radius, name)
        self.learner = LearnerA3C(name)

    def is_within_coverage(self, point_x, point_y):
        return super().is_within_coverage(point_x, point_y)

    def add_fog_node(self, fog_node):
        return super().add_fog_node(fog_node)

    def find_assignee(self, user_node, task):
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

    def get_possible_fog_nodes(self, task, user_node):
        return super().get_possible_fog_nodes(task, user_node)

    @staticmethod
    def not_enough_time(task, distance, fog_node=None, is_cloud=False, is_migrated=False):
        return ZoneManagerBase.not_enough_time(task, distance, fog_node, is_cloud, is_migrated)

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

    def get_state(self, task):
        return State.get_from_fog_nodes_and_task(self.fog_nodes, task)

    def send_task_result_to_owner(self, task, topology):
        ownder_id = task.creator.id
        owner = topology.get_node(ownder_id)
        x, y = owner.x, owner.y
        owner.deliver_task_result(task)

        state = task.creation_state
        next_state = self.get_state(task)
        task.check_deadline_missed()
        reward = self.learner.get_reward(is_deadline_missed=task.is_deadline_missed, is_migrated=task.is_migrated)
        self.learner.update_q_table_by_finished_task(task=task, next_state=next_state, reward=reward)
        return

    def update(self, topology):
        return super().update(topology)
