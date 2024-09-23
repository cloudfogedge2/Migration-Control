import random
import numpy as np
import math
import json
from Task import Task
from Config import Config
from Evaluater import timer_log

is_iman = Config.IS_IMAN
discrete_levels = Config.DISCRETE_LEVELS

def discretize(value, bins):
    return np.digitize(value, bins)


''' 
State class:

State is used for representing the state of a zone manager when it is making a decision about assigning a task to a fog node.
It is to be used by the learner to make decisions based on the current state of the zone manager and update the Q-table accordingly.
State class has two attributes:
    - fog_nodes_data: a list of tuples, each tuple represents the data of a fog node in the zone manager. 
        The data of a fog node is a tuple of the following form:
            (x, y, speed, angle, power)
    - task_data: a tuple representing the data of the task that the zone manager is making a decision about.
        The data of a task is a tuple of the following form:
            (power_needed, size, deadline, creator_x, creator_y, creator_speed, angle)
'''


class State:
    def __init__(self, fog_nodes_data, task_data):
        self.fog_nodes_data = fog_nodes_data
        self.task_data = task_data

    @staticmethod
    @timer_log
    def get_task_data(task):
        """
        This method is used to get the data of a task in a discretized form.
        """
        task_data = (
            # task.name,
            discretize(task.power_needed, np.linspace(0, 3, discrete_levels)),
            discretize(task.size, np.linspace(0, 3, discrete_levels)),
            discretize(task.deadline, np.linspace(0, 100, discrete_levels)),
            discretize(task.creator.x, np.linspace(0, 10, discrete_levels)),
            discretize(task.creator.y, np.linspace(0, 10, discrete_levels)),
            discretize(task.creator.speed, np.linspace(0, 3, discrete_levels)),
            discretize(task.creator.angle, np.linspace(0, 360, discrete_levels))
        )
        return task_data

    @staticmethod
    @timer_log
    def get_fog_nodes_data(fog_nodes):
        fog_nodes_data = []
        for fog_node in fog_nodes:
            fog_node_data = (
                # fog_node.id,
                discretize(fog_node.x, np.linspace(0, 10, discrete_levels)),
                discretize(fog_node.y, np.linspace(0, 10, discrete_levels)),
                discretize(fog_node.speed, np.linspace(0, 3, discrete_levels)),
                discretize(fog_node.angle, np.linspace(0, 360, discrete_levels)),
                discretize(fog_node.power, np.linspace(0, 20, discrete_levels))
            )
            fog_nodes_data.append(fog_node_data)
        return fog_nodes_data

    @staticmethod
    @timer_log
    def from_str(state_str):
        state_str = state_str.replace("State: [", "").replace("(", "")
        fog_nodes_data_str, task_data_str = state_str.split("], ")
        task_data_str = task_data_str.replace("(", "").replace(")", "")
        fog_nodes_data = []
        for fog_node_data_str in fog_nodes_data_str.split("), "):
            fog_node_data_str = fog_node_data_str.replace("(", "").replace(")", "")
            fog_node_data = tuple(map(int, fog_node_data_str.split(", ")))
            fog_nodes_data.append(fog_node_data)
        task_data = tuple(map(int, task_data_str.split(", ")))
        return State(fog_nodes_data, task_data)

    def __str__(self):
        return f"State: {self.fog_nodes_data}, {self.task_data}"

    def __repr__(self):
        return f"State: {self.fog_nodes_data}, {self.task_data}"


'''
Action class:

An action is a decision of assigning a task to a fog node. We only keep the general properties of the fog node in the action.
The action class has the following attributes:
    (id, x, y, speed, angle, power)
'''


class Action:
    def __init__(self, id, x, y, speed, angle, power):
        self.id = id
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.power = power

    @staticmethod
    @timer_log
    def from_fog_node(fog_node):
        return Action(fog_node.id, fog_node.x, fog_node.y, fog_node.speed, fog_node.angle, fog_node.power)

    def __str__(self):
        return f"Action: {self.id}, {self.x}, {self.y}, {self.speed}, {self.angle}, {self.power}"

    def __repr__(self):
        return f"Action: {self.id}, {self.x}, {self.y}, {self.speed}, {self.angle}, {self.power}"

    @staticmethod
    @timer_log
    def from_str(action_str):
        action_str = action_str.replace("Action: ", "")
        id, x, y, speed, angle, power = action_str.split(", ")
        return Action(id, float(x), float(y), float(speed), float(angle), float(power))


