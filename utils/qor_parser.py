# utils/qor_parser.py
import os, re, csv, glob
from pathlib import Path

def _read_text(p: Path) -> str:
    return p.read_text(errors="ignore") if p.exists() else ""

def _parse_sta(reports_dir: Path):
    """Return (WNS, TNS). Prefer summary; fall back to computing from max.rpt."""
    wns = tns = None
    summary = reports_dir / "31-rcx_sta.summary.rpt"
    maxrpt  = reports_dir / "31-rcx_sta.max.rpt"

    if summary.exists():
        s = _read_text(summary)
        m = re.search(r"WNS[^-\d]*([-\d.]+)", s, re.I)
        if m: wns = float(m.group(1))
        m = re.search(r"TNS[^-\d]*([-\d.]+)", s, re.I)
        if m: tns = float(m.group(1))

    if (wns is None or tns is None) and maxrpt.exists():
        slacks = []
        for line in _read_text(maxrpt).splitlines():
            if "slack" in line.lower():
                tok = line.strip().split()[-1]
                try: slacks.append(float(tok))
                except: pass
        if slacks:
            wns = min(slacks)
            tns = sum(x for x in slacks if x < 0)

    if tns is None and wns is not None and wns >= 0:
        tns = 0.0

    return wns, tns

def _parse_drc(reports_dir: Path):
    drc = reports_dir / "drc.rpt"
    if drc.exists():
        for line in reversed(_read_text(drc).splitlines()):
            if "violation" in line.lower():
                m = re.search(r"(\d+)\s*$", line)
                if m: return int(m.group(1))
    return None

def _parse_metrics_csv(run_root: Path):
    candidates = [run_root / "reports" / "metrics.csv",
                  run_root / "reports" / "signoff" / "metrics.csv"]
    for f in candidates:
        if f.exists():
            rows = list(csv.DictReader(open(f, newline="")))
            if not rows: break
            last = rows[-1]

            def pick(d, *keys):
                for k in keys:
                    if k in d and d[k] not in ("", None): return d[k]
                return None
            cell = pick(last, "cell_area", "CELL_AREA", "cellarea")
            die  = pick(last, "die_area",  "DIE_AREA",  "diearea", "DIEAREA")
            return (float(cell) if cell else None,
                    float(die)  if die  else None)
    return (None, None)

def _die_area_from_def(run_root: Path):
    defs = glob.glob(str(run_root / "results" / "final" / "*" / "*.def"))
    if not defs: return None
    text = Path(defs[0]).read_text(errors="ignore")
    mu = re.search(r'UNITS\s+DISTANCE\s+MICRONS\s+(\d+)', text)
    md = re.search(r'DIEAREA\s*\(\s*\d+\s+\d+\s*\)\s*\(\s*(\d+)\s+(\d+)\s*\)', text)
    if mu and md:
        dbu = float(mu.group(1))
        x, y = float(md.group(1)), float(md.group(2))
        return (x/dbu) * (y/dbu)  # µm^2
    return None

def extract_qor(run_root: str):
    run_root = Path(run_root)
    rpt_dir = run_root / "reports" / "signoff"
    if not rpt_dir.exists(): rpt_dir = run_root / "reports"  

    wns, tns = _parse_sta(rpt_dir)
    drc = _parse_drc(rpt_dir)
    cell_area, die_area = _parse_metrics_csv(run_root)
    if die_area is None:
        die_area = _die_area_from_def(run_root)

    return {"WNS": wns, "TNS": tns, "DRC": drc,
            "cell_area": cell_area, "die_area": die_area}
