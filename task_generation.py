from task_systems import PeriodicTask, PeriodicTaskSystem
from random import choice


def generate_task_system(phases, periods, costs, relative_deadlines, num_tasks):
    """
    Randomly generate :num_tasks: tasks by choosing phases, periods, costs, and relative deadlines (uniformly) randomly
    from the corresponding parameter.

    :param phases: set of possible phases
    :param periods: set of possible periods
    :param costs: set of possible costs
    :param relative_deadlines: set of possible relative deadlines
    :param num_tasks: number of tasks to generate
    :return: randomly generated task system
    """
    return PeriodicTaskSystem([PeriodicTask(phase=choice(phases), period=choice(periods),
                                            cost=choice(costs), relative_deadline=choice(relative_deadlines),
                                            id=k)
                               for k in range(num_tasks)])


def read_task_system_from_file(filename):
    """
    Read a task system from a text file.

    :param filename: name of file to read from
    :return: task system read from file
    """

    tasks = []
    with open(filename, "r") as file:
        for line in file.readlines():
            phase, period, cost, relative_deadline, task_number = eval(line)
            tasks.append(PeriodicTask(phase=phase, period=period, cost=cost,
                                      relative_deadline=relative_deadline, id=task_number))
    return PeriodicTaskSystem(tasks)


def write_task_system_to_file(filename, task_system):
    """
    Write a task system to a text file.

    :param filename: name of file to write to
    :param task_system: task system to write to file
    """

    with open(filename, "w") as file:
        for task in task_system:
            file.write(f"{(task.phase, task.period, task.cost, task.relative_deadline, task.id)}\n")
