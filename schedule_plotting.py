import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

_COLORMAP = plt.get_cmap("Set1")
_COLORS = [_COLORMAP(i) for i in range(8)]
_OVERHEAD_COLOR = _COLORMAP(9)


def plot_external_legend(schedules, entity="Task", filename="legend.pdf", expand=None, fontsize=14):
    """
    Export a legend for a multiprocessor schedule plot.

    :param schedules: list of schedules to plot
    :param entity: 'Task' or 'Processor'
    :param filename: filename to save plot to
    :param expand: amount by which to expand plot borders. Defaults to [-5, -5, 5, 5]
    :param fontsize: font size in plot
    """
    if expand is None:
        expand = [-5, -5, 5, 5]

    fig = plt.figure()

    if entity == "Processor":
        num_entities = len(schedules) - 1
    elif entity == "Task":
        num_entities = max(scheduled_job.job.task.id for schedule in schedules for scheduled_job in schedule)
    else:
        raise ValueError(f"Entity {entity} not implemented for legend!")

    for task_id in range(num_entities + 1):
        rect = patches.Rectangle((0, 0), 0, 0,
                                 linewidth=2, edgecolor='black',
                                 facecolor=_COLORS[task_id % len(_COLORS)],
                                 label=f"{entity} {task_id}")
        fig.gca().add_patch(rect)

    legend = fig.legend(loc="center", framealpha=1, frameon=True, fontsize=fontsize)
    legend_fig = legend.figure
    legend_fig.canvas.draw()
    bbox = legend.get_window_extent()
    bbox = bbox.from_extents(*(bbox.extents + np.array(expand)))
    bbox = bbox.transformed(legend_fig.dpi_scale_trans.inverted())
    legend_fig.savefig(filename, dpi="figure", bbox_inches=bbox)
    plt.close(legend_fig)


def plot_uniprocessor_schedule(schedule, job_height=0.75,
                               arrowhead_width=None, arrowhead_height=0.2,
                               arrow_width=0.25, arrow_height=0.85,
                               T_height=0.85, T_width=None, T_linewidth=4,
                               fontsize=14):
    """
    Plot a uniprocessor schedule with one row in the plot per task.

    :param schedule: schedule to plot
    :param job_height: height of each job in the plot
    :param arrowhead_width: width of release/deadline arrowheads. Defaults to 0.75 * (last_deadline / 25)
    :param arrowhead_height: height of release/deadline arrowheads
    :param arrow_width: width of release/deadline arrows
    :param arrow_height: height of release/deadline arrows
    :param T_height: height of job completion markers
    :param T_width: width of job completion markers. Defaults to 0.5 * (last_deadline / 25)
    :param T_linewidth: linewidth of job completion markers and horizontal row lines
    :param fontsize: font size in plot
    """

    all_jobs = {scheduled_job.job for scheduled_job in schedule}

    if len(all_jobs) == 0:
        return

    if any(job.task.id is None for job in all_jobs):
        raise ValueError("All tasks must have integer IDs for plotting!")

    largest_task_id = max(job.task.id for job in all_jobs)
    vertical_offset = {job: job.task.id - job_height / 2 for job in all_jobs}
    last_deadline = max(job.deadline for job in all_jobs)

    # Try to force matplotlib to choose reasonable window limits
    plt.plot([0, last_deadline],
             [min(vertical_offset.values()), max(vertical_offset.values()) + arrow_height], linewidth=0,
             color="white")

    if T_width is None:
        T_width = 0.5 * (last_deadline / 25)

    if arrowhead_width is None:
        arrowhead_width = 0.75 * (last_deadline / 25)

    # Plot horizontal row lines
    for job in all_jobs:
        plt.hlines(vertical_offset[job], 0, last_deadline, linewidth=T_linewidth)

    # Plot job releases
    for job in all_jobs:
        plt.arrow(job.release, vertical_offset[job], 0, arrow_height,
                  head_width=arrowhead_width, head_length=arrowhead_height,
                  length_includes_head=True, width=arrow_width, linewidth=2,
                  facecolor="blue")

    # Plot job deadlines
    for job in all_jobs:
        plt.arrow(job.deadline, vertical_offset[job] + arrow_height, 0, -arrow_height,
                  head_width=arrowhead_width, head_length=arrowhead_height,
                  length_includes_head=True, width=arrow_width, linewidth=2,
                  facecolor="red")

    # Plot scheduled jobs
    for scheduled_job in schedule:
        start = scheduled_job.start_time
        end = scheduled_job.end_time
        job = scheduled_job.job
        task_id = job.task.id

        rect = patches.Rectangle((start, vertical_offset[job]), end - start, job_height,
                                 linewidth=2, edgecolor='black',
                                 facecolor=_COLORS[task_id % len(_COLORS)])
        plt.gca().add_patch(rect)

    # Plot job completions
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

    # Extend x tick marks upward
    old_xlim = plt.xlim()
    old_ylim = plt.ylim()
    xticks = [x for x in plt.xticks()[0] if x >= 0 and x <= last_deadline]
    plt.vlines(xticks, old_ylim[0], old_ylim[1], linewidth=2, linestyles="dashed", alpha=0.5)
    plt.xlim(*old_xlim)
    plt.ylim(*old_ylim)


