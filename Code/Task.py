"""
    The Task class encapsulates the details of a computational task within the system.
    It includes the task's power requirements, size, deadline, and the node responsible for executing it.
    The class tracks whether the task has been assigned, whether it meets its deadline, and
    if it needs to be migrated to another node. It also stores the result of the task once it's completed,
    making it a crucial component for managing and monitoring task execution.
"""
from Clock import Clock


def get_exec_time(size, needed_freq):
    return size / needed_freq


class Task:
    def __init__(self, power_needed, name, size, deadline, creator, creation_time, needed_freq=2):
        self.power_needed = power_needed
        self.name = name
        self.deadline = deadline
        self.exec_time = get_exec_time(size, needed_freq)
        self.size = size
        self.creation_time = creation_time
        self.creator = creator
        self.assigned_action = None
        self.assigned_node = None
        self.result = None
        self.deadline_duration = deadline - creation_time
        self.creation_state = None
        self.is_migrated = False
        self.is_deadline_missed = False

    def set_creation_state(self, state):
        self.creation_state = state

    def set_result(self, result):
        self.result = result

    def get_result(self):
        return self.result

    def set_assignee(self, node, action):
        self.assigned_node = node
        self.assigned_action = action

    def remove_assignee(self):
        self.assigned_node = None

    def check_deadline_missed(self):
        self.is_deadline_missed = Clock.time > self.deadline
        return self.is_deadline_missed
# class TaskProfile:
#     #todo implement
