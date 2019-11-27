from math import inf


def _RM(job, t):
    return job.task.period


def _DM(job, t):
    return job.task.relative_deadline


def _static(job, t):
    if job.task.id is None:
        raise ValueError(f"Cannot use task ID {job.task.id} as priority!")
    return job.task.id


def _EDF(job, t):
    return job.deadline - t


def _LLF(job, t):
    return job.deadline - t - job.remaining_cost


def handle_overhead(priority_function):
    def overhead_variant(job, t):
        if job.remaining_overhead > 0:
            return -inf
        return priority_function(job, t)

    return overhead_variant


def make_nonpreemptive(priority_function):
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
