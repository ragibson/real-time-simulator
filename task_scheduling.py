import functools
from math import inf

_DEBUG = True


class Processor:
    """Processor that can schedule jobs"""

    def __init__(self, schedule_cost=0, dispatch_cost=0, preemption_cost=0,
                 cache_warmup_time=None, warm_cache_rate=1):
        """
        :param schedule_cost: overhead to schedule a job
        :param dispatch_cost: overhead to dispatch a job
        :param preemption_cost: overhead to preempt/resume a job
        :param cache_warmup_time: time to completely warm up cache
        :param warm_cache_rate: rate of execution when cache is cold
        """
        self.schedule = Schedule()
        self.time = 0

        self.schedule_cost = schedule_cost
        self.dispatch_cost = dispatch_cost
        self.preemption_cost = preemption_cost

        self.cache_warmup_time = cache_warmup_time
        self.warm_cache_rate = warm_cache_rate
        self.execution_rate = warm_cache_rate

    def reset(self):
        self.schedule = Schedule()
        self.time = 0
        self.execution_rate = self.warm_cache_rate

    def last_job_scheduled(self):
        """Returns the last job scheduled or None if processor was idle"""
        if len(self.schedule) > 0:
            last_scheduled_job = self.schedule[-1]
            if last_scheduled_job.end_time == self.time:
                return last_scheduled_job.job
        return None  # idle

    def schedule_job(self, job):
        """Schedule a job for one time unit"""
        if job != self.last_job_scheduled():
            self.execution_rate = 1  # reset cache

            if not job.has_started():
                job.remaining_overhead += self.schedule_cost + self.dispatch_cost
            else:
                job.remaining_overhead += self.dispatch_cost + self.preemption_cost  # resume new job

            if self.last_job_scheduled() is not None:
                job.remaining_overhead += self.preemption_cost  # preempt last job

        self.schedule.add(job, self.time, self.time + 1)
        self.time += 1

        gain_cache_hit_ratio = not job.has_remaining_overhead()
        job.decrement_remaining_cost(self.execution_rate)

        if gain_cache_hit_ratio and self.cache_warmup_time is not None:
            # linearly increase execution rate to warm cache rate by the cache warmup time
            self.execution_rate += ((self.warm_cache_rate - 1) / self.cache_warmup_time)
            if self.execution_rate >= self.warm_cache_rate:
                self.execution_rate = self.warm_cache_rate

        if job.has_completed():
            self.schedule[-1].job_completed = True

    def idle_until(self, t):
        """Idle processor until specified time"""
        if _DEBUG:
            assert t >= self.time
        self.time = t


class Schedule:
    """Sequence of scheduled jobs"""

    def __init__(self):
        self.schedule = []

    def __len__(self):
        return len(self.schedule)

    def __iter__(self):
        return iter(self.schedule)

    def __getitem__(self, item):
        return self.schedule[item]

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        if any(s1.start_time != s2.start_time for s1, s2 in zip(self, other)):
            return False
        if any(s1.end_time != s2.end_time for s1, s2 in zip(self, other)):
            return False
        return all(s1.job.task == s2.job.task for s1, s2 in zip(self, other))

    def __str__(self):
        return "\n".join([str(x) for x in self.schedule])

    def add(self, job, start_time, end_time):
        """Add a job to the schedule"""

        if _DEBUG:
            # With a fully general priority function, we can only schedule one time unit at a time
            assert end_time == start_time + 1

        if len(self.schedule) > 0 and job == self.schedule[-1].job:
            if _DEBUG:
                assert start_time == self.schedule[-1].end_time

            # extend the last scheduled job if this is a continued execution
            self.schedule[-1].end_time = end_time
        else:
            self.schedule.append(ScheduledJob(start_time, end_time, job))


class ScheduledJob:
    """A job scheduled during an interval of time"""

    def __init__(self, start_time, end_time, job):
        self.start_time = start_time
        self.end_time = end_time
        self.job = job
        self.job_completed = False

    def __str__(self):
        return f"{str(self.job)} executing in [{self.start_time}, {self.end_time}]"


