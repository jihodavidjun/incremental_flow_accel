import subprocess, time

def run_openlane(start_stage, design="spm", container="openlane"):
    # NOTE: flow.tcl auto-resumes cached runs internally
    cmd = f"docker exec {container} flow.tcl -design {design}"

    print(f"[INFO] Starting OpenLane from stage: {start_stage}")
    start_time = time.time()

    # Run the flow
    result = subprocess.run(cmd, shell=True)
    runtime = round((time.time() - start_time) / 60, 2)

    if result.returncode == 0:
        print(f"[INFO] ✅ Flow completed successfully in {runtime} minutes.")
    else:
        print(f"[ERROR] ❌ Flow failed at stage {start_stage}. Exit code: {result.returncode}")

    return runtime, result.returncode
