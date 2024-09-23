import math

from Code.Learner import State


def calculate_distance_of_states(state1, state2):
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



task_data_sample = (1, 1, 1, 1, 1, 1, 1)
fog_node_sample = (1, 1, 1, 1, 1)
state1 = State(task_data=task_data_sample, fog_nodes_data=[fog_node_sample]*37)
state2 = State(task_data=task_data_sample, fog_nodes_data=[fog_node_sample]*2)
print(state1)
print(state2)
print(calculate_distance_of_states(state1, state2))
