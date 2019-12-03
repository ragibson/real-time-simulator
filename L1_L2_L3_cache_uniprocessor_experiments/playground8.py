import pickle
from priority_functions import *
from task_scheduling import *
from time import time
import numpy as np
from breakdown_utilization_experiments.breakdown_density import *

print("NP_DM")
priority_function = priority_NP_DM

random_task_systems = pickle.load(open("../breakdown_utilization_experiments/uniprocessor_25_random_10task_systems.p",
                                       "rb"))
scheduler = UniprocessorScheduler(priority_function=priority_function,
                                  processor=Processor(schedule_cost=4, dispatch_cost=1,
                                                      preemption_cost=2, cache_warmup_time=65,
                                                      warm_cache_rate=50))

breakdown_utilizations = []

start = time()
for task_system in random_task_systems:
    v = uniprocessor_breakdown_density(scheduler, task_system)
    breakdown_utilizations.append(v)
    print(v)

print(breakdown_utilizations)
print(np.mean(breakdown_utilizations))
