"""Snapshot the scanned state of plugins so later runs can diff against it."""
import json
import os
from datetime import datetime, timezone

SNAPSHOT_FORMAT_VERSION = 1


def take_snapshot(plugins_dir, scan_results=None):
    from .scanner import scan_plugins
    scan_results = scan_results if scan_results is not None else scan_plugins(plugins_dir)
    snapshot = {
        "format_version": SNAPSHOT_FORMAT_VERSION,
        "taken_at": datetime.now(timezone.utc).isoformat(),
        "plugins_dir": os.path.abspath(plugins_dir),
        "plugins": {
            pid: {k: v for k, v in rec.items() if k in (
                "name", "version", "origin", "official", "auto_update", "mcp_servers", "files")}
            for pid, rec in scan_results.items() if "error" not in rec
        },
    }
    return snapshot


def save_snapshot(snapshot, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, sort_keys=True)
    return path


def load_snapshot(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or data.get("format_version") != SNAPSHOT_FORMAT_VERSION:
        raise ValueError("not a compatible plugin-provenance-verifier snapshot: %s" % path)
    return data
