from priority_functions import *
from task_scheduling import *
from task_systems import *
from schedule_plotting import *
import matplotlib.pyplot as plt

task_system = PeriodicTaskSystem([PeriodicTask(period=100, cost=30, id=k) for k in range(7)])

scheduler = MultiprocessorScheduler(priority_function=priority_LLF,
                                    processors=[Processor(),
                                                Processor(),
                                                Processor()],
                                    restrict_migration=False)
schedules, schedulable = scheduler.generate_schedule(task_system=task_system)

plt.figure()
plot_multiprocessor_schedule_per_processor(schedules)
plt.tight_layout()
plt.figure()
plot_multiprocessor_schedule_per_task(schedules)
plt.tight_layout()
plt.show()

scheduler = MultiprocessorScheduler(priority_function=priority_LLF,
                                    processors=[Processor(),
                                                Processor(),
                                                Processor()],
                                    restrict_migration=True)
schedules, schedulable = scheduler.generate_schedule(task_system=task_system)

plt.figure()
plot_multiprocessor_schedule_per_processor(schedules)
plt.tight_layout()
plt.figure()
plot_multiprocessor_schedule_per_task(schedules)
plt.tight_layout()
plt.show()
