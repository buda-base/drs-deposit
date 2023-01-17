"""
Created on July 26, 2018

@author: jimk
"""
import time


class ProgressTimer:
    """
    Class to calculate counts and rates
    """
    etStart: time
    calls: int
    total: int
    print_interval: int

    def __init__(self, total, interval=15):
        self.calls = 0
        self.print_interval = interval
        self.total = total
        self.etStart = None

    def tick(self):
        """
        Increments the counter, prints rate info
        :return:
        """
        if self.calls == 0:
            self.etStart = time.perf_counter()
        self.calls += 1
        if self.calls % self.print_interval == 0:
            y = time.perf_counter()
            print(" %d calls ( %3.2f %%).  Rate: %5.2f /sec"
                  % (self.calls, 100 * self.calls / self.total, self.print_interval / (y - self.etStart)))
            self.etStart = y
