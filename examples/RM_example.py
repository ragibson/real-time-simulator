from priority_functions import *
from task_scheduling import UniprocessorScheduler
from task_systems import PeriodicTask, PeriodicTaskSystem
from schedule_plotting import *
import matplotlib.pyplot as plt

t1 = PeriodicTask(period=6, cost=1, id=0)
t2 = PeriodicTask(period=8, cost=2, id=1)
t3 = PeriodicTask(period=12, cost=4, id=2)
task_system = PeriodicTaskSystem([t1, t2, t3])

scheduler = UniprocessorScheduler(priority_function=priority_RM)
schedule = scheduler.generate_schedule(task_system=task_system)[0]

plot_uniprocessor_schedule(schedule)
plt.tight_layout()
plt.savefig("RM_uniprocessor_example.pdf")