class UniprocessorScheduler:
    """Entity that schedules on a single processor"""

    def __init__(self, priority_function, processor=None):
        """
        :param priority_function: job priority function to use
        :param processor: processor to schedule on. Defaults to a zero overhead CPU
        """
        self.priority_function = priority_function
        if processor is None:
            self.CPU = Processor()
        else:
            self.CPU = processor

    def generate_schedule(self, task_system, final_time=None):
        """Generate a schedule for a provided task system"""

        # If no final time is provided, compute the final time required to provably show the task system is schedulable
        if final_time is None:
            if all(task.phase == 0 for task in task_system.tasks) and \
                    all(task.relative_deadline <= task.period for task in task_system.tasks):
                # For synchronous task systems with relative deadlines not exceeding periods, a deadline miss must
                # occur by the hyperperiod
                final_time = task_system.hyperperiod
            else:
                # Result by Leung and Merrill: If a deadline is missed in a periodic task system with
                # utilization <= 1, then it will be missed by time 2*P + max(D_i) + max(s_i)
                final_time = 2 * task_system.hyperperiod + max(task.relative_deadline for task in task_system.tasks) + \
                             max(task.phase for task in task_system.tasks)

        CPU = self.CPU
        CPU.reset()
        released_jobs = []
        remaining_jobs = sorted([job for task in task_system.tasks
                                 for job in task.generate_jobs(final_time)], key=lambda job: -job.release)

        if task_system.utilization() > CPU.warm_cache_rate:
            return CPU.schedule, False  # not schedulable

        while CPU.time < final_time and len(remaining_jobs) + len(released_jobs) > 0:
            if len(released_jobs) != 0:
                job_to_schedule = CPU.last_job_scheduled()
                for job in released_jobs:
                    if job_to_schedule is None or job_to_schedule.has_completed():
                        job_to_schedule = job  # CPU was idle, so choose this job
                    elif self.priority_function(job, CPU.time) + 1e-10 < self.priority_function(job_to_schedule,
                                                                                                CPU.time):
                        # strict inequality here favors continuing execution of previous job and addition of 1e-10
                        # allows for minor handling of floating point errors from the variable execution rate
                        job_to_schedule = job

                CPU.schedule_job(job_to_schedule)

                if job_to_schedule.has_completed():
                    released_jobs.remove(job_to_schedule)

                if CPU.time > job_to_schedule.deadline:
                    return CPU.schedule, False  # not schedulable
            elif len(remaining_jobs) > 0:
                # idle until next job release
                CPU.idle_until(remaining_jobs[-1].release)

            while len(remaining_jobs) > 0 and remaining_jobs[-1].release <= CPU.time:
                released_jobs.append(remaining_jobs.pop())

        if all(job.deadline > final_time for job in remaining_jobs) and \
                all(job.deadline > final_time for job in released_jobs):
            return CPU.schedule, True
        else:
            return CPU.schedule, False


