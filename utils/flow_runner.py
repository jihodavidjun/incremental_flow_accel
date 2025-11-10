# utils/flow_runner.py
import subprocess, time
from pathlib import Path
from .qor_parser import extract_qor
from .logger import log_run
from .file_hash import hash_design, has_changes, detect_changed_stage  

<<<<<<< HEAD
def run_openlane(start_stage, design="spm", container="openlane"):
    # NOTE: flow.tcl auto-resumes cached runs internally
    cmd = f"docker exec {container} flow.tcl -design {design}"
=======
def run_openlane(start_stage=None, design="spm", container="openlane"):
    """
    Run OpenLane using docker exec inside the running container.
    Automatically checks for design file changes (incremental),
    parses QoR metrics, and logs results.
    """
    design_dir = f"{Path.home()}/OpenLane/designs/{design}"
>>>>>>> 5579002 (Added qor_parser.py; improved design)

    # ---------- Incremental detection ----------
    new_hashes = hash_design(design_dir)

    if not has_changes(design, new_hashes):
        print(f"[INFO] Skipping run — no changes since last flow for '{design}'.")
        return None

    # Determine which stage to start from
    stage = detect_changed_stage(design_dir, new_hashes)
    start_stage = stage or start_stage or "floorplan"
    print(f"[INFO] Re-running flow from stage '{start_stage}' for design '{design}'")

    # ---------- Run OpenLane flow ----------
    cmd = (
    f"docker exec {container} bash -c "
    f"'export OPENLANE_START={start_stage.capitalize()}; "
    f"flow.tcl -design {design}'"
    )
    print(f"[CMD] {cmd}")
    start_time = time.time()

    result = subprocess.run(cmd, shell=True)
    runtime_min = round((time.time() - start_time) / 60, 2)

    if result.returncode == 0:
        print(f"[INFO] Flow completed successfully in {runtime_min} minutes.")
    else:
        print(f"[ERROR] Flow failed at stage {start_stage}. Exit code: {result.returncode}")
        return None

    # ---------- Post-run QoR parsing ----------
    run_dir = f"/openlane/designs/{design}/runs"
    get_latest = f"docker exec {container} bash -c 'ls -td {run_dir}/*/ | head -1'"
    latest = subprocess.check_output(get_latest, shell=True).decode().strip().rstrip("/")
    print(f"[INFO] Parsing metrics from {latest}")

    # Convert container path → host path
    host_path = Path(f"openlane/designs/{design}/runs") / Path(latest).name

    # Extract PD metrics
    qor = extract_qor(str(host_path))
    qor["runtime_min"] = runtime_min
    qor["design"] = design
    qor["run"] = Path(latest).name

    # ---------- Log results ----------
    log_run(qor)
    return qor


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run OpenLane incrementally via Docker.")
    parser.add_argument("--design", default="spm", help="Design name inside OpenLane/designs/")
    parser.add_argument("--container", default="openlane", help="Docker container name")
    parser.add_argument("--stage", default="floorplan", help="Start stage (optional)")

    args = parser.parse_args()

    print(f"[DEBUG] Launching incremental run for {args.design} in {args.container}...")
    run_openlane(start_stage=args.stage, design=args.design, container=args.container)
