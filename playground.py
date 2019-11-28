from task_generation import *
from priority_functions import *
from task_scheduling import UniprocessorScheduler, Processor
from task_systems import PeriodicTask, PeriodicTaskSystem
from schedule_plotting import *
from time import time
import matplotlib.pyplot as plt

task_system = PeriodicTaskSystem([PeriodicTask(phase=0, period=10, cost=5, relative_deadline=20, id=0),
                                  PeriodicTask(phase=0, period=20, cost=5, relative_deadline=25, id=1)])

print(task_system)

scheduler = UniprocessorScheduler(priority_function=priority_EDF,
                                  processor=Processor())
start = time()
schedule, schedulable = scheduler.generate_schedule(task_system=task_system)
print(f"Took {time() - start:.2f} s")
print(schedule)
print(schedulable)

plot_uniprocessor_schedule(schedule)
plt.tight_layout()
plt.show()
