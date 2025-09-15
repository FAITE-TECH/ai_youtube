import numpy as np

class EpsilonGreedy:
    def __init__(self, n_arms, eps=0.1):
        self.n = n_arms
        self.eps = eps
        self.counts = np.zeros(n_arms)
        self.values = np.zeros(n_arms)
    def select(self):
        if np.random.rand() < self.eps:
            return np.random.randint(0, self.n)
        return int(np.argmax(self.values))
    def update(self, arm, reward):
        self.counts[arm] += 1
        n = self.counts[arm]
        self.values[arm] += (reward - self.values[arm]) / n
    def allocation(self):
        vals = np.clip(self.values, 1e-6, None)
        alloc = vals / vals.sum() if vals.sum()>0 else np.ones(self.n)/self.n
        return alloc.tolist()
