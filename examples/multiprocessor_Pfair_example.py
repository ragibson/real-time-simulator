from priority_functions import *
from task_scheduling import *
from task_systems import *
from schedule_plotting import *
import matplotlib.pyplot as plt

t1 = PeriodicTask(phase=0, period=100, cost=60, relative_deadline=100, id=0)
t2 = PeriodicTask(phase=10, period=100, cost=60, relative_deadline=80, id=1)
t3 = PeriodicTask(phase=20, period=100, cost=60, relative_deadline=60, id=2)
t4 = PeriodicTask(phase=30, period=100, cost=40, relative_deadline=60, id=3)
t5 = PeriodicTask(phase=40, period=100, cost=40, relative_deadline=60, id=4)

task_system = PeriodicTaskSystem([t1, t2, t3, t4, t5])
print(task_system.utilization(), task_system.density())

scheduler = MultiprocessorScheduler(priority_function=priority_Pfair,
                                    processors=[Processor(),
                                                Processor(),
                                                Processor()],
                                    restrict_migration=False)

schedules, schedulable = scheduler.generate_schedule(task_system=task_system, final_time=100)

plot_multiprocessor_schedule_per_processor(schedules)
plt.savefig("Pfair_multiprocessor_example1.pdf")
plt.close()
plot_external_legend(schedules, entity="Task", filename="EDF_multiprocessor_legend1.pdf")

plot_multiprocessor_schedule_per_task(schedules)
plt.savefig("Pfair_multiprocessor_example2.pdf")
plt.close()
plot_external_legend(schedules, entity="Processor", filename="EDF_multiprocessor_legend2.pdf")
