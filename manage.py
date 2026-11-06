#!/usr/bin/env python3
"""Compatibility entry point; prefer install.py."""

import subprocess, sys
from pathlib import Path

if len(sys.argv) < 2:
    raise SystemExit("Usage: python3 manage.py install|update|status|check")
command = sys.argv[1]
if command in ("install", "update", "check"):
    subprocess.run(
        [sys.executable, str(Path(__file__).with_name("install.py"))]
        + ({"install": [], "update": ["--update"], "check": ["--check"]}[command]),
        check=True,
    )
elif command == "status":
    subprocess.run(
        [
            "systemctl",
            "status",
            "h200-console-web.service",
            "h200-console-broker.service",
        ]
    )
else:
    raise SystemExit("Unsupported command. Container creation is disabled.")
