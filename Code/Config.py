"""
    Configuration class for setting up various parameters for the simulation.
    This class contains static configuration values that can be adjusted to modify the behavior of the system.

    Attributes:
        FOG_COVERAGE_RADIUS (int): The radius of coverage for fog nodes.
        CLOUD_COVERAGE_RADIUS (int): The radius of coverage for cloud nodes.
        CLOUD_X (int): The X-coordinate of the cloud node.
        CLOUD_Y (int): The Y-coordinate of the cloud node.
        TIMESLOT_LENGTH (int): The length of each timeslot in the simulation.
        SIMULATION_DURATION (int): The total duration of the simulation.
        PACKET_COST_PER_METER (float): The cost per meter for packet transmission.
        TASK_COST_PER_METER (float): The cost per meter for task transmission.
        CLOUD_POWER (int): The power available at the cloud node.
        FOG_POWER (int): The power available at a fog node.
        ENABLE_TIMER_LOG (bool): Flag to enable logging of time-consuming processes.
        TIMER_LOG_THRESHOLD (int): Threshold time in seconds for logging a process.
        ENABLE_VISUALIZATION (bool): Flag to enable visualization of the simulation.
        X_RANGE (int): The X-axis range for visualization.
        Y_RANGE (int): The Y-axis range for visualization.
        OFFLINE_MODE (bool): Flag to enable offline mode, affecting the data source.
        IS_IMAN (bool): Flag indicating if the simulation is running under a specific configuration.
        RUNNING_MODES (list): A list of possible running modes for the simulation.
        RUNNING_MODE (str): The currently selected running mode.
"""


class Config:
    FOG_COVERAGE_RADIUS = 3
    CLOUD_COVERAGE_RADIUS = 100
    CLOUD_X = 50
    CLOUD_Y = 50

    TIMESLOT_LENGTH = 1
    SIMULATION_DURATION = 199

    PACKET_COST_PER_METER = 0.001
    TASK_COST_PER_METER = 0.005
    MIGRATION_OVERHEAD = 0.01
    CLOUD_PROCESSING_OVERHEAD = 0.5

    Q_LEARNING_NEAREST_ACTION_DISTANCE_THRESHOLD = 10
    Q_LEARNING_NEAREST_STATE_DISTANCE_THRESHOLD = 10

    CLOUD_POWER = 30
    FOG_POWER = 15

    ENABLE_TIMER_LOG = True
    TIMER_LOG_THRESHOLD = 4
    DISCRETE_LEVELS = 5

    ENABLE_VISUALIZATION = False
    ENABLE_VISUALIZATION_METRICS = True
    X_RANGE = 10
    Y_RANGE = 10

    TASK_QUEUE_SIZE = 20

    OFFLINE_MODE = True
    IS_IMAN = False

    RUNNING_MODE_RANDOM = "random"
    RUNNING_MODE_Q_LEARNING = "q_learning"
    RUNNING_MODE_HEURISTIC = "heuristic"
    RUNNING_MODE_A3C = "a3c"
    RUNNING_MODE_FULLY_RANDOM = "fully_random"

    RUNNING_MODE = "q_learning"