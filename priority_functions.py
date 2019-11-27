from math import inf


def priority_RM(job, t):
    return job.task.period


def priority_DM(job, t):
    return job.task.relative_deadline


def priority_static(job, t):
    if job.task.id is None:
        raise ValueError(f"Cannot use task ID {job.task.id} as priority!")
    return job.task.id


def priority_EDF(job, t):
    return job.deadline - t


def priority_LLF(job, t):
    return job.deadline - t - job.remaining_cost


def make_nonpreemptive(priority_function):
    def nonpreemptive_variant(job, t):
        if job.remaining_cost < job.cost:
            return -inf
        return priority_function(job, t)

    return nonpreemptive_variant


priority_NP_RM = make_nonpreemptive(priority_RM)
priority_NP_DM = make_nonpreemptive(priority_DM)
priority_NP_static = make_nonpreemptive(priority_static)
priority_NP_EDF = make_nonpreemptive(priority_EDF)
priority_NP_LLF = make_nonpreemptive(priority_LLF)
