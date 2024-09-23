"""
    Node class representing any computational resource in the system.
    Nodes can belong to different layers, such as Users, Fog, or Cloud.

    Attributes:
        id (int): The unique identifier of the node.
        layer (Layer): The layer to which this node belongs (Users, Fog, or Cloud).
        power (int): The computational power available at this node.
        x (float): The X-coordinate of the node's position.
        y (float): The Y-coordinate of the node's position.
        speed (float): The speed of the node (for mobile nodes).
        angle (float): The direction in which the node is moving.
        coverage_radius (float): The coverage radius of the node.
        tasks (list): A list of tasks assigned to this node.

    Methods:
        distance(other_node): Calculates the distance between this node and another node.
        distance_by_x_y(x, y): Calculates the distance between this node and a given (x, y) coordinate.
        distance_in_future(other_node, exec_time_estimate): Predicts the future distance between this node and another node.
        append_task(task): Appends a task to the node's task list and updates the node's power.
        generate_task(task_data): Generates a task based on the provided task data.
        is_in_range(x, y): Checks if a given (x, y) coordinate is within the node's coverage range.
        is_in_range_in_future(x, y, exec_time_estimate): Checks if a given (x, y) coordinate will be in range in the future.
        deliver_task_result(task): Delivers the result of a task and checks if the deadline is missed.
        is_done(task): Checks if a task is completed based on the current time.
        remove_task(task): Removes a task from the node's task list and updates the node's power.
        get_pred_x_y(exec_time_estimate): Predicts the future (x, y) position of the node.
"""

import math
from Task import Task
from Clock import Clock
from Evaluater import Evaluator
from Config import Config
from Learner import Action


class Layer:
    Users = 0
    Fog = 1
    Cloud = 2


class Node:
    def __init__(self, id, layer, power=Config.FOG_POWER, x=0, y=0, coverage_radius=Config.FOG_COVERAGE_RADIUS, speed=0,
                 angle=0):
        """
        Initializes a new Node instance.

        Args:
            id (int): The unique identifier of the node.
            layer (Layer): The layer to which this node belongs (Users, Fog, or Cloud).
            power (int, optional): The computational power of the node. Defaults to Config.FOG_POWER.
            x (float, optional): The X-coordinate of the node. Defaults to 0.
            y (float, optional): The Y-coordinate of the node. Defaults to 0.
            coverage_radius (float, optional): The coverage radius of the node. Defaults to Config.FOG_COVERAGE_RADIUS.
            speed (float, optional): The speed of the node (for mobile nodes). Defaults to 0.
            angle (float, optional): The direction in which the node is moving. Defaults to 0.
        """
        self.id = id
        self.layer = layer
        self.power = power
        self.x = x
        self.y = y
        self.speed = speed
        self.coverage_radius = coverage_radius
        self.angle = angle
        self.tasks = []

    def __repr__(self):
        return f"Node(id={self.id}, x={self.x}, y={self.y})"

    def distance(self, other_node):
        """
        Calculates the distance between this node and another node.

        Args:
            other_node (Node): The other node to which the distance is calculated.

        Returns:
            float: The Euclidean distance between the two nodes.
        """
        return self.distance_by_x_y(other_node.x, other_node.y)

    def distance_by_x_y(self, x, y):
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)

    def distance_in_future(self, other_node, exec_time_estimate):
        other_pred_x, other_pred_y = other_node.get_pred_x_y(exec_time_estimate)
        return self.distance_in_future_by_x_y(other_pred_x, other_pred_y, exec_time_estimate)

    def distance_in_future_by_x_y(self, x, y, exec_time_estimate):
        pred_x, pred_y = self.get_pred_x_y(exec_time_estimate)
        return math.sqrt((pred_x - x) ** 2 + (pred_y - y) ** 2)

    def append_task(self, task):
        Evaluator.update_task_count(self.id)
        task.set_assignee(node=self, action=Action.from_fog_node(self))
        self.tasks.append(task)
        self.power -= task.power_needed

    def generate_task(self, task_data):
        task = Task(
            name=task_data['name'],
            power_needed=task_data['power_needed'],
            size=task_data['size'],
            deadline=task_data['deadline'],
            creator=self,
            creation_time=task_data['creation_time']
        )
        Evaluator.total_tasks += 1
        return task

    def is_in_range(self, x, y):
        return self.distance_by_x_y(x, y) <= self.coverage_radius

    def is_in_range_in_future(self, x, y, exec_time_estimate):
        return self.distance_in_future_by_x_y(x, y, exec_time_estimate) <= self.coverage_radius

    def deliver_task_result(self, task):
        task.check_deadline_missed()
        task.remove_assignee()

        if not task.is_deadline_missed:
            print(f"Task {task.name} is done and delivered on time!")
        else:
            print(f"Task {task.name} is done but delivered late!")
            Evaluator.increment_deadline_misses()

    def is_done(self, task):
        distance = self.distance(task.creator)
        is_cloud = self.layer == Layer.Cloud
        if Clock.time >= (task.creation_time + self.get_exec_time(distance, task, is_cloud=is_cloud,
                                                                  is_migrated=task.is_migrated)):
            task.set_result("Random Result")
            return True
        return False

    def remove_task(self, task):
        self.tasks.remove(task)
        self.power += task.power_needed

    def get_pred_x_y(self, exec_time_estimate):
        pred_x = self.x + self.speed * exec_time_estimate * math.cos(math.radians(self.angle))
        pred_y = self.y + self.speed * exec_time_estimate * math.sin(math.radians(self.angle))
        return pred_x, pred_y

    @staticmethod
    def get_exec_time(distance, task, is_cloud, is_migrated):
        exec_time = task.exec_time
        if is_cloud:
            # exec_time = exec_time / 2  # cloud can process faster
            exec_time += Config.CLOUD_PROCESSING_OVERHEAD
        time_taken = exec_time \
                     + Config.TASK_COST_PER_METER * distance * 2 \
                     + Config.PACKET_COST_PER_METER * distance
        if is_migrated:
            time_taken += Config.MIGRATION_OVERHEAD
        return time_taken
