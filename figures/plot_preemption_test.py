import matplotlib.pyplot as plt

edf_data = []
redf_data = []
np_edf_data = []

with open("preemption_test", "r") as file:
    for line in file.readlines():
        priority_name, _, _, preemption_cost, breakdown_density = line.split()
        preemption_cost = int(preemption_cost)
        breakdown_density = float(breakdown_density)
        if priority_name == "G-EDF":
            edf_data.append((preemption_cost, breakdown_density))
        elif priority_name == "GR-EDF":
            redf_data.append((preemption_cost, breakdown_density))
        else:
            np_edf_data.append((preemption_cost, breakdown_density))

edf_data.sort(key=lambda x: x[0])
redf_data.sort(key=lambda x: x[0])
np_edf_data.sort(key=lambda x: x[0])

xs, ys = zip(*edf_data)
plt.plot(xs, ys, linestyle="dashed", label="G-EDF")
plt.scatter(xs, ys, marker='+')
xs, ys = zip(*redf_data)
plt.plot(xs, ys, linestyle="dashed", label="GR-EDF")
plt.scatter(xs, ys, marker='+')
xs, ys = zip(*np_edf_data)
plt.plot(xs, ys, linestyle="dashed", label="G-NP-EDF")
plt.scatter(xs, ys, marker='+')

plt.ylabel("breakdown utilization")
plt.xlabel(f"cache warmup time ($\mu$s)")
plt.legend()
# plt.show()
plt.savefig("multiprocessor_preemption.pdf")
