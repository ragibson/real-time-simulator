from task_generation import *
from priority_functions import *
from task_scheduling import *
from task_systems import *
from schedule_plotting import *
from time import time
import matplotlib.pyplot as plt
from random import choice, randint

MS = 1000


def random_task(id):
    period = MS * choice([2 ** k for k in range(10)])
    cost = randint(1, period)
    relative_deadline = randint(cost, period)
    return PeriodicTask(phase=randint(0, period - 1), period=period,
                        cost=cost, relative_deadline=relative_deadline, id=id)


task_system = PeriodicTaskSystem([random_task(k) for k in range(6)])
while task_system.utilization() > 1:
    task_system = PeriodicTaskSystem([random_task(k) for k in range(6)])

print(task_system.utilization(), task_system.hyperperiod)

scheduler = UniprocessorScheduler(priority_function=priority_LLF)
# scheduler = MultiprocessorScheduler(priority_function=priority_LLF,
#                                     processors=[Processor(),
#                                                 Processor(),
#                                                 Processor()],
#                                     restrict_migration=True)

start = time()
schedules, schedulable = scheduler.generate_schedule(task_system=task_system)
print(f"Took {time() - start:.2f} s")
print("Is schedulable?", schedulable)
