"""
Przerysowanie wykresow exp1 (bramki) i exp2 (czas kontroli) tak, aby na obu
osiach znajdowaly sie latwo interpretowalne metryki: czas zapelnienia trybun
oraz sredni czas wejscia. Dane bramek pochodza z odpornego biegu (8 replikacji,
mediana) zapisanego w exp1_gates_robust.csv.
"""
import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
PLOTS = os.path.join(HERE, "plots")


def read_csv(name):
    with open(os.path.join(HERE, name)) as f:
        return list(csv.DictReader(f))


# ---- EXP1: bramki (dane odporne) ----
g = read_csv("exp1_gates_robust.csv")
x = [int(r["num_gates"]) for r in g]
fill = [float(r["median_fill"]) for r in g]
entry = [float(r["mean_entry"]) for r in g]

fig, ax1 = plt.subplots(figsize=(6, 4))
ax1.plot(x, fill, marker="o", color="tab:blue")
ax1.set_xlabel("Liczba bramek")
ax1.set_ylabel("Czas zapełnienia (mediana) [kroki]", color="tab:blue")
ax1.tick_params(axis="y", labelcolor="tab:blue")
ax2 = ax1.twinx()
ax2.plot(x, entry, marker="s", color="tab:red")
ax2.set_ylabel("Średni czas wejścia [kroki]", color="tab:red")
ax2.tick_params(axis="y", labelcolor="tab:red")
plt.title("Wpływ liczby bramek")
fig.tight_layout()
fig.savefig(os.path.join(PLOTS, "exp1_gates.png"), dpi=130)
plt.close(fig)

# ---- EXP2: czas kontroli ----
s = read_csv("exp2_service.csv")
x = [int(r["service_time"]) for r in s]
fill = [float(r["fill_time"]) for r in s]
entry = [float(r["mean_entry"]) for r in s]

fig, ax1 = plt.subplots(figsize=(6, 4))
ax1.plot(x, fill, marker="o", color="tab:blue")
ax1.set_xlabel("Czas kontroli biletu [kroki/kibic]")
ax1.set_ylabel("Czas zapełnienia [kroki]", color="tab:blue")
ax1.tick_params(axis="y", labelcolor="tab:blue")
ax2 = ax1.twinx()
ax2.plot(x, entry, marker="s", color="tab:red")
ax2.set_ylabel("Średni czas wejścia [kroki]", color="tab:red")
ax2.tick_params(axis="y", labelcolor="tab:red")
plt.title("Wpływ czasu kontroli biletów (120 kibiców)")
fig.tight_layout()
fig.savefig(os.path.join(PLOTS, "exp2_service.png"), dpi=130)
plt.close(fig)

# ---- EXP3: szerokosc bramek ----
w = read_csv("exp3_width.csv")
x = [int(r["gate_width"]) for r in w]
fill = [float(r["fill_time"]) for r in w]
entry = [float(r["mean_entry"]) for r in w]

fig, ax1 = plt.subplots(figsize=(6, 4))
ax1.plot(x, fill, marker="o", color="tab:blue")
ax1.set_xlabel("Szerokość bramki [komórki]")
ax1.set_ylabel("Czas zapełnienia [kroki]", color="tab:blue")
ax1.tick_params(axis="y", labelcolor="tab:blue")
ax2 = ax1.twinx()
ax2.plot(x, entry, marker="s", color="tab:red")
ax2.set_ylabel("Średni czas wejścia [kroki]", color="tab:red")
ax2.tick_params(axis="y", labelcolor="tab:red")
plt.title("Wpływ szerokości bramek")
fig.tight_layout()
fig.savefig(os.path.join(PLOTS, "exp3_width.png"), dpi=130)
plt.close(fig)

print("replot done")
