from task_generation import *
from priority_functions import *
from task_scheduling import *
from task_systems import *
from schedule_plotting import *
from time import time
import matplotlib.pyplot as plt

t1 = PeriodicTask(period=100, cost=30, id=0)
t2 = PeriodicTask(period=100, cost=30, id=1)
t3 = PeriodicTask(period=100, cost=30, id=2)
t4 = PeriodicTask(period=100, cost=30, id=3)
t5 = PeriodicTask(period=100, cost=30, id=4)
t6 = PeriodicTask(period=100, cost=30, id=5)
t7 = PeriodicTask(period=100, cost=30, id=6)
t8 = PeriodicTask(period=100, cost=30, id=7)
task_system = PeriodicTaskSystem([t1, t2, t3, t4, t5, t6, t7, t8])

scheduler = MultiprocessorScheduler(priority_function=priority_LLF,
                                    processors=[Processor(),
                                                Processor(),
                                                Processor()],
                                    restrict_migration=True)

start = time()
schedules, schedulable = scheduler.generate_schedule(task_system=task_system)
print(f"Took {time() - start:.2f} s")

print(schedulable)

plt.figure()
plot_multiprocessor_schedule_per_processor(schedules)
plt.tight_layout()
# plt.show()

plt.figure()
plot_multiprocessor_schedule_per_task(schedules)
plt.tight_layout()
plt.show()
