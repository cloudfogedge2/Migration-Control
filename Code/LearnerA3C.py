
from Learner import *


class LearnerA3C(Learner):
    # This class is used to manage the learning process of the A3C algorithm
    def __init__(self, name):
        super().__init__(name)
        self.discount_factor = 0.99
        self.learning_rate = 0.01



    def update_q_table(self, state, action, reward, next_state):
        # The update formula is different from Q-Learning:
        # Q(s, a) = Q(s, a) + alpha * (R + gamma * V(s') - Q(s, a))
        # V(s') is the value of the next state
        q_value = self.get_q_value(state, action, find_nearest_action=True)
        next_state_value = self.get_state_value(next_state)
        q_value += self.learning_rate * (reward + self.discount_factor * next_state_value - q_value)
        self.q_table[state][action] = q_value


    def get_state_value(self, state):
        value = 0
        if state not in self.q_table:
            return 0
        for action in self.q_table[state]:
            value += self.q_table[state][action]
        return value/len(self.q_table[state])

