# utils/logger.py
import os
import pandas as pd
from datetime import datetime
from rich.console import Console

console = Console()

def log_result(stage, runtime):
    """Append the runtime result to results_log.csv"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([[timestamp, stage, runtime]], 
                      columns=["timestamp", "stage", "runtime_min"])
    path = "data/results_log.csv"
    exists = os.path.exists(path)
    df.to_csv(path, mode='a', header=not exists, index=False)
    console.log(f"[bold green]✔ Logged result:[/bold green] {stage} ({runtime} min)")
