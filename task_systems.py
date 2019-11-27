from functools import reduce
from math import floor, gcd

_DEBUG = True


def _lcm(a, b):
    return abs(a * b) // gcd(a, b)


class Job:
    def __init__(self, release, cost, deadline, task):
        self.release = release
        self.cost = cost
        self.remaining_cost = cost
        self.deadline = deadline  # absolute deadline
        self.task = task

    def __str__(self):
        return f"Job (release={self.release}, cost={self.cost}, deadline={self.deadline}) from {self.task}"


class PeriodicTask:
    def __init__(self, phase=None, period=None, cost=None, relative_deadline=None, id=None):
        if phase is None:
            self.phase = 0
        else:
            self.phase = phase

        self.period = period
        self.cost = cost
        self.id = id

        if relative_deadline is None:
            self.relative_deadline = self.period
        else:
            self.relative_deadline = relative_deadline

        if self.period <= 0 or self.period is None:
            raise ValueError("Task period must be non-negative!")

        if self.relative_deadline <= 0:
            raise ValueError("Task relative deadline must be non-negative!")

        if self.cost <= 0 or self.cost is None:
            raise ValueError("Task cost must be non-negative!")

        if _DEBUG:
            assert all(x is not None for x in [self.phase, self.period, self.cost])

    def __str__(self):
        id_string = "" if self.id is None else f"{self.id} "

        if self.phase != 0:
            return f"Task {id_string}(phi={self.phase}, T={self.period}, C={self.cost}, D={self.relative_deadline})"

        if self.period == self.relative_deadline:
            return f"Task {id_string}(T={self.period}, C={self.cost})"

        return f"Task {id_string}(T={self.period}, C={self.cost}, D={self.relative_deadline})"

    def utilization(self):
        return self.cost / self.period

    def density(self):
        return self.cost / self.relative_deadline

    def generate_jobs(self, final_time):
        num_releases = floor((final_time - self.phase - self.relative_deadline) / self.period) + 1
        jobs = [Job(
            release=self.phase + k * self.period,
            cost=self.cost,
            deadline=self.phase + k * self.period + self.relative_deadline,
            task=self
        ) for k in range(num_releases)]

        if _DEBUG:
            if len(jobs) == 0:
                assert final_time < self.phase + self.relative_deadline
            else:
                assert jobs[-1].deadline <= final_time < jobs[-1].release + self.period + self.relative_deadline

        return jobs


class PeriodicTaskSystem:
    def __init__(self, initial_tasks=None):
        if initial_tasks is None:
            self.tasks = []
            self.hyperperiod = 0
        else:
            self.tasks = initial_tasks.copy()
            self._update_hyperperiod()

    def __iter__(self):
        return iter(self.tasks)

    def add_tasks(self, new_tasks):
        self.tasks.extend(new_tasks)
        self._update_hyperperiod()

    def utilization(self):
        return sum(task.utilization() for task in self.tasks)

    def density(self):
        return sum(task.density() for task in self.tasks)

    def _update_hyperperiod(self):
        if len(self.tasks) == 0:
            self.hyperperiod = 0
        else:
            self.hyperperiod = reduce(_lcm, [task.period for task in self.tasks])

    def __str__(self):
        return f"Task System with {len(self.tasks)} tasks, hyperperiod={self.hyperperiod}" + \
               "".join(f"\n  {task}" for task in self.tasks)
