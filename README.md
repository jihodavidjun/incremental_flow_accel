# Incremental Flow Accelerator — Python / OpenLane

- This repository contains a Python-based orchestration layer designed to **accelerate OpenLane RTL-to-GDSII flows** by detecting and re-running only modified stages.  
- It was developed to explore **incremental physical design automation** concepts such as dependency tracking, stage caching, and runtime optimization.

---

## Overview

The system wraps around OpenLane’s `flow.tcl` using Python’s `subprocess` interface and automatically:
- Tracks design and configuration file changes using SHA256 hashing.
- Detects which stages (e.g., synthesis, floorplan, CTS) are affected.
- Re-invokes the OpenLane flow **only from the modified stage** onward (still reuses cached layout and timing data for unchanged stages).
- Logs runtime data to a CSV file for benchmarking runtime and QoR consistency.

This approach aims to **reduce full-flow turnaround time** during iterative design debugging, while preserving design quality.

---

## Features

- **Incremental Stage Detection:** Automatically determines which stages need to re-run based on file-hash changes.
- **Smart Orchestration:** Integrates with OpenLane Docker containers and reuses prior results.
- **Runtime Benchmarking:** Records all runs with timestamps and stage runtimes.
- **QoR Consistency:** Targets up to 4× speed-up with no timing, area, or DRC degradation.

---

## Folder Structure

```markdown
incremental_flow_accel/
│
├── utils/
│ ├── flow_runner.py # Executes OpenLane flow.tcl stages
│ ├── file_hash.py # Computes and compares SHA256 hashes
│ ├── logger.py # Records runtime logs to CSV
│ └── openlane_manager.py # Manages container interaction and flow logic
│
├── config/
│ └── flow_dependencies.json # Defines per-stage dependencies
│
├── data/
│ ├── flow_state.json # Stores last-known file hashes
│ └── results_log.csv # Cumulative runtime log
│
├── flow_tracker.py # Main entrypoint for the incremental runner
└── README.md
```

---

## Prerequisites

1. **Install Docker Desktop**
   - [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Ensure Docker Engine is running (check with `docker ps`)

2. **Clone and set up OpenLane (on your local terminal)**
   ```bash
   git clone https://github.com/The-OpenROAD-Project/OpenLane.git
   cd OpenLane
   make pull-openlane
   make mount
   ```
   This mounts the OpenLane container with all required tools (Magic, OpenROAD, etc.) and maps your local directories.

3. **Clone this repository**
   ```bash
   git clone https://github.com/jihodavidjun/incremental_flow_accel.git
   cd incremental_flow_accel
   ```
   
4. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   If no requirements.txt yet, install manually:
   `pip install watchdog pandas`

---

## How to Run

1. **Run a full flow (initial baseline)**
   `python flow_tracker.py`
   - Runs OpenLane from start to signoff.
   - Generates `data/flow_state.json` (stores file hashes)
   - Logs runtime data to `data/results_log.csv`.

2. **Modify a design file (trigger incremental)**
   ```bash
   cd ~/OpenLane/designs/spm/src
   echo "// logic change" >> adder.v
   ```

3. **Run incrementally**
   ```bash
   cd ~/incremental_flow_accel
   python flow_tracker.py
   ```
   - Detects which design files have changed (e.g., `adder.v`).
   - Determines which downstream stages (e.g., synthesis → placement → routing) are affected.
   - Reuses existing data (netlists, DEFs, SPEF, etc.) from previous runs for all unchanged stages.
   - Automatically resumes the flow from the earliest modified stage onward.
   - Logs runtime and results to `data/results_log.csv`.
  
---

## Example Validation (SKY130)
| Run Type | Runtime (mins) | WNS (ns) | DRC Count | Area (µm²) |
| :------- | :------: | -------: | -------: | -------: |
| Full Flow | 60.0 | -0.05 | 0 | 123,456 |
| Incremental | 15.5 (~4x faster) | -0.05 | 0 | 123,456 |

---

## Tools Used
- **Python 3.11** – orchestration and logging
- **Docker + OpenLane 2.0** – RTL-to-GDSII automation
- **SkyWater 130 PDK** – validation process
- **VSCode** – development & visualization

--- 

## Motivation
While completing the Physical Design onboarding for the **Silicon Jackets** team, I noticed that each OpenLane or Innovus flow run often took over an hour — even for small design edits.
That long turnaround inspired me to experiment with incremental execution: a way to detect what actually changed and re-run only the affected stages.
This project became my independent attempt to replicate the runtime efficiency of professional ECO flows used in industry tools like Innovus or ICC2, using open-source infrastructure.
