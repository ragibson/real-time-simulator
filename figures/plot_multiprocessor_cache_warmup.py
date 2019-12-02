import matplotlib.pyplot as plt

gedf_data = []
gredf_data = []
gnpedf_data = []

with open("multiprocessor_cache_warmup_output", "r") as file:
    for line in file.readlines():
        priority_name, warmup_time, _, breakdown_density = line.split()
        warmup_time = int(warmup_time) // 1000
        breakdown_density = float(breakdown_density)
        if priority_name == "G-EDF":
            gedf_data.append((warmup_time, breakdown_density))
        elif priority_name == "GR-EDF":
            gredf_data.append((warmup_time, breakdown_density))
        else:
            gnpedf_data.append((warmup_time, breakdown_density))

gedf_data.sort(key=lambda x: x[0])
gredf_data.sort(key=lambda x: x[0])
gnpedf_data.sort(key=lambda x: x[0])

xs, ys = zip(*gedf_data)
ys = [y / 4.8609 for y in ys]
plt.plot(xs, ys, linestyle="dashed", label="G-EDF")
plt.scatter(xs, ys, marker='+')
xs, ys = zip(*gredf_data)
ys = [y / 4.3334 for y in ys]
plt.plot(xs, ys, linestyle="dashed", label="GR-EDF")
plt.scatter(xs, ys, marker='+')
xs, ys = zip(*gnpedf_data)
ys = [y / 3.3274 for y in ys]
plt.plot(xs, ys, linestyle="dashed", label="G-NP-EDF")
plt.scatter(xs, ys, marker='+')

plt.ylabel("multiplicative increase in breakdown density\ncompared with \"No Cache\"")
plt.xlabel(f"cache warmup time (ms)")
plt.legend()
# plt.show()
plt.savefig("multiprocessor_breakdown_density_vs_cache_warmup.pdf")
