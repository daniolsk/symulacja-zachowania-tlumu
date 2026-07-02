# Eksperymenty

Skrypty do wsadowego (headless) uruchamiania modelu `StadiumModel` i zbierania
danych do sekcji „Wyniki badań eksperymentalnych" sprawozdania.

## Uruchomienie

```bash
../venv/bin/python run_experiments.py   # 4 główne sweepy -> exp*.csv + plots/exp*.png
../venv/bin/python robust_gates.py       # odporny (8 replikacji) sweep liczby bramek -> exp1_gates_robust.csv
../venv/bin/python replot.py             # regeneracja wykresów exp1/2/3 z plików CSV
```

## Zawartość

- `run_experiments.py` — definicje czterech eksperymentów (liczba bramek, czas
  kontroli biletów, szerokość bramek, świadomy vs losowy wybór bramki).
- `robust_gates.py` — powtórzony sweep liczby bramek z 8 replikacjami i raportem
  odsetka ukończonych biegów (mediana czasu zapełnienia).
- `replot.py` — przerysowanie wykresów tak, by prezentowały czas zapełnienia i
  średni czas wejścia.
- `exp*.csv` — surowe wyniki liczbowe.
- `plots/exp*.png` — wykresy do sprawozdania.
- `plots/rys_*.png` — zrzuty ekranu z warstwy wizualizacji (`python run.py`).

Konfiguracja bazowa: 200 kibiców, 4 bramki, szerokość 2, czas kontroli 5,
świadome wejście. W każdym eksperymencie zmieniany jest jeden parametr.
