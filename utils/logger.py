# utils/logger.py
# Minimal dependency-free logger for both legacy and PD metrics.

import os, csv
from pathlib import Path
from datetime import datetime

# ---------- Legacy logger (for timestamp, stage, runtime_min) ----------
def log_result(stage: str, runtime: float):
    """
    Append timestamp, stage, and runtime to data/results_log_old.csv
    """
    path = Path(__file__).resolve().parents[1] / "data" / "results_log_old.csv"
    path.parent.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
<<<<<<< HEAD
    df = pd.DataFrame([[timestamp, stage, runtime]], 
                      columns=["timestamp", "stage", "runtime_min"])
    path = "data/results_log.csv"
    exists = os.path.exists(path)
    df.to_csv(path, mode='a', header=not exists, index=False)
    console.log(f"[bold green]✔ Logged result:[/bold green] {stage} ({runtime} min)")
=======
    write_header = not path.exists() or path.stat().st_size == 0

    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["timestamp", "stage", "runtime_min"])
        w.writerow([timestamp, stage, runtime])

    print(f"[INFO] Logged legacy runtime → {path}")

# ---------- New PD metrics logger ----------
FIELDS = ["design", "run", "runtime_min", "WNS", "TNS", "DRC", "cell_area", "die_area"]

def log_run(qor_data: dict):
    """
    Append parsed PD metrics to data/results_log.csv
    """
    out_csv = Path(__file__).resolve().parents[1] / "data" / "results_log.csv"
    out_csv.parent.mkdir(exist_ok=True)

    write_header = not out_csv.exists() or out_csv.stat().st_size == 0
    with open(out_csv, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        w.writerow({k: qor_data.get(k, "") for k in FIELDS})

    print(f"[INFO] Logged PD metrics → {out_csv}")
>>>>>>> 5579002 (Added qor_parser.py; improved design)
