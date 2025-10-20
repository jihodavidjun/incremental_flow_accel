import os, glob, hashlib, json

def hash_file(path):
    """Compute MD5 hash for a single file."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        # Read in chunks so large files don't overload memory
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def collect_hashes(patterns):
    """
    Given a list of glob patterns, compute MD5 hashes
    for all matching files and return {path: hash}.
    """
    hashes = {}
    for pat in patterns:
        for path in glob.glob(pat, recursive=True):
            if os.path.isfile(path):
                hashes[path] = hash_file(path)
    return hashes

def save_state(state, path="data/flow_state.json"):
    """Save file hashes to disk as JSON."""
    with open(path, "w") as f:
        json.dump(state, f, indent=2)

def load_state(path="data/flow_state.json"):
    """Load previous file hashes from disk if available."""
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}
