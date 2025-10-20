import os, json
from utils.file_hash import collect_hashes, load_state, save_state
from utils.flow_runner import run_openlane
from utils.logger import log_result, console
from utils.openlane_manager import ensure_openlane_container  

def detect_changed_stage():
    # Load flow dependencies (maps stages to file patterns)
    with open("config/flow_dependencies.json") as f:
        deps = json.load(f)

    # Load previous state (old hashes)
    old_state = load_state()
    new_state = {}

    # Compute new hashes for each stage
    for stage, patterns in deps["stages"].items():
        new_state[stage] = collect_hashes(patterns)

    # Compare stage by stage to find first change
    first_changed = None
    for stage in deps["stage_order"]:
        old_hashes = old_state.get(stage, {})
        new_hashes = new_state.get(stage, {})
        if old_hashes != new_hashes:
            first_changed = stage
            break

    # Save updated state for next run
    save_state(new_state)

    # If nothing changed, return empty list
    if not first_changed:
        return []

    # Return list of affected stages: the first changed stage and all downstream stages
    order = deps["stage_order"]
    try:
        idx = order.index(first_changed)
    except ValueError:
        return [first_changed]

    return order[idx:]


if __name__ == "__main__":
    affected_stages = detect_changed_stage()

    if affected_stages:
        start_stage = affected_stages[0]
        console.log(f"[bold yellow]Detected change affecting stages:[/bold yellow] {affected_stages}")

        # Auto-start OpenLane container if it's not running
        if not ensure_openlane_container():
            console.log("[bold red]Failed to connect to or start OpenLane container. Exiting.[/bold red]")
            exit(1)

        # Run the OpenLane flow from the changed stage
        container_name = ensure_openlane_container() or "openlane"
        runtime, code = run_openlane(start_stage, design="spm", container=container_name)

        # Log the runtime result
        log_result(start_stage, runtime)

        console.log(f"[bold cyan]Re-run from {start_stage} finished in {runtime} min (code {code})[/bold cyan]")
    else:
        console.log("[bold green]No changes detected. Skipping flow re-run.[/bold green]")