'''
Learner class:

Learner is the class that implements the Q-learning algorithm. It keeps a Q-table that stores the Q-values of the states and actions.

The learner class has the following attributes:
    - q_table: the q-table of the learner
        The q-table is a dictionary of the following form:
        {state: {action1: q_value1, action2: q_value2, ...}}
    - alpha: the learning rate of the learner
    - gamma: the discount factor of the learner
    - epsilon: the exploration rate of the learner
    
The learner class has the following methods that are called by the q-learning zone manager:
    - get_suggested_assignee: returns the suggested assignee for a task based on the current state of the zone manager and the q-table
    - get_reward: returns the reward for a task based on the task's properties (whether the deadline is missed or it's migrated)
    - update_q_table: updates the q-table based on the reward and the next state of the zone manager
'''


class Learner:
    def __init__(self, zone_manager_name):
        # q table: {state: {action1: q_value1, action2: q_value2, ...}}
        # a state is a state class object of the form:
        # ([fog_node_data1, fog_node_data2, ...], (input_task_data))
        # fog_node_data is a tuple of the form:
        #   (fog_node_id, fog_node_x, fog_node_y, fog_node_speed, fog_node_angle, fog_node_remaining_power)
        # input_task_data is a tuple of the form:
        #   (task_name, task_power_needed, task_size, task_deadline, task_creator_x, task_creator_y, task_creator_speed, task_creator_angle)
        # actions are the fog nodes that the learner can assign the task to
        if Config.OFFLINE_MODE:
            self.q_table = {}
        else:
            if is_iman:
                self.q_table = self.load_q_table(f'Code/data/{zone_manager_name}_q_table.txt')
            else:
                self.q_table = self.load_q_table(f'./data/{zone_manager_name}_q_table.txt')

        self.alpha = 0.1
        self.gamma = 0.6
        self.epsilon = 0.1

    @timer_log
    def get_state_from_task(self, task: Task):
        return task.creation_state

    def exist_state(self, state):
        nearest_state = self.find_nearest_state(state)
        if nearest_state is None:
            return False
        distance = self.calculate_distance_of_states(state, nearest_state)
        return distance == 0

    @timer_log
    def get_from_fog_nodes_and_task(self, fog_nodes, task):
        fog_nodes_data = State.get_fog_nodes_data(fog_nodes)
        task_data = State.get_task_data(task)
        state = State(fog_nodes_data, task_data)
        if self.exist_state(state):
            state = self.find_nearest_state(state)
        return state

    @timer_log
    def get_suggested_assignee(self, all_fog_nodes, possible_fog_nodes, task):
        """
        This method is used to get the suggested assignee for a task based on the current state of the zone manager and the q-table.
        :param all_fog_nodes: all the fog nodes in the zone manager, used for creating the state
        :param possible_fog_nodes: the fog nodes that the task creator can reach, used for getting the suggested assignee
        :param task: the task that the zone manager is making a decision about
        :return: the suggested assignee for the task
        """
        if possible_fog_nodes is None or len(possible_fog_nodes) == 0:
            return None
        # note that we should only pass the fog nodes that are in range of the task creator
        state = self.get_from_fog_nodes_and_task(all_fog_nodes, task)
        if Config.OFFLINE_MODE:
            if not self.exist_state(state):
                self.q_table[state] = {}
        if self.epsilon > 0 and random.random() < self.epsilon:
            return random.choice(possible_fog_nodes)
        best_action = self.get_best_q_entry(state, possible_fog_nodes)
        if best_action is None:
            # This means that the learner has not seen this state before
            # or by any reason, it has no action for this state. The zone manager should handle this case
            return None
        fog_node = self.get_node_by_id(best_action.id, all_fog_nodes)
        return fog_node

    @timer_log
    def get_node_by_id(self, node_id, all_fog_nodes):
        for node in all_fog_nodes:
            if node.id == node_id:
                return node

    @timer_log
    def get_q_value(self, state, action, find_nearest_action=False):
        """
        This method is used to get the q-value of a state-action pair from the q-table.
        :param state: the state of the zone manager
        :param action: the action of assigning a task to a fog node
        :param find_nearest_action: a boolean that indicates whether the learner should find the nearest action to the given action
            or just keep looking for the original action. This is used when the learner has not seen the action before.
        :return: the q-value of the state-action pair
                if the state-action pair is not in the q-table, and nearest action isn't also to be considered, it returns 0
        """
        if not self.exist_state(state):
            self.q_table[state] = {}
        else:
            state = self.find_nearest_state(state)
        if action not in self.q_table[state]:
            if find_nearest_action:
                nearest_action = self.find_nearest_action(state, action)
                if nearest_action:
                    action = nearest_action
                else:
                    return 0
            else:
                self.q_table[state][action] = 0
        return self.q_table[state][action]

    @timer_log
    def get_max_q_value(self, state):
        if not self.exist_state(state):
            self.q_table[state] = {}
            return 0
        else:
            state = self.find_nearest_state(state)
        if len(self.q_table[state].values()) == 0:
            return 0

        return max(self.q_table[state].values())

    @timer_log
    def get_best_q_entry(self, state, possible_fog_nodes=None):
        """
        This method is used to get the best action for a state based on the q-table.
        :param state: the state of the zone manager
        :param possible_fog_nodes: the fog nodes that the task creator can reach
        :return: the best action for the state
        """
        if not self.exist_state(state):
            nearest_state = self.find_nearest_state(state)
            if nearest_state:
                state = nearest_state
            else:
                self.q_table[state] = {}
        if self.q_table[state] == {}:
            return None
        if possible_fog_nodes is None:
            return max(self.q_table[state], key=self.q_table[state].get)
        else:
            best_q_value = float('-inf')
            best_action = None
            for node in possible_fog_nodes:
                action = Action.from_fog_node(node)
                # if action not in self.q_table[state]:
                #     continue
                q_value = self.get_q_value(state, action, find_nearest_action=True)
                if q_value > best_q_value:
                    best_q_value = q_value
                    best_action = action
            if best_action is None:
                return max(self.q_table[state], key=self.q_table[state].get)
            return best_action

    @timer_log
    def find_nearest_state(self, state):
        nearest_state = None
        min_distance = float('inf')
        # for existing_state in self.q_table.keys() - {state}:
        for existing_state in self.q_table.keys():
            distance = self.calculate_distance_of_states(state, existing_state)
            if distance < min_distance:
                min_distance = distance
                nearest_state = existing_state
        if min_distance <= Config.Q_LEARNING_NEAREST_STATE_DISTANCE_THRESHOLD:
            return nearest_state
        else:
            return None

    @timer_log
    def calculate_distance_of_states(self, state1, state2):
        # todo : what happens if the states have different number of fog nodes?
        # or what happens if the second fog nodes are a subset of the first fog nodes but in different order?
        distance = 0
        if len(state1.fog_nodes_data) > len(state2.fog_nodes_data):
            state1, state2 = state2, state1
        all_distances = []
        for data1 in state1.fog_nodes_data:
            min_distance = float('inf')
            for data2 in state2.fog_nodes_data:
                pairwise_distance = sum((x1 - x2) ** 2 for x1, x2 in zip(data1, data2))
                if pairwise_distance < min_distance:
                    min_distance = pairwise_distance
            all_distances.append(min_distance)
        distance += sum(all_distances)
        task_distance = sum((x1 - x2) ** 2 for x1, x2 in zip(state1.task_data, state2.task_data))
        distance += task_distance
        return math.sqrt(distance)

    @timer_log
    def find_nearest_action(self, state, action):
        nearest_action = None
        min_distance = float('inf')
        for existing_action in self.q_table[state].keys():
            distance = self.calculate_distance_of_actions(action, existing_action)
            if distance != 0 and distance < min_distance:
                min_distance = distance
                nearest_action = existing_action
        if min_distance <= Config.Q_LEARNING_NEAREST_ACTION_DISTANCE_THRESHOLD:
            return nearest_action
        else:
            return None

    @timer_log
    def calculate_distance_of_actions(self, action1, action2):
        action_data1 = (action1.x, action1.y, action1.speed, action1.angle, action1.power)
        action_data2 = (action2.x, action2.y, action2.speed, action2.angle, action2.power)
        distance = sum((x1 - x2) ** 2 for x1, x2 in zip(action_data1, action_data2))
        return math.sqrt(distance)

    @timer_log
    def update_q_table(self, state, action, reward, next_state):
        """
        This method is used to update the q-table based on the reward and the next state of the zone manager.
        It is to be called by the zone manager after a task is finished
        :param state: the state of the zone manager
        :param action: the action of assigning a task to a fog node
        :param reward: the reward of the action
        :param next_state: the state of zone manager after the task is done
        """
        q_value = self.get_q_value(state, action)
        max_q_value = self.get_max_q_value(next_state)
        new_q_value = q_value + self.alpha * (reward + self.gamma * max_q_value - q_value)
        if self.exist_state(state):
            state = self.find_nearest_state(state)
        self.q_table[state][action] = new_q_value

    @timer_log
    def update_q_table_by_finished_task(self, task, next_state, reward):
        state = self.get_state_from_task(task)
        action = task.assigned_action
        self.update_q_table(state=state, action=action, reward=reward, next_state=next_state)

    @timer_log
    def save_q_table(self, file_path):
        nested_q_table = self.convert_q_table(self.q_table)
        with open(file_path, 'w') as file:
            json.dump(nested_q_table, file, indent=4)

    @timer_log
    def load_q_table(self, file_path):
        """
        Used for loading the q-table from a file that was filled in the offline phase
        """
        q_table = {}
        with open(file_path, 'r') as file:
            nested_q_table = json.load(file)
            for state_str, entry in nested_q_table.items():
                state = State.from_str(state_str)
                if entry == {}:
                    continue
                q_table[state] = {}
                for action_str, q_value in entry.items():
                    action = Action.from_str(action_str)
                    if q_value != 0:
                        q_table[state][action] = q_value
        return q_table

    @timer_log
    def convert_q_table(self, q_table):
        """
        Used for converting the q-table to a nested dictionary to be saved in a file
        """
        nested_q_table = {}
        for state, actions in q_table.items():
            if actions == {}:
                continue
            nested_q_table[str(state)] = {}
            for action, reward in actions.items():
                if reward == 0:
                    continue
                if action is None:
                    print(f"Warning: Skipping a None node entry in state {str(state)}")
                    continue
                nested_q_table[str(state)][str(action)] = reward
        return nested_q_table

    # todo maybe uncomment
    # @staticmethod
    # def get_reward(task, is_deadline_missed, is_migrated, energy_consumed, resource_utilization, distance):
    #
    #     reward = 0
    #
    #     # Penalty for missing deadline
    #     if is_deadline_missed:
    #         reward -= 10
    #     else:
    #         reward += 10  # Reward for meeting the deadline
    #
    #     # Penalty for migration
    #     if is_migrated:
    #         reward -= 2
    #
    #     # Reward for energy efficiency (less energy consumed is better)
    #     reward += (100 - energy_consumed) / 10
    #
    #     # Reward for efficient resource utilization (e.g., CPU, memory)
    #     reward += resource_utilization * 5
    #
    #     # Reward for distance (closer nodes get a higher reward)
    #     reward += (100 - distance) / 10
    #
    #     return reward

    @staticmethod
    @timer_log
    def get_reward(is_deadline_missed, is_migrated):
        reward = 0
        if is_deadline_missed:
            reward -= 10
        else:
            reward += 10
        if is_migrated:
            reward -= 20
        return reward
