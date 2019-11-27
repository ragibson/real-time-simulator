from priority_functions import *
from task_scheduling import UniprocessorScheduler, Processor
from task_systems import PeriodicTask, PeriodicTaskSystem
from schedule_plotting import *
from time import time
import matplotlib.pyplot as plt

INFLATION = 10

t1 = PeriodicTask(phase=0, period=5 * INFLATION, cost=2 * INFLATION, id=0)
t2 = PeriodicTask(phase=0, period=5 * INFLATION, cost=2 * INFLATION, id=1)
task_system = PeriodicTaskSystem([t1, t2])

scheduler = UniprocessorScheduler(priority_function=priority_LLF,
                                  processor=Processor(cold_cache_rate=0.5, cache_warmup_time=3))
start = time()
schedule, schedulable = scheduler.generate_schedule(task_system=task_system, final_time=5 * INFLATION)
print(schedule)
print(schedulable)

plot_uniprocessor_schedule(schedule)
plt.tight_layout()
plt.show()
