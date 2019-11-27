import warnings

_DEBUG = True


class Processor:
    # TODO: add schedule_cost=0, dispatch_cost=0, preemption_cost=0
    # TODO: add cache_warmup_time=0 and cold_cache_rate=1
    def __init__(self):
        self.schedule = Schedule()
        self.time = 0

    def last_job_scheduled(self):
        if len(self.schedule) > 0:
            last_scheduled_job = self.schedule[-1]
            if last_scheduled_job.end_time == self.time:
                return last_scheduled_job.job
        return None  # idle

    def schedule_job(self, job):
        self.schedule.add(job, self.time, self.time + 1)
        self.time += 1

        job.remaining_cost -= 1
        if job.remaining_cost <= 0:
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
    def __init__(self, priority_function):
        self.priority_function = priority_function

    def generate_schedule(self, task_system, final_time=None):
        if final_time is None:
            if all(task.phase == 0 for task in task_system.tasks):
                final_time = task_system.hyperperiod
            else:
                # Result by Leung and Merrill: If a deadline is missed in a periodic task system with
                # utilization <= 1, then it will be missed by time 2*P + max(D_i) + max(s_i)
                final_time = 2 * task_system.hyperperiod + max(task.relative_deadline for task in task_system.tasks) + \
                             max(task.phase for task in task_system.tasks)

        CPU = Processor()
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
                    elif self.priority_function(job, CPU.time) < self.priority_function(job_to_schedule, CPU.time):
                        # strict inequality here favors continuing execution of previous job
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

        return CPU.schedule, len(remaining_jobs) + len(released_jobs) == 0
