from functools import reduce
from math import floor, gcd, inf

_DEBUG = True


def _lcm(a, b):
    return abs(a * b) // gcd(a, b)


class Job:
    """A released job from a task"""

    def __init__(self, release, cost, deadline, task):
        """
        :param release: release time
        :param cost: execution cost
        :param deadline: deadline
        :param task: task that the job is released from
        """
        self.release = release
        self.cost = cost
        self.remaining_overhead = 0  # overhead is essentially nonpreemptive execution cost
        self.remaining_cost = cost
        self.deadline = deadline  # absolute deadline
        self.task = task
        self.started = False

    def decrement_remaining_cost(self, execution_rate):
        """Decrease the remaining execution cost with the current cache rate, preferring to complete overhead first"""
        self.started = True
        if self.has_remaining_overhead():
            # overhead always executes at "full speed"
            self.remaining_overhead -= 1
        else:
            self.remaining_cost -= execution_rate

    def has_started(self):
        """Returns whether the job has started execution"""
        if _DEBUG:
            if self.remaining_cost < self.cost or self.remaining_overhead > 0:
                assert self.started
        return self.started

    def has_remaining_overhead(self):
        return self.remaining_overhead > 0

    def has_completed(self):
        if self.remaining_cost <= 0:
            if _DEBUG:
                assert self.remaining_overhead <= 0
            return True
        return False

    def __str__(self):
        return f"Job (release={self.release}, cost={self.cost}, deadline={self.deadline}) from {self.task}"


class PeriodicTask:
    """A periodic task that can release jobs"""

    def __init__(self, phase=None, period=None, cost=None, relative_deadline=None, id=None):
        """
        :param phase: phase of task. Defaults to zero
        :param period: period of task
        :param cost: execution cost of task
        :param relative_deadline: relative deadline of task. Defaults to period
        :param id: task ID
        """

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

        if self.period is None or self.period <= 0:
            raise ValueError("Task period must be non-negative!")

        if self.relative_deadline <= 0:
            raise ValueError("Task relative deadline must be non-negative!")

        if self.cost is None or self.cost <= 0:
            raise ValueError("Task cost must be non-negative!")

        if self.period == inf and self.relative_deadline == inf:
            raise ValueError("One-shot job (infinite period) cannot have infinite relative deadline!")

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
        """Generate all jobs released by :final_time:"""

        if self.period != inf:
            # num_releases = floor((final_time - self.phase - self.relative_deadline) / self.period) + 1
            num_releases = floor((final_time - self.phase) / self.period) + 1
            jobs = [Job(
                release=self.phase + k * self.period,
                cost=self.cost,
                deadline=self.phase + k * self.period + self.relative_deadline,
                task=self
            ) for k in range(num_releases)]
        else:
            jobs = [Job(
                release=self.phase,
                cost=self.cost,
                deadline=self.phase + self.relative_deadline,
                task=self
            )]

        if _DEBUG:
            if len(jobs) == 0:
                assert final_time < self.phase + self.relative_deadline
            else:
                assert jobs[-1].release <= final_time < jobs[-1].release + self.period + self.relative_deadline

        return jobs


class PeriodicTaskSystem:
    """System of multiple periodic tasks"""

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
            self.hyperperiod = reduce(_lcm, [task.period for task in self.tasks if task.period != inf])

    def __str__(self):
        return f"Task System with {len(self.tasks)} tasks, hyperperiod={self.hyperperiod}" + \
               "".join(f"\n  {task}" for task in self.tasks)
