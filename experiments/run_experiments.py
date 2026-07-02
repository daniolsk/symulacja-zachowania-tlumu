"""
Batchowe uruchamianie modelu StadiumModel (headless) w celu zebrania danych
do sekcji "Wyniki badań eksperymentalnych".

Uruchamia model wielokrotnie (replikacje) dla różnych zestawów parametrów,
zapisuje surowe wyniki do plików CSV oraz generuje wykresy PNG (matplotlib).

Uruchom:  ../venv/bin/python run_experiments.py
"""
import os
import sys
import csv
import time
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# import modelu z katalogu nadrzednego
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from model import StadiumModel
from agent import FanAgent

PLOTS = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS, exist_ok=True)

WIDTH = HEIGHT = 50
MAX_STEPS = 1800
REPS = 3

# domyslne (bazowe) wartosci parametrow
BASE = dict(num_fans=200, gate_service_time=5, gate_width=2, num_gates=4, smart_entry=1)


def run_once(**params):
    """Pojedynczy bieg. Zwraca slownik metryk zagregowanych."""
    p = dict(BASE)
    p.update(params)
    m = StadiumModel(WIDTH, HEIGHT, **p)
    fans = [a for a in m.schedule.agents if isinstance(a, FanAgent)]
    n = len(fans)
    fill_time = None
    queue_series = []
    throughput_series = []
    for i in range(MAX_STEPS):
        m.step()
        df_last = m.datacollector.model_vars
        queue_series.append(df_last["Długość kolejki"][-1])
        throughput_series.append(df_last["Przepustowość"][-1])
        if sum(1 for a in fans if a.is_seated) == n:
            fill_time = i + 1
            break
    seated = sum(1 for a in fans if a.is_seated)
    mean_entry = df_last["Średni czas wejścia"][-1]
    active_thr = [t for t in throughput_series if t > 0]
    return dict(
        fans=n,
        fill_time=fill_time if fill_time is not None else MAX_STEPS,
        completed=(fill_time is not None),
        seated=seated,
        mean_entry=mean_entry,
        # srednia liczba kibicow oczekujacych na odprawe w trakcie calego biegu
        # (miara poziomu zatloczenia / natezenia waskiego gardla)
        mean_queue=(statistics.mean(queue_series) if queue_series else 0),
        mean_throughput=(statistics.mean(active_thr) if active_thr else 0),
    )


def run_config(reps=REPS, **params):
    """Wiele replikacji jednej konfiguracji -> srednie + odchylenia."""
    rows = [run_once(**params) for _ in range(reps)]
    agg = {}
    for key in ("fill_time", "mean_entry", "mean_queue", "mean_throughput"):
        vals = [r[key] for r in rows]
        agg[key] = statistics.mean(vals)
        agg[key + "_sd"] = statistics.pstdev(vals) if len(vals) > 1 else 0.0
    agg["completed_all"] = all(r["completed"] for r in rows)
    return agg