class MultiprocessorScheduler:
    """Entity that schedules on a multiprocessor"""

    def __init__(self, priority_function, processors, restrict_migration=False):
        """
        :param priority_function: job priority function to use
        :param processor: processors to schedule on
        :param restrict_migration: whether job migration is restricted
        """
        self.priority_function = priority_function
        self.CPUs = processors
        self.num_processors = len(processors)
        self.restrict_migration = restrict_migration

    @staticmethod
    def has_idle_processors(CPUs, jobs_to_schedule):
        """Returns whether any of the CPUs are idle with the current set of jobs to schedule"""
        return any(jobs_to_schedule[CPU] is None for CPU in CPUs)

    @staticmethod
    def get_idle_processor(CPUs, jobs_to_schedule):
        """Returns an idle CPU with the current set of jobs to schedule (or None if no such CPU exists)"""
        for CPU in CPUs:
            if jobs_to_schedule[CPU] is None:
                return CPU
        return None

    def generate_schedule(self, task_system, final_time=None):
        """Generate a schedule for a provided task system"""

        if final_time is None:
            if all(task.phase == 0 for task in task_system.tasks) and \
                    all(task.relative_deadline <= task.period for task in task_system.tasks):
                # For synchronous task systems with relative deadlines not exceeding periods, a deadline miss must
                # occur by the hyperperiod
                final_time = task_system.hyperperiod
            else:
                # Result by Leung and Merrill: If a deadline is missed in a periodic task system with
                # utilization <= 1, then it will be missed by time 2*P + max(D_i) + max(s_i)
                final_time = 2 * task_system.hyperperiod + max(task.relative_deadline for task in task_system.tasks) + \
                             max(task.phase for task in task_system.tasks)

        CPUs = self.CPUs
        for CPU in CPUs:
            CPU.reset()
        released_jobs = []
        remaining_jobs = sorted([job for task in task_system.tasks
                                 for job in task.generate_jobs(final_time)], key=lambda job: -job.release)
        migration_restriction = {job: None for job in remaining_jobs}

        if task_system.utilization() > self.num_processors * max(CPU.warm_cache_rate for CPU in CPUs):
            return [CPU.schedule for CPU in CPUs], False  # not schedulable

        while CPUs[0].time < final_time and len(remaining_jobs) + len(released_jobs) > 0:
            if len(released_jobs) != 0:
                jobs_to_schedule = {CPU: CPU.last_job_scheduled() for CPU in CPUs}

                for CPU in CPUs:
                    if jobs_to_schedule[CPU] is None or jobs_to_schedule[CPU].has_completed():
                        jobs_to_schedule[CPU] = None

                if self.restrict_migration:
                    # Handle restricted migration jobs first
                    for job in released_jobs:
                        CPU_to_reschedule = migration_restriction[job]
                        if CPU_to_reschedule is not None:
                            current_job = jobs_to_schedule[CPU_to_reschedule]
                            if current_job is None or \
                                    self.priority_function(job, CPUs[0].time) + 1e-10 < \
                                    self.priority_function(current_job, CPUs[0].time):
                                # strict inequality here favors continuing execution of previous job and the 1e-10
                                # allows for minor handling of floating point errors from the variable execution rate
                                jobs_to_schedule[CPU_to_reschedule] = job

                # Handle all jobs whose migration is not (yet) restricted
                for job in released_jobs:
                    if job in jobs_to_schedule.values():
                        continue

                    if _DEBUG:
                        if not self.restrict_migration:
                            assert migration_restriction[job] is None

                    if migration_restriction[job] is None:
                        if self.has_idle_processors(CPUs, jobs_to_schedule):
                            # CPU was idle, so choose this job
                            jobs_to_schedule[self.get_idle_processor(CPUs, jobs_to_schedule)] = job
                        elif self.priority_function(job, CPUs[0].time) + 1e-10 < \
                                max(self.priority_function(job_to_schedule, CPUs[0].time)
                                    for job_to_schedule in jobs_to_schedule.values()):
                            # strict inequality here favors continuing execution of previous job and the 1e-10
                            # allows for minor handling of floating point errors from the variable execution rate
                            CPU_to_reschedule = max(jobs_to_schedule.items(),
                                                    key=lambda CPU_job:
                                                    self.priority_function(CPU_job[1], CPUs[0].time))[0]
                            jobs_to_schedule[CPU_to_reschedule] = job

                        if _DEBUG:
                            assert len(jobs_to_schedule) == self.num_processors

                last_time = CPUs[0].time

                for CPU, job in jobs_to_schedule.items():
                    if job is not None:
                        CPU.schedule_job(job)

                for CPU in CPUs:
                    CPU.idle_until(last_time + 1)

                for CPU in CPUs:
                    job_to_schedule = CPU.last_job_scheduled()

                    if self.restrict_migration and job_to_schedule is not None:
                        # set migration restriction since job has been scheduled
                        migration_restriction[job_to_schedule] = CPU

                        if _DEBUG:
                            if migration_restriction[job_to_schedule] is not None:
                                assert CPU == migration_restriction[job_to_schedule]

                    if job_to_schedule is not None and job_to_schedule.has_completed():
                        released_jobs.remove(job_to_schedule)

                if _DEBUG:
                    assert all(CPU.time == CPUs[0].time for CPU in CPUs)

                if any(CPU.last_job_scheduled() is not None and not CPU.last_job_scheduled().has_completed() and \
                       CPU.time > CPU.last_job_scheduled().deadline
                       for CPU in CPUs):
                    return [CPU.schedule for CPU in CPUs], False  # not schedulable
            elif len(remaining_jobs) > 0:
                for CPU in CPUs:
                    # idle until next job release
                    CPU.idle_until(remaining_jobs[-1].release)

            while len(remaining_jobs) > 0 and remaining_jobs[-1].release <= CPUs[0].time:
                released_jobs.append(remaining_jobs.pop())

        if all(job.deadline > final_time for job in remaining_jobs) and \
                all(job.deadline > final_time for job in released_jobs):
            return [CPU.schedule for CPU in CPUs], True
        else:
            return [CPU.schedule for CPU in CPUs], False
