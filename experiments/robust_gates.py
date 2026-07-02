"""Odporny (8 replikacji) bieg sweepu liczby bramek + regeneracja wykresu exp1."""
import os
import csv
import statistics as st
import run_experiments as r

REPS = 8
HERE = os.path.dirname(__file__)
rows = []
print("gates | mean_fill median_fill compl/reps mean_entry", flush=True)
for g in [1, 2, 3, 4, 6, 8]:
    runs = [r.run_once(num_gates=g) for _ in range(REPS)]
    fills = [x["fill_time"] for x in runs]
    entry = st.mean([x["mean_entry"] for x in runs])
    compl = sum(x["completed"] for x in runs)
    rows.append([g, st.mean(fills), st.median(fills), compl, REPS, entry])
    print(f"{g:5d} | {st.mean(fills):8.1f} {st.median(fills):8.1f}   {compl}/{REPS}   {entry:.1f}", flush=True)

with open(os.path.join(HERE, "exp1_gates_robust.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["num_gates", "mean_fill", "median_fill", "completed", "reps", "mean_entry"])
    w.writerows(rows)
print("saved exp1_gates_robust.csv", flush=True)
