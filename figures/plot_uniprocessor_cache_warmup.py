import matplotlib.pyplot as plt

edf_data = []
np_edf_data = []

with open("uniprocessor_cache_warmup_output", "r") as file:
    for line in file.readlines():
        priority_name, warmup_time, breakdown_density = line.split()
        warmup_time = int(warmup_time) // 1000
        breakdown_density = float(breakdown_density)
        if priority_name == "EDF":
            edf_data.append((warmup_time, breakdown_density))
        else:
            np_edf_data.append((warmup_time, breakdown_density))

edf_data.sort(key=lambda x: x[0])
np_edf_data.sort(key=lambda x: x[0])

xs, ys = zip(*edf_data)
ys = [y / 1.294 for y in ys]
plt.plot(xs, ys, linestyle="dashed", label="EDF")
plt.scatter(xs, ys, marker='+')
xs, ys = zip(*np_edf_data)
ys = [y / 0.5074 for y in ys]
plt.plot(xs, ys, linestyle="dashed", label="NP-EDF")
plt.scatter(xs, ys, marker='+')

plt.ylabel("multiplicative increase in breakdown density\ncompared with \"No Cache\"")
plt.xlabel(f"cache warmup time (ms)")
plt.legend()
plt.savefig("uniprocessor_breakdown_density_vs_cache_warmup.pdf")