def plot_multiprocessor_schedule_per_processor(schedules, job_height=0.75,
                                               T_linewidth=4,
                                               fontsize=14):
    """
    Plot a multiprocessor schedule with one row in the plot per processor.

    :param schedules: list of schedules to plot
    :param job_height: height of each job in the plot
    :param T_linewidth: linewidth of horizontal row lines
    :param fontsize: font size in plot
    """
    all_jobs = {scheduled_job.job for schedule in schedules for scheduled_job in schedule}

    if len(all_jobs) == 0:
        return

    last_deadline = max(job.deadline for job in all_jobs)
    vertical_offsets = {processor_idx: processor_idx - job_height / 2 for processor_idx in range(len(schedules))}

    # Try to force matplotlib to choose reasonable window limits
    plt.plot([0, last_deadline], [min(vertical_offsets.values()), max(vertical_offsets.values()) + job_height],
             linewidth=0, color="white")

    for processor_idx, schedule in enumerate(schedules):
        vertical_offset = vertical_offsets[processor_idx]

        # Plot horizontal row lines
        plt.hlines(vertical_offset, 0, last_deadline, linewidth=T_linewidth)

        # Plot scheduled jobs
        for scheduled_job in schedule:
            start = scheduled_job.start_time
            end = scheduled_job.end_time
            job = scheduled_job.job
            task_id = job.task.id

            rect = patches.Rectangle((start, vertical_offset), end - start, job_height,
                                     linewidth=2, edgecolor='black',
                                     facecolor=_COLORS[task_id % len(_COLORS)])
            plt.gca().add_patch(rect)

    plt.xlabel("time", fontsize=fontsize)
    plt.ylabel("processor id", fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.yticks(range(0, len(schedules)), fontsize=fontsize)

    # Extend x tick marks upward
    old_xlim = plt.xlim()
    old_ylim = plt.ylim()
    xticks = [x for x in plt.xticks()[0] if 0 <= x <= last_deadline]
    plt.vlines(xticks, old_ylim[0], old_ylim[1], linewidth=2, linestyles="dashed", alpha=0.5)
    plt.xlim(*old_xlim)
    plt.ylim(*old_ylim)


def plot_multiprocessor_schedule_per_task(schedules, job_height=0.75,
                                          arrowhead_width=None, arrowhead_height=0.2,
                                          arrow_width=0.25, arrow_height=0.85,
                                          T_height=0.85, T_width=None, T_linewidth=4,
                                          fontsize=14):
    """
    Plot a multiprocessor schedule with one row in the plot per task.

    :param schedule: list of schedules to plot
    :param job_height: height of each job in the plot
    :param arrowhead_width: width of release/deadline arrowheads. Defaults to 0.75 * (last_deadline / 25)
    :param arrowhead_height: height of release/deadline arrowheads
    :param arrow_width: width of release/deadline arrows
    :param arrow_height: height of release/deadline arrows
    :param T_height: height of job completion markers
    :param T_width: width of job completion markers. Defaults to 0.5 * (last_deadline / 25)
    :param T_linewidth: linewidth of job completion markers and horizontal row lines
    :param fontsize: font size in plot
    """

    combined_schedule = {scheduled_job for schedule in schedules for scheduled_job in schedule}
    all_jobs = {scheduled_job.job for scheduled_job in combined_schedule}
    processor_idx_per_scheduled_job = {scheduled_job: processor_idx for processor_idx in range(len(schedules))
                                       for scheduled_job in schedules[processor_idx]}

    if len(all_jobs) == 0:
        return

    if any(job.task.id is None for job in all_jobs):
        raise ValueError("All tasks must have integer IDs for plotting!")

    largest_task_id = max(job.task.id for job in all_jobs)
    vertical_offset = {job: job.task.id - job_height / 2 for job in all_jobs}
    last_deadline = max(job.deadline for job in all_jobs)

    # Try to force matplotlib to choose reasonable window limits
    plt.plot([0, last_deadline],
             [min(vertical_offset.values()), max(vertical_offset.values()) + arrow_height], linewidth=0,
             color="white")

    if T_width is None:
        T_width = 0.5 * (last_deadline / 25)

    if arrowhead_width is None:
        arrowhead_width = 0.75 * (last_deadline / 25)

    # Plot horizontal row lines
    for job in all_jobs:
        plt.hlines(vertical_offset[job], 0, last_deadline, linewidth=T_linewidth)

    # Plot job releases
    for job in all_jobs:
        plt.arrow(job.release, vertical_offset[job], 0, arrow_height,
                  head_width=arrowhead_width, head_length=arrowhead_height,
                  length_includes_head=True, width=arrow_width, linewidth=2,
                  facecolor="blue")

    # Plot job deadlines
    for job in all_jobs:
        plt.arrow(job.deadline, vertical_offset[job] + arrow_height, 0, -arrow_height,
                  head_width=arrowhead_width, head_length=arrowhead_height,
                  length_includes_head=True, width=arrow_width, linewidth=2,
                  facecolor="red")

    # Plot scheduled jobs
    for scheduled_job in combined_schedule:
        start = scheduled_job.start_time
        end = scheduled_job.end_time
        job = scheduled_job.job
        processor_idx = processor_idx_per_scheduled_job[scheduled_job]

        rect = patches.Rectangle((start, vertical_offset[job]), end - start, job_height,
                                 linewidth=2, edgecolor='black',
                                 facecolor=_COLORS[processor_idx % len(_COLORS)])
        plt.gca().add_patch(rect)

    # Plot job completions
    for scheduled_job in combined_schedule:
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

    # Extend x tick marks upward
    old_xlim = plt.xlim()
    old_ylim = plt.ylim()
    xticks = [x for x in plt.xticks()[0] if x >= 0 and x <= last_deadline]
    plt.vlines(xticks, old_ylim[0], old_ylim[1], linewidth=2, linestyles="dashed", alpha=0.5)
    plt.xlim(*old_xlim)
    plt.ylim(*old_ylim)
