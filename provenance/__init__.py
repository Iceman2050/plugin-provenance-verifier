"""plugin-provenance-verifier: audit where Claude Code plugins came from and catch silent drift."""
from .scanner import scan_plugins, load_manifest
from .snapshot import take_snapshot, save_snapshot, load_snapshot
from .differ import diff_snapshot

__all__ = ["scan_plugins", "load_manifest", "take_snapshot", "save_snapshot", "load_snapshot", "diff_snapshot"]