def save_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Eksperyment 1: wplyw liczby bramek
# ---------------------------------------------------------------------------
def exp_gates():
    log("EXP1: liczba bramek")
    xs = [1, 2, 3, 4, 6, 8]
    rows = []
    for g in xs:
        a = run_config(num_gates=g)
        rows.append([g, a["fill_time"], a["fill_time_sd"], a["mean_entry"],
                     a["mean_queue"], a["mean_throughput"]])
        log(f"  gates={g} fill={a['fill_time']:.1f} entry={a['mean_entry']:.1f} maxQ={a['mean_queue']:.1f}")
    save_csv(os.path.join(PLOTS, "..", "exp1_gates.csv"),
             ["num_gates", "fill_time", "fill_time_sd", "mean_entry", "mean_queue", "mean_throughput"], rows)

    g = [r[0] for r in rows]
    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax1.errorbar(g, [r[1] for r in rows], yerr=[r[2] for r in rows], marker="o", color="tab:blue", capsize=3, label="Czas zapełnienia")
    ax1.set_xlabel("Liczba bramek")
    ax1.set_ylabel("Czas zapełnienia [kroki]", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax2 = ax1.twinx()
    ax2.plot(g, [r[4] for r in rows], marker="s", color="tab:red", label="Śr. kolejka")
    ax2.set_ylabel("Średnia długość kolejki", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")
    plt.title("Wpływ liczby bramek na czas zapełnienia i kolejkę")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "exp1_gates.png"), dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Eksperyment 2: wplyw czasu kontroli biletow
# ---------------------------------------------------------------------------
def exp_service():
    log("EXP2: czas kontroli biletow")
    # lzejsze obciazenie (120 kibicow) aby biegi przy dlugiej odprawie zdazyly sie zakonczyc
    xs = [1, 3, 5, 8, 12]
    rows = []
    for s in xs:
        a = run_config(gate_service_time=s, num_fans=120)
        rows.append([s, a["fill_time"], a["fill_time_sd"], a["mean_entry"], a["mean_queue"]])
        log(f"  service={s} fill={a['fill_time']:.1f} entry={a['mean_entry']:.1f} maxQ={a['mean_queue']:.1f}")
    save_csv(os.path.join(PLOTS, "..", "exp2_service.csv"),
             ["service_time", "fill_time", "fill_time_sd", "mean_entry", "mean_queue"], rows)

    x = [r[0] for r in rows]
    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax1.errorbar(x, [r[1] for r in rows], yerr=[r[2] for r in rows], marker="o", color="tab:blue", capsize=3)
    ax1.set_xlabel("Czas kontroli biletu [kroki/kibic]")
    ax1.set_ylabel("Czas zapełnienia [kroki]", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax2 = ax1.twinx()
    ax2.plot(x, [r[4] for r in rows], marker="s", color="tab:red")
    ax2.set_ylabel("Średnia długość kolejki", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")
    plt.title("Wpływ czasu kontroli biletów")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "exp2_service.png"), dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Eksperyment 3: wplyw szerokosci bramek
# ---------------------------------------------------------------------------
def exp_width():
    log("EXP3: szerokosc bramek")
    xs = [1, 2, 3, 4, 5]
    rows = []
    for w in xs:
        a = run_config(gate_width=w)
        rows.append([w, a["fill_time"], a["fill_time_sd"], a["mean_entry"],
                     a["mean_queue"], a["mean_throughput"]])
        log(f"  width={w} fill={a['fill_time']:.1f} entry={a['mean_entry']:.1f} thr={a['mean_throughput']:.2f}")
    save_csv(os.path.join(PLOTS, "..", "exp3_width.csv"),
             ["gate_width", "fill_time", "fill_time_sd", "mean_entry", "mean_queue", "mean_throughput"], rows)

    x = [r[0] for r in rows]
    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax1.errorbar(x, [r[1] for r in rows], yerr=[r[2] for r in rows], marker="o", color="tab:blue", capsize=3)
    ax1.set_xlabel("Szerokość bramki [komórki]")
    ax1.set_ylabel("Czas zapełnienia [kroki]", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax2 = ax1.twinx()
    ax2.plot(x, [r[5] for r in rows], marker="s", color="tab:green")
    ax2.set_ylabel("Średnia przepustowość [kibic/krok]", color="tab:green")
    ax2.tick_params(axis="y", labelcolor="tab:green")
    plt.title("Wpływ szerokości bramek")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "exp3_width.png"), dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Eksperyment 4: swiadome vs losowe wejscie, w funkcji obciazenia
# ---------------------------------------------------------------------------
def exp_smart():
    log("EXP4: swiadome vs losowe wejscie")
    loads = [100, 150, 200, 250, 300]
    rows = []
    for nf in loads:
        a1 = run_config(num_fans=nf, smart_entry=1)
        a0 = run_config(num_fans=nf, smart_entry=0)
        rows.append([nf, a1["mean_entry"], a1["fill_time"], a0["mean_entry"], a0["fill_time"]])
        log(f"  fans={nf} smart_entry={a1['mean_entry']:.1f}/{a1['fill_time']:.0f} "
            f"random_entry={a0['mean_entry']:.1f}/{a0['fill_time']:.0f}")
    save_csv(os.path.join(PLOTS, "..", "exp4_smart.csv"),
             ["num_fans", "smart_mean_entry", "smart_fill", "random_mean_entry", "random_fill"], rows)

    x = [r[0] for r in rows]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, [r[1] for r in rows], marker="o", color="tab:green", label="Świadome wejście")
    ax.plot(x, [r[3] for r in rows], marker="s", color="tab:orange", label="Losowe wejście")
    ax.set_xlabel("Liczba kibiców")
    ax.set_ylabel("Średni czas wejścia [kroki]")
    ax.legend()
    plt.title("Świadomy wybór bramki vs wejście losowe")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "exp4_smart.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    t0 = time.time()
    exp_gates()
    exp_width()
    exp_smart()
    exp_service()
    log(f"GOTOWE w {time.time()-t0:.0f}s")
