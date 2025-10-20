import subprocess, time
from rich.console import Console

console = Console()

def get_openlane_container_name():
    result = subprocess.run(
        "docker ps --format '{{.Image}} {{.Names}}' | grep 'openroad-project/openlane' | head -n 1 | awk '{print $2}'",
        shell=True, capture_output=True, text=True
    )
    name = result.stdout.strip()
    return name if name else None


def ensure_openlane_container(timeout=30):
    name = get_openlane_container_name()
    if name:
        console.log(f"[bold green]OpenLane container already running:[/bold green] {name}")
        return name

    console.log("[bold yellow]Starting OpenLane container...[/bold yellow]")
    subprocess.Popen("cd ~/OpenLane && make mount", shell=True)
    console.log("[green]Container launch initiated![/green]")

    # Wait until the container is visible to Docker
    for i in range(timeout):
        time.sleep(2)
        name = get_openlane_container_name()
        if name:
            console.log(f"[bold green]Container ready:[/bold green] {name}")
            return name
        else:
            console.log(f"[dim]...waiting for container ({2*(i+1)}s)...[/dim]")

    console.log("[bold red]Failed to connect to or start OpenLane container. Exiting.[/bold red]")
    return None
