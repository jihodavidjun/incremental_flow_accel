# Incremental Flow Accelerator — Python / OpenLane

- This repository contains a Python-based orchestration layer designed to **accelerate OpenLane RTL-to-GDSII flows** by detecting and re-running only modified stages.
- The project replicates the engineering change order (ECO) principle in open-source P&R flows — reducing redundant computation while maintaining signoff consistency.  
- It was developed to explore **incremental physical design automation** concepts such as dependency tracking, stage caching, and runtime optimization.

---

## Overview

The system wraps around OpenLane’s `flow.tcl` using Python’s `subprocess` interface and automatically:
- Tracks design and configuration file changes using SHA256 hashing.
- Detects which stages (e.g., synthesis, floorplan, CTS) are affected.
- Re-invokes the OpenLane flow starting from the earliest modified stage onward, reusing cached layout and timing data for all prior stages.
- Logs runtime data to a CSV file for benchmarking runtime and QoR consistency.

This approach aims to **reduce full-flow turnaround time** during iterative design debugging, while preserving design quality.

---

## Features

- **Incremental Stage Detection:** Automatically determines which stages need to re-run based on file-hash changes.
- **Smart Orchestration:** Integrates with OpenLane Docker containers and reuses prior results.
- **Runtime Benchmarking:** Records all runs with timestamps and stage runtimes.
- **QoR Consistency:** Targets measurable runtime reduction with no timing, area, or DRC degradation.

---

## Folder Structure

```markdown
incremental_flow_accel/
│
├── utils/
│ ├── flow_runner.py # Executes OpenLane flow.tcl stages
│ ├── file_hash.py # Computes and compares SHA256 hashes
│ ├── logger.py # Records runtime logs to CSV
│ ├── qor_parser.py # Parses OpenLane reports/metrics to extract QoR
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

2. **OpenLane container**
   ```bash
   git clone https://github.com/The-OpenROAD-Project/OpenLane.git ~/OpenLane
   cd ~/OpenLane
   ```
   
   - Mac (Apple Silicon / M1 / M2)
   ```bash
   docker pull efabless/openlane:2024.09.05r1-amd64
   docker rm -f openlane 2>/dev/null || true
   docker run -dit \
     --platform linux/amd64 \
     --name openlane \
     -v "$HOME/OpenLane:/openlane" \
     -v "$HOME/OpenLane/pdks:/pdks" \
     -v "$HOME/OpenLane/workspace:/workspace" \
     -w /workspace \
     efabless/openlane:2024.09.05r1-amd64
   ```
   - Mac (Intel) or Linux (x86-64)
   ```bash
   docker pull efabless/openlane:2024.09.05r1
   docker rm -f openlane 2>/dev/null || true
   docker run -dit \
     --name openlane \
     -v "$HOME/OpenLane:/openlane" \
     -v "$HOME/OpenLane/pdks:/pdks" \
     -v "$HOME/OpenLane/workspace:/workspace" \
     -w /workspace \
     efabless/openlane:2024.09.05r1
   ```
   - Windows 10/11 (WSL 2 required)
   1. Install Docker Desktop for Windows (https://www.docker.com/products/docker-desktop/). 
   2. Enable WSL 2 backend and install Ubuntu 22.04 from Microsoft Store.
   3. Run commands inside the Ubuntu terminal (same as the Linux section above).
   
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

1. **Baseline full flow (creates the first run & caches)**
   Either run OpenLane yourself:
   `docker exec openlane flow.tcl -design spm`
   Or run via the project script (this still does a full first run, then logs QoR):
   ```bash
   cd ~/incremental_flow_accel
   python3 -m utils.flow_runner --design spm --container openlane
   ```
   This will:
   - Emit a run folder under ~/OpenLane/designs/spm/runs/RUN_*
   - Parse QoR and append to data/results_log.csv
   - Save file hashes to data/flow_state.json
   
2. **Make a change that should trigger incremental**
   Edit something under ~/OpenLane/designs/spm/ (e.g., RTL or config):
   `echo "// small logic tweak" >> ~/OpenLane/designs/spm/src/spm.v`

3. **Incremental re-run (stage-aware)**
   ```bash
   cd ~/incremental_flow_accel
   python3 -m utils.flow_runner --design spm --container openlane
   ```
   You should see logs like:
   ```bash
   [INFO] Detected design changes for 'spm' — updating state.
   [INFO] Re-running flow from stage 'floorplan' for design 'spm'
   [INFO] Flow completed successfully in 8.96 minutes.
   [INFO] Logged PD metrics → /Users/<you>/incremental_flow_accel/data/results_log.csv
   ```

---

## Tools Used
- **Python 3.11** – orchestration and logging
- **Docker + OpenLane 2.0** – RTL-to-GDSII automation
- **SkyWater 130 PDK** – validation process
- **Pandas** – QoR parsing and CSV logging
- **Watchdog** – file hash monitoring

--- 

## Motivation
While completing the Physical Design onboarding for the **Silicon Jackets** team, I noticed that each OpenLane or Innovus flow run often took over an hour — even for small design edits.
That long turnaround inspired me to experiment with incremental execution: a way to detect what actually changed and re-run only the affected stages.
This project became my independent attempt to replicate the runtime efficiency of professional ECO flows used in industry tools like Innovus or ICC2, using open-source infrastructure.
