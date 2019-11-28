from math import inf

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


priority_RM = handle_overhead(_RM)
priority_DM = handle_overhead(_DM)
priority_static = handle_overhead(_static)
priority_EDF = handle_overhead(_EDF)
priority_LLF = handle_overhead(_LLF)

priority_NP_RM = make_nonpreemptive(priority_RM)
priority_NP_DM = make_nonpreemptive(priority_DM)
priority_NP_static = make_nonpreemptive(priority_static)
priority_NP_EDF = make_nonpreemptive(priority_EDF)
priority_NP_LLF = make_nonpreemptive(priority_LLF)
