from math import inf

_DEBUG = True


class Processor:
    def __init__(self, schedule_cost=0, dispatch_cost=0, preemption_cost=0,
                 cache_warmup_time=None, cold_cache_rate=1):
        self.schedule = Schedule()
        self.time = 0

        self.schedule_cost = schedule_cost
        self.dispatch_cost = dispatch_cost
        self.preemption_cost = preemption_cost

        self.cache_warmup_time = cache_warmup_time
        self.cold_cache_rate = cold_cache_rate
        self.execution_rate = cold_cache_rate

    def last_job_scheduled(self):
        if len(self.schedule) > 0:
            last_scheduled_job = self.schedule[-1]
            if last_scheduled_job.end_time == self.time:
                return last_scheduled_job.job
        return None  # idle

    def schedule_job(self, job):
        if job != self.last_job_scheduled():
            self.execution_rate = self.cold_cache_rate  # reset cache

            if not job.has_started():
                job.remaining_overhead += self.schedule_cost + self.dispatch_cost
            elif self.last_job_scheduled() is None:  # CPU was idle
                job.remaining_overhead += self.dispatch_cost + self.preemption_cost
            else:
                job.remaining_overhead += self.dispatch_cost + 2 * self.preemption_cost

        self.schedule.add(job, self.time, self.time + 1)
        self.time += 1

        gain_cache_affinity = not job.has_remaining_overhead()
        job.decrement_remaining_cost(self.execution_rate)

        if gain_cache_affinity and self.cache_warmup_time is not None:
            # TODO: floating point errors could cause issues here for some priority functions
            self.execution_rate += ((1 - self.cold_cache_rate) / self.cache_warmup_time)
            if self.execution_rate >= 1:
                self.execution_rate = 1

        if job.has_completed():
            self.schedule[-1].job_completed = True

    def idle_until(self, t):
        if _DEBUG:
            assert t >= self.time
        self.time = t


class Schedule:
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
        if _DEBUG:
            assert end_time == start_time + 1

        if len(self.schedule) > 0 and job == self.schedule[-1].job:
            if _DEBUG:
                assert start_time == self.schedule[-1].end_time

            self.schedule[-1].end_time = end_time
        else:
            self.schedule.append(ScheduledJob(start_time, end_time, job))


class ScheduledJob:
    def __init__(self, start_time, end_time, job):
        self.start_time = start_time
        self.end_time = end_time
        self.job = job
        self.job_completed = False

    def __str__(self):
        return f"{str(self.job)} executing in [{self.start_time}, {self.end_time}]"


class UniprocessorScheduler:
    def __init__(self, priority_function, processor=None):
        self.priority_function = priority_function
        if processor is None:
            self.CPU = Processor()
        else:
            self.CPU = processor

    def generate_schedule(self, task_system, final_time=None):
        if final_time is None:
            if all(task.phase == 0 for task in task_system.tasks) and \
                    all(task.relative_deadline <= task.period for task in task_system.tasks):
                final_time = task_system.hyperperiod
            else:
                # Result by Leung and Merrill: If a deadline is missed in a periodic task system with
                # utilization <= 1, then it will be missed by time 2*P + max(D_i) + max(s_i)
                final_time = 2 * task_system.hyperperiod + max(task.relative_deadline for task in task_system.tasks) + \
                             max(task.phase for task in task_system.tasks)

        CPU = self.CPU
        released_jobs = []
        remaining_jobs = sorted([job for task in task_system.tasks
                                 for job in task.generate_jobs(final_time)], key=lambda job: -job.release)

        if task_system.utilization() > 1:
            return CPU.schedule, False  # not schedulable

        while CPU.time < final_time and len(remaining_jobs) + len(released_jobs) > 0:
            if len(released_jobs) != 0:
                job_to_schedule = CPU.last_job_scheduled()
                for job in released_jobs:
                    if job_to_schedule is None or job_to_schedule.has_completed():
                        job_to_schedule = job
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

        if _DEBUG:
            assert all(job.deadline > final_time for job in remaining_jobs) and \
                   all(job.deadline > final_time for job in released_jobs)

        return CPU.schedule, True


class MultiprocessorScheduler:
    def __init__(self, priority_function, processors):
        self.priority_function = priority_function
        self.CPUs = processors
        self.num_processors = len(processors)

    def generate_schedule(self, task_system, final_time=None):
        if final_time is None:
            if all(task.phase == 0 for task in task_system.tasks) and \
                    all(task.relative_deadline <= task.period for task in task_system.tasks):
                final_time = task_system.hyperperiod
            else:
                # Result by Leung and Merrill: If a deadline is missed in a periodic task system with
                # utilization <= 1, then it will be missed by time 2*P + max(D_i) + max(s_i)
                final_time = 2 * task_system.hyperperiod + max(task.relative_deadline for task in task_system.tasks) + \
                             max(task.phase for task in task_system.tasks)

        CPUs = self.CPUs
        released_jobs = []
        remaining_jobs = sorted([job for task in task_system.tasks
                                 for job in task.generate_jobs(final_time)], key=lambda job: -job.release)

        if task_system.utilization() > self.num_processors:
            return [CPU.schedule for CPU in CPUs], False  # not schedulable

        while CPUs[0].time < final_time and len(remaining_jobs) + len(released_jobs) > 0:
            print(f"time step: {CPUs[0].time}")
            for j in released_jobs:
                print(f"{str(j)} has priority {self.priority_function(j, CPUs[0].time)}")
            print("==========================")

            if len(released_jobs) != 0:
                jobs_to_schedule = {CPU.last_job_scheduled() for CPU in CPUs
                                    if CPU.last_job_scheduled() is not None
                                    and not CPU.last_job_scheduled().has_completed()}

                for job in released_jobs:
                    if len(jobs_to_schedule) < self.num_processors:
                        jobs_to_schedule.add(job)
                    elif self.priority_function(job, CPUs[0].time) + 1e-10 < \
                            max(self.priority_function(job_to_schedule, CPUs[0].time)
                                for job_to_schedule in jobs_to_schedule):
                        # strict inequality here favors continuing execution of previous job and addition of 1e-10
                        # allows for minor handling of floating point errors from the variable execution rate
                        jobs_to_schedule.remove(max(jobs_to_schedule,
                                                    key=lambda job: self.priority_function(job, CPUs[0].time)))
                        jobs_to_schedule.add(job)

                        if _DEBUG:
                            assert len(jobs_to_schedule) == self.num_processors

                idle_processors = {CPU for CPU in CPUs}
                last_time = CPUs[0].time

                for CPU in CPUs:
                    # if we're continuing an old execution, do so
                    if CPU.last_job_scheduled() in jobs_to_schedule:
                        idle_processors.remove(CPU)
                        jobs_to_schedule.remove(CPU.last_job_scheduled())
                        CPU.schedule_job(CPU.last_job_scheduled())

                for job_to_schedule in jobs_to_schedule:
                    CPU = idle_processors.pop()
                    CPU.schedule_job(job_to_schedule)

                for CPU in CPUs:
                    CPU.idle_until(last_time + 1)

                for CPU in CPUs:
                    job_to_schedule = CPU.last_job_scheduled()
                    if job_to_schedule is not None and job_to_schedule.has_completed():
                        released_jobs.remove(job_to_schedule)

                if _DEBUG:
                    assert all(CPU.time == CPUs[0].time for CPU in CPUs)

                for CPU in CPUs:
                    print("chose to schedule", str(CPU.last_job_scheduled()))

                if any(CPU.last_job_scheduled() is not None and CPU.time > CPU.last_job_scheduled().deadline
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
