import functools
from cProfile import run
from math import floor, inf
import pickle
from random import choice, randint
import matplotlib.pyplot as plt
from multiprocessing import cpu_count, Pool
from priority_functions import *
from schedule_plotting import *
from task_scheduling import *
from task_systems import *
from time import time
import sys


def reweight_task_system(w, task_system):
    return PeriodicTaskSystem([PeriodicTask(phase=task.phase, period=task.period, cost=max(1, floor(w * task.cost)),
                                            relative_deadline=task.relative_deadline, id=task.id)
                               for task in task_system])


def uniprocessor_breakdown_density(scheduler, task_system, density_tolerance=1e-3, warm_cache_rate=50):
    @functools.lru_cache(maxsize=10)
    def test_weight(weight):
        reweighted_task_system = reweight_task_system(weight, task_system)
        _, schedulable = scheduler.generate_schedule(reweighted_task_system)
        return reweighted_task_system, schedulable, reweighted_task_system.density()

    weight = warm_cache_rate * (1 + len(task_system) / min(task.period for task in task_system)) \
             / task_system.utilization()
    weight_step = weight

    last_schedulable = False
    last_density = inf
    while True:
        reweighted_task_system, schedulable, new_density = test_weight(weight)
        # print(f"trying weight {weight} density {new_density} schedulable? {schedulable}")
        if schedulable and not last_schedulable and abs(new_density - last_density) < density_tolerance:
            return new_density

        last_density = new_density
        last_schedulable = schedulable

        if not schedulable:
            weight -= weight_step
            weight_step /= 2
        else:
            weight += weight_step


def multiprocessor_breakdown_density(scheduler, task_system, utilization_tolerance=1e-3, warm_cache_rate=50):
    @functools.lru_cache(maxsize=10)
    def test_weight(weight):
        reweighted_task_system = reweight_task_system(weight, task_system)
        _, schedulable = scheduler.generate_schedule(reweighted_task_system)
        return reweighted_task_system, schedulable, reweighted_task_system.density()

    weight = warm_cache_rate * (scheduler.num_processors + len(task_system) / min(task.period
                                                                                  for task in
                                                                                  task_system)) / task_system.utilization()
    weight_step = weight

    last_schedulable = False
    last_density = inf
    while True:
        reweighted_task_system, schedulable, new_density = test_weight(weight)

        if last_density == inf:
                assert not schedulable

        # print(f"trying weight {weight} density {new_density} schedulable? {schedulable}")
        if schedulable and not last_schedulable and abs(new_density - last_density) < utilization_tolerance:
            return new_density

        last_density = new_density
        last_schedulable = schedulable

        if not schedulable:
            weight -= weight_step
            weight_step /= 2
        else:
            weight += weight_step
