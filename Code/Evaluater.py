import time
from Config import Config

'''
    The Evaluator class is used to track and log the performance of the system in handling tasks. 
    It monitors metrics such as the number of tasks that are migrated between nodes, how many tasks miss
    their deadlines, and the distribution of tasks among fog nodes. 
    This information is critical for assessing the efficiency and effectiveness of the task assignment strategies
    used in the network. The Evaluator helps in identifying areas for improvement in the system's performance.
'''


class Evaluator:
    migrations_count = 0
    deadline_misses = 0
    total_tasks = 0
    cloud_tasks = 0
    fog_node_task_counts = {}
    migration_counts_per_step = []
    deadline_misses_per_step = []
    current_step_migrations = 0
    current_step_deadline_misses = 0

    @staticmethod
    def log_evaluation():
        Evaluator.log_fog_node_task_counts()
        print("\nMetrics:")
        print(f"Total migrations:\t\t{Evaluator.migrations_count}")
        print(f"Total deadline misses:\t{Evaluator.deadline_misses}")
        print(f"Total cloud tasks:\t\t{Evaluator.cloud_tasks}")
        print(f"Total tasks:\t\t\t{Evaluator.total_tasks}")
        Evaluator.log_short_evaluation()

    @staticmethod
    def log_short_evaluation():
        if Evaluator.total_tasks != 0:
            print(f"Migration ratio: \t\t{'{:.3f}'.format(Evaluator.migrations_count * 100 / Evaluator.total_tasks)}%")
            print(f"Deadline miss ratio:\t{'{:.3f}'.format(Evaluator.deadline_misses * 100 / Evaluator.total_tasks)}%")

    @staticmethod
    def log_fog_node_task_counts():
        print("\nTasks count assigned to each Fog Node:")
        average = 0
        min = float('inf')
        max = 0
        for node_id, task_count in Evaluator.fog_node_task_counts.items():
            print(f"\tFog Node {node_id}:\t{task_count}")
            average += task_count
            if task_count < min:
                min = task_count
            if task_count > max:
                max = task_count
        average /= len(Evaluator.fog_node_task_counts)
        print(f"\tAverage tasks per Fog Node:\t\t{average}")
        print(f"\tMin, Max tasks per Fog Node:\t{min}, {max}")

    @staticmethod
    def track_step_metrics():
        Evaluator.migration_counts_per_step.append(Evaluator.current_step_migrations)
        Evaluator.deadline_misses_per_step.append(Evaluator.current_step_deadline_misses)
        Evaluator.current_step_migrations = 0
        Evaluator.current_step_deadline_misses = 0

    @staticmethod
    def update_task_count(id):
        if id not in Evaluator.fog_node_task_counts:
            Evaluator.fog_node_task_counts[id] = 0
        Evaluator.fog_node_task_counts[id] += 1

    @staticmethod
    def increment_migrations():
        Evaluator.current_step_migrations += 1
        Evaluator.migrations_count += 1

    @staticmethod
    def increment_deadline_misses():
        Evaluator.current_step_deadline_misses += 1
        Evaluator.deadline_misses += 1


def timer_log(func):
    if not Config.ENABLE_TIMER_LOG:
        return func

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        request_time = time.perf_counter() - start
        threshold = Config.TIMER_LOG_THRESHOLD
        if request_time > threshold:
            print(f"\033[95mProcess time: {request_time} for method {func.__name__}\033[0m")
        return result

    return wrapper
