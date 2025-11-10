# utils/file_hash.py
import hashlib, json, glob
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parents[1] / "data" / "flow_state.json"
FLOW_DEPS = Path(__file__).resolve().parents[1] / "config" / "flow_dependencies.json"

def hash_file(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def hash_design(design_dir: str) -> dict:
    """
    Compute combined hashes for all Verilog/LEF/DEF files
    inside the given OpenLane design directory.
    """
    # Always resolve to the actual OpenLane location in your home directory
    if "OpenLane" not in design_dir:
        design_dir = f"{Path.home()}/OpenLane/designs/{Path(design_dir).name}"

    design_path = Path(design_dir).expanduser().resolve()
    print(f"[DEBUG] Hashing design path: {design_path}")
    exts = {".v", ".sv", ".lef", ".def", ".tcl", ".cfg"}
    hashes = {}

    if not design_path.exists():
        print(f"[ERROR] Design directory not found: {design_path}")
        return hashes

    for f in sorted(design_path.rglob("*")):
        if f.suffix.lower() in exts and f.is_file():
            hashes[str(f)] = hash_file(f)

    print(f"[DEBUG] Found {len(hashes)} files in {design_path}")
    return hashes

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def has_changes(design: str, new_hashes: dict) -> bool:
    """Compare new vs old hashes and update the state if changed."""
    state = load_state()
    old_hashes = state.get(design, {})
    if old_hashes != new_hashes:
        print(f"[INFO] Detected design changes for '{design}' — updating state.")
        state[design] = new_hashes
        save_state(state)
        return True
    print(f"[SKIP] 🔄 No design changes detected for '{design}'.")
    return False

def detect_changed_stage(design_dir: str, new_hashes: dict) -> str:
    """
    Determine which stage should be re-run based on changed files
    and config/flow_dependencies.json.
    """
    deps = json.loads(FLOW_DEPS.read_text())
    stages = deps["stages"]
    order = deps["stage_order"]

    state = load_state()
    old_hashes = state.get(design_dir.split("/")[-1], {})

    changed_files = [
        f for f, h in new_hashes.items()
        if old_hashes.get(f) != h
    ]
    if not changed_files:
        return None

    # Match each changed file to its corresponding stage
    triggered = set()
    for stage, patterns in stages.items():
        for pattern in patterns:
            for file_path in changed_files:
                for p in glob.glob(pattern):
                    if Path(file_path).resolve() == Path(p).resolve():
                        triggered.add(stage)

    # Return earliest stage (lowest in stage_order)
    if triggered:
        for s in order:
            if s in triggered:
                return s
    return "floorplan"

if __name__ == "__main__":
    d = "openlane/designs/spm"
    hashes = hash_design(d)
    print(f"Found {len(hashes)} files:")
    for f in hashes:
        print(" -", f)
