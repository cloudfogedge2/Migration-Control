import matplotlib.pyplot as plt

'''
    this class is responsible for creating visual representations of the system's state,
     particularly the positions of user nodes and fog nodes in a 2D space.
     It uses matplotlib to plot these nodes on a graph, which helps in observing the mobility patterns and coverage of
      different nodes over time. This is useful for analyzing how nodes interact within the system's geographic area.
'''


class Visualizer:
    def __init__(self, x_range, y_range):
        self.x_range = x_range
        self.y_range = y_range

    def visualize_mobility(self, graph, title="Mobility Visualization"):
        plt.figure(figsize=(10, 10))

        user_nodes = graph.get_user_nodes()
        user_x = [node.x for node in user_nodes]
        user_y = [node.y for node in user_nodes]
        plt.scatter(user_x, user_y, c='blue', label='Users')

        fog_nodes = graph.get_moving_fog_nodes()
        fog_x = [node.x for node in fog_nodes]
        fog_y = [node.y for node in fog_nodes]
        plt.scatter(fog_x, fog_y, c='red', label='Fog Nodes')

        plt.xlim(0, self.x_range)
        plt.ylim(0, self.y_range)

        plt.title(title)
        plt.legend()
        plt.show()

    def plot_metrics(self, migration_counts_per_step, deadline_misses_per_step):
        plt.figure(figsize=(10, 6))

        plt.plot(migration_counts_per_step, label="Migrations Count", color='b')

        plt.plot(deadline_misses_per_step, label="Deadline Misses", color='r')

        plt.xlabel("Step")
        plt.ylabel("Count")
        plt.title("Migrations and Deadline Misses Over Time")
        plt.legend()

        plt.show()
