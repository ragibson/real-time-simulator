from task_generation import *
from priority_functions import *
from task_scheduling import *
from task_systems import *
from schedule_plotting import *
from time import time
import matplotlib.pyplot as plt

t1 = PeriodicTask(period=100, cost=50, id=0)
t2 = PeriodicTask(period=100, cost=50, id=1)
t3 = PeriodicTask(period=100, cost=50, id=2)
t4 = PeriodicTask(period=100, cost=50, id=3)
task_system = PeriodicTaskSystem([t1, t2, t3, t4])

scheduler = MultiprocessorScheduler(priority_function=priority_LLF,
                                    processors=[Processor(), Processor()])

start = time()
schedules, schedulable = scheduler.generate_schedule(task_system=task_system)
print(f"Took {time() - start:.2f} s")

print(schedules[0])
print("=======")
print(schedules[1])

plt.figure()
plot_uniprocessor_schedule(schedules[0])
plt.tight_layout()

plt.figure()
plot_uniprocessor_schedule(schedules[1])
plt.tight_layout()
plt.show()
