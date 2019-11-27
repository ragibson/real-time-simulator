from task_systems import PeriodicTask, PeriodicTaskSystem
from random import choice


def generate_task_system(phases, periods, costs, relative_deadlines, num_tasks):
    return PeriodicTaskSystem([PeriodicTask(phase=choice(phases), period=choice(periods),
                                            cost=choice(costs), relative_deadline=choice(relative_deadlines),
                                            id=k)
                               for k in range(num_tasks)])


def read_task_system_from_file(filename):
    tasks = []
    with open(filename, "r") as file:
        for line in file.readlines():
            phase, period, cost, relative_deadline, task_number = eval(line)
            tasks.append(PeriodicTask(phase=phase, period=period, cost=cost,
                                      relative_deadline=relative_deadline, id=task_number))
    return PeriodicTaskSystem(tasks)


def write_task_system_to_file(filename, task_system):
    with open(filename, "w") as file:
        for task in task_system:
            file.write(f"{(task.phase, task.period, task.cost, task.relative_deadline, task.id)}\n")
