from math import inf
from priority_functions import *
from random import randint, seed
from task_generation import generate_task_system, read_task_system_from_file, write_task_system_to_file
from task_scheduling import UniprocessorScheduler
from task_systems import PeriodicTask, PeriodicTaskSystem, Job
from schedule_plotting import *
from time import time
import matplotlib.pyplot as plt
from cProfile import run

INFLATION = 1

t1 = PeriodicTask(period=6 * INFLATION, cost=1 * INFLATION, id=0)
t2 = PeriodicTask(period=8 * INFLATION, cost=2 * INFLATION, id=1)
t3 = PeriodicTask(period=12 * INFLATION, cost=4 * INFLATION, id=2)
task_system = PeriodicTaskSystem([t1, t2, t3])

scheduler = UniprocessorScheduler(priority_function=priority_RM)
start = time()
schedule = scheduler.generate_schedule(task_system=task_system, final_time=24 * INFLATION)[0]
print(schedule)

plot_uniprocessor_schedule(schedule)
plt.tight_layout()
plt.show()
