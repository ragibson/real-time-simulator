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

# discrete time model with 1 time unit = 1 microsecond
MS = 1000

_POSSIBLE_PERIODS = [MS * 2 ** k for k in range(3, 9)]


def random_task(id=None):
    period = choice(_POSSIBLE_PERIODS)
    phase = randint(0, period - 1)
    cost = randint(1, period - 1)
    relative_deadline = randint(cost, period)
    return PeriodicTask(phase=phase, period=period, cost=cost, relative_deadline=relative_deadline, id=id)


def random_task_system(num_tasks):
    return PeriodicTaskSystem([random_task(id=k) for k in range(num_tasks)])
