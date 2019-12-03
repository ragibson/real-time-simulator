from math import ceil, floor, inf
from task_systems import PeriodicTask

"""
This module contains priority functions for real time schedule.

Each function takes a job :job: and time :t: as parameters and returns the associated priority.
"""


def _RM(job, t):
    """Rate-Monotonic assigns higher priority to jobs with smaller periods"""
    return job.task.period


def _DM(job, t):
    """Deadline-Monotonic assigns higher priority to jobs with smaller relative deadlines"""
    return job.task.relative_deadline


def _static(job, t):
    """Static priority assignment according to task IDs (smaller is higher priority)"""
    if job.task.id is None:
        raise ValueError(f"Cannot use task ID {job.task.id} as priority!")
    return job.task.id


def _EDF(job, t):
    """Earliest-Deadline-First assigns higher priority to jobs with earlier deadlines"""
    return job.deadline - t


def _LLF(job, t):
    """
    Least-Laxity-First assigns higher priority to jobs with lesser laxity (slack).

    The laxity (slack) of a job of a job with deadline d at time t is equal to
        deadline - t - (time required to complete the remaining portion of the job)
    """
    return job.deadline - t - job.remaining_cost


def handle_overhead(priority_function):
    """Augment a priority function by executing overhead nonpreemptively before any non-overhead execution cost"""

    def overhead_variant(job, t):
        if job.remaining_overhead > 0:
            return -inf
        return priority_function(job, t)

    return overhead_variant


def make_nonpreemptive(priority_function):
    """Augment a priority function by forcing nonpreemptive execution"""

    def nonpreemptive_variant(job, t):
        if job.remaining_cost < job.cost:
            return -inf
        return priority_function(job, t)

    return nonpreemptive_variant


def _Pfair(job, t, eps=1e-7):
    if job.remaining_overhead > 0:
        raise ValueError("Pfair implementation does not support overhead!")

    if job.remaining_cost == job.deadline - t:
        return -inf  # job must run immediately, successor bit insufficient for tiebreak here

    task = job.task
    phase, period, cost, relative_deadline, id = task.phase, task.period, task.cost, task.relative_deadline, task.id
    weight = max(cost / period, cost / relative_deadline)
    subtask_idx = job.cost - job.remaining_cost + 1
    pseudorelease = phase + floor((subtask_idx - 1) / weight)
    pseudodeadline = phase + ceil(subtask_idx / weight)
    successor_bit = ceil(subtask_idx / weight) - floor(subtask_idx / weight)
    if weight == 1:
        group_deadline = phase + relative_deadline  # does not imply infinite deadline when D_i != T_i
    else:
        group_deadline = phase + ceil(ceil(ceil(subtask_idx / weight) * (1 - weight)) / (1 - weight))

    priority = pseudodeadline  # earlier deadline is higher priority
    priority -= successor_bit / 2  # deadline ties broken in favor of job with successor bit
    priority -= group_deadline * eps  # further ties broken in favor of *later* group deadline
    return priority


priority_RM = handle_overhead(_RM)
priority_DM = handle_overhead(_DM)
priority_static = handle_overhead(_static)
priority_EDF = handle_overhead(_EDF)
priority_LLF = handle_overhead(_LLF)
priority_Pfair = _Pfair  # overhead cannot be supported without changing Pfair's quantum size

priority_NP_RM = make_nonpreemptive(priority_RM)
priority_NP_DM = make_nonpreemptive(priority_DM)
priority_NP_static = make_nonpreemptive(priority_static)
priority_NP_EDF = make_nonpreemptive(priority_EDF)
priority_NP_LLF = make_nonpreemptive(priority_LLF)
