import matplotlib.pyplot as plt
import matplotlib.patches as patches

_COLORMAP = plt.get_cmap("Set1")
_COLORS = [_COLORMAP(i) for i in range(8)]
_OVERHEAD_COLOR = _COLORMAP(9)


def plot_uniprocessor_schedule(schedule, job_height=0.75,
                               arrowhead_width=None, arrowhead_height=0.2,
                               arrow_width=0.25, arrow_height=0.85,
                               T_height=0.85, T_width=None, T_linewidth=4,
                               fontsize=14):
    all_jobs = {scheduled_job.job for scheduled_job in schedule}

    if len(all_jobs) == 0:
        return

    if any(job.task.id is None for job in all_jobs):
        raise ValueError("All tasks must have integer IDs for plotting!")

    largest_task_id = max(job.task.id for job in all_jobs)
    vertical_offset = {job: job.task.id - job_height / 2 for job in all_jobs}
    last_deadline = max(job.deadline for job in all_jobs)

    plt.plot([0, last_deadline],
             [min(vertical_offset.values()), max(vertical_offset.values())], linewidth=0,
             color="white")

    if T_width is None:
        T_width = 0.5 * (last_deadline / 25)

    if arrowhead_width is None:
        arrowhead_width = 0.75 * (last_deadline / 25)

    for job in all_jobs:
        plt.hlines(vertical_offset[job], 0, last_deadline, linewidth=T_linewidth)

    for job in all_jobs:
        plt.arrow(job.release, vertical_offset[job], 0, arrow_height,
                  head_width=arrowhead_width, head_length=arrowhead_height,
                  length_includes_head=True, width=arrow_width, linewidth=2,
                  facecolor="blue")

    for job in all_jobs:
        plt.arrow(job.deadline, vertical_offset[job] + arrow_height, 0, -arrow_height,
                  head_width=arrowhead_width, head_length=arrowhead_height,
                  length_includes_head=True, width=arrow_width, linewidth=2,
                  facecolor="red")

    for scheduled_job in schedule:
        start = scheduled_job.start_time
        end = scheduled_job.end_time
        job = scheduled_job.job
        task_id = job.task.id

        rect = patches.Rectangle((start, vertical_offset[job]), end - start, job_height,
                                 linewidth=2, edgecolor='black',
                                 facecolor=_COLORS[task_id % len(_COLORS)])
        plt.gca().add_patch(rect)

    for scheduled_job in schedule:
        if scheduled_job.job_completed:
            end = scheduled_job.end_time
            job = scheduled_job.job
            plt.plot([end, end], [vertical_offset[job], vertical_offset[job] + T_height],
                     linewidth=T_linewidth, color="black")
            plt.plot([end - T_width, end + T_width], [vertical_offset[job] + T_height, vertical_offset[job] + T_height],
                     linewidth=T_linewidth, color="black")

    plt.xlabel("time", fontsize=fontsize)
    plt.ylabel("task id", fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.yticks(range(0, largest_task_id + 1), fontsize=fontsize)
