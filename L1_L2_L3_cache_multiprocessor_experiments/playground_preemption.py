import pickle
from priority_functions import *
from task_scheduling import *
from time import time
import numpy as np
from breakdown_utilization_experiments.breakdown_density import *
import sys

priority_name = sys.argv[1]
preemption_cost = int(sys.argv[2])
t_warmup = 16000
r_max = 5
restrict_migration = False

if r_max == 1:
    t_warmup = None

if priority_name == "G-EDF":
    priority_function = priority_EDF
elif priority_name == "G-LLF":
    priority_function = priority_LLF
elif priority_name == "G-RM":
    priority_function = priority_RM
elif priority_name == "G-DM":
    priority_function = priority_DM
elif priority_name == "GR-EDF":
    priority_function = priority_EDF
    restrict_migration = True
elif priority_name == "GR-LLF":
    priority_function = priority_LLF
    restrict_migration = True
elif priority_name == "GR-RM":
    priority_function = priority_RM
    restrict_migration = True
elif priority_name == "GR-DM":
    priority_function = priority_DM
    restrict_migration = True
elif priority_name == "G-NP_EDF":
    priority_function = priority_NP_EDF
elif priority_name == "G-NP_LLF":
    priority_function = priority_NP_LLF
elif priority_name == "G-NP_RM":
    priority_function = priority_NP_RM
elif priority_name == "G-NP_DM":
    priority_function = priority_NP_DM
else:
    raise ValueError(f"priority {priority_name} not supported!")

random_task_systems = pickle.load(open("breakdown_utilization_experiments/uniprocessor_25_random_10task_systems.p",
                                       "rb"))
scheduler = MultiprocessorScheduler(priority_function=priority_function,
                                    processors=[Processor(schedule_cost=4, dispatch_cost=1,
                                                          preemption_cost=preemption_cost, cache_warmup_time=t_warmup,
                                                          warm_cache_rate=r_max),
                                                Processor(schedule_cost=4, dispatch_cost=1,
                                                          preemption_cost=preemption_cost, cache_warmup_time=t_warmup,
                                                          warm_cache_rate=r_max),
                                                Processor(schedule_cost=4, dispatch_cost=1,
                                                          preemption_cost=preemption_cost, cache_warmup_time=t_warmup,
                                                          warm_cache_rate=r_max),
                                                Processor(schedule_cost=4, dispatch_cost=1,
                                                          preemption_cost=preemption_cost, cache_warmup_time=t_warmup,
                                                          warm_cache_rate=r_max)
                                                ],
                                    restrict_migration=restrict_migration)

breakdown_utilizations = []

start = time()
for task_system in random_task_systems:
    v = multiprocessor_breakdown_density(scheduler, task_system)
    breakdown_utilizations.append(v)
    # print(v)

print(priority_name, t_warmup, r_max, preemption_cost, np.mean(breakdown_utilizations))
