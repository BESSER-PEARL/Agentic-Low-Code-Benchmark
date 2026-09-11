"""Run the acceptance suite and record the result, so a number can be checked.

Writes one directory under runs/ holding the raw behave output for every feature
folder, plus a manifest saying what was measured and against what. Nothing is
summarised by hand: the totals in the manifest are parsed from the output stored
next to them.

    python record_run.py --label besser-7.16.1 --tool "BESSER generators" \
        --notes "app generated from editor.besser-pearl.org"

The application under test must already be running, on the addresses the suite
uses (BENCH_API / BENCH_UI, default http://localhost:8000 and :3000).
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDERS = ["basic_functionality", "constraints", "behavior"]

# behave's closing summary, e.g. "22 scenarios passed, 1 failed, 0 skipped"
SUMMARY = re.compile(
    r"^(?P<passed>\d+) (?:scenario|scenarios) passed, (?P<failed>\d+) failed, "
    r"(?P<skipped>\d+) skipped(?:, (?P<untested>\d+) untested)?",
    re.M,
)
DURATION = re.compile(r"^Took (?:(?P<mins>\d+)min\s*)?(?P<secs>[\d.]+)s", re.M)
FAILING = re.compile(r"^(?:Failing|Errored) scenarios:\n((?:  .*\n)+)", re.M)


def git(*args: str, cwd: Path) -> str:
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def working_tree_dirty(runs_dir: Path) -> bool:
    """Whether anything outside the recorded runs is uncommitted.

    Recording writes its own logs, which makes the tree dirty by definition, so
    the run directory is excluded - otherwise every run would flag itself as
    unreproducible and the flag would say nothing.
    """
    status = git("status", "--porcelain", cwd=HERE)
    if status == "unknown":
        return False
    marker = runs_dir.name
    changed = []
    for line in status.splitlines():
        path = line[3:].strip().strip('"')
        if marker in path:
            continue
        changed.append(path)
    return bool(changed)


def run_folder(folder: str, out_dir: Path) -> dict:
    """Run one feature folder, store its output verbatim, return what it said."""
    proc = subprocess.run(
        [sys.executable, "-m", "behave", f"features/{folder}/"],
        cwd=HERE, capture_output=True, text=True,
    )
    output = proc.stdout + proc.stderr
    (out_dir / f"{folder}.txt").write_text(output, encoding="utf-8")

    summary = SUMMARY.search(output)
    duration = DURATION.search(output)
    failing = FAILING.search(output)
    return {
        "passed": int(summary["passed"]) if summary else None,
        "failed": int(summary["failed"]) if summary else None,
        "skipped": int(summary["skipped"]) if summary else None,
        "seconds": (int(duration["mins"]) * 60 + float(duration["secs"])) if duration else None,
        "failing_scenarios": [line.strip() for line in failing[1].splitlines()] if failing else [],
        "exit_code": proc.returncode,
        "log": f"{folder}.txt",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True,
                        help="directory name for this run, e.g. besser-7.16.1")
    parser.add_argument("--tool", required=True,
                        help="what produced the application under test")
    parser.add_argument("--approach", default="Pure low-code",
                        help="how it was produced: pure low-code, hybrid, LLM-only, ...")
    parser.add_argument("--llm", default="No LLM", help="model tier used, if any")
    parser.add_argument("--tool-version", required=True,
                        help="version of the tool that produced the application under test. "
                             "Stated by whoever runs this: the runner cannot detect it, and "
                             "the version installed beside the test suite is not the one that "
                             "built the app.")
    parser.add_argument("--notes", default="", help="anything a reader needs to interpret the run")
    args = parser.parse_args()

    stamp = datetime.date.today().isoformat()
    out_dir = HERE / "runs" / f"{stamp}-{args.label}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Measured before the run writes anything of its own.
    dirty_before_run = working_tree_dirty(out_dir)

    results = {folder: run_folder(folder, out_dir) for folder in FOLDERS}
    counted = [r for r in results.values() if r["passed"] is not None]

    manifest = {
        "recorded": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "approach": args.approach,
        "tool": args.tool,
        "llm": args.llm,
        "notes": args.notes,
        "under_test": {
            "version": args.tool_version,
            "api": os.getenv("BENCH_API", "http://localhost:8000"),
            "ui": os.getenv("BENCH_UI", "http://localhost:3000"),
        },
        "benchmark": {
            "commit": git("rev-parse", "--short", "HEAD", cwd=HERE),
            "model_last_changed": git(
                "log", "-1", "--format=%h %ad", "--date=short", "--",
                "../low-code-model/model.json", cwd=HERE),
            "dirty": dirty_before_run,
        },
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "results": results,
        "totals": {
            "passed": sum(r["passed"] for r in counted),
            "failed": sum(r["failed"] for r in counted),
            "total": sum(r["passed"] + r["failed"] for r in counted),
            "seconds": round(sum(r["seconds"] or 0 for r in counted), 1),
        },
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    t = manifest["totals"]
    print(f"recorded in {out_dir.relative_to(HERE)}")
    print(f"{t['passed']}/{t['total']} scenarios passed in {t['seconds']}s")
    for folder, r in results.items():
        print(f"  {folder:20s} {r['passed']}/{r['passed'] + r['failed']}")


if __name__ == "__main__":
    main()
