"""Write a fully pinned runtime lock from installed package metadata.

Usage: python scripts/resolve_runtime_lock.py --python-version 3.12 --platform linux|windows
The installed package versions provide the resolution; markers are evaluated for the target.
"""
from __future__ import annotations

import argparse
from importlib import metadata
from pathlib import Path

from packaging.markers import default_environment
from packaging.requirements import Requirement

ROOTS = ["streamlit", "plotly", "pandas", "numpy", "scikit-learn", "networkx", "joblib"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--python-version", default="3.12")
    parser.add_argument("--platform", choices=("linux", "windows"), default="linux")
    parser.add_argument("--output", default="requirements-lock.txt")
    args = parser.parse_args()

    env = default_environment()
    major, minor = args.python_version.split(".")[:2]
    env.update({"python_version": f"{major}.{minor}", "python_full_version": f"{major}.{minor}.0",
                "sys_platform": "linux" if args.platform == "linux" else "win32",
                "platform_system": "Linux" if args.platform == "linux" else "Windows",
                "platform_python_implementation": "CPython", "implementation_name": "cpython"})
    pending, selected = list(ROOTS), {}
    while pending:
        name = pending.pop()
        key = name.lower().replace("_", "-")
        if key in selected:
            continue
        dist = metadata.distribution(name)
        selected[key] = (dist.metadata["Name"], dist.version)
        for raw in dist.requires or []:
            req = Requirement(raw)
            if req.marker is None or req.marker.evaluate(env):
                pending.append(req.name)

    lines = ["# Fully pinned runtime dependency closure.",
             f"# Resolved for CPython {args.python_version} on {args.platform}; regenerate after dependency changes."]
    lines.extend(f"{name}=={version}" for name, version in sorted(selected.values(), key=lambda x: x[0].lower()))
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}: {len(selected)} pinned packages")


if __name__ == "__main__":
    main()
