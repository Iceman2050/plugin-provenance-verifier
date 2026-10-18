"""CLI for plugin-provenance-verifier: scan | snapshot | diff."""
import argparse
import json
import sys

from .scanner import scan_plugins
from .snapshot import take_snapshot, save_snapshot, load_snapshot
from .differ import diff_snapshot


def cmd_scan(args):
    results = scan_plugins(args.plugins_dir)
    for pid, rec in results.items():
        print("== %s ==" % pid)
        if "error" in rec:
            print("  ERROR: %s" % rec["error"])
            continue
        print("  name:        %s" % rec["name"])
        print("  version:     %s" % rec["version"])
        print("  origin:      %s" % rec["origin"])
        print("  auto_update: %s" % rec["auto_update"])
        print("  mcp_servers: %s" % (", ".join(rec["mcp_servers"]) or "(none)"))
        print("  files:       %d" % len(rec["files"]))
        for w in rec["warnings"]:
            print("  WARNING: %s" % w)
    return 0


def cmd_snapshot(args):
    results = scan_plugins(args.plugins_dir)
    snap = take_snapshot(args.plugins_dir, results)
    path = save_snapshot(snap, args.snapshot_file)
    print("snapshot written to %s (%d plugins)" % (path, len(snap["plugins"])))
    return 0


def cmd_diff(args):
    results = scan_plugins(args.plugins_dir)
    snap = load_snapshot(args.snapshot_file)
    findings = diff_snapshot(results, snap)
    if not findings:
        print("OK: no drift since snapshot")
        return 0
    high = sum(1 for f in findings if f["severity"] == "high")
    print("DRIFT: %d finding(s), %d high severity" % (len(findings), high))
    for f in findings:
        print("[%s] %s %s: %s" % (f["severity"].upper(), f["plugin"], f["kind"], f["detail"]))
    return 1 if high else 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="plugin-provenance-verifier",
                                     description="Audit Claude Code plugin provenance and drift.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, helptext in (("scan", "audit plugin origins, auto-update, bundled MCP servers"),
                           ("snapshot", "record current plugin state"),
                           ("diff", "compare current state against a snapshot")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--plugins-dir", required=True, help="path to the plugins directory")
        if name in ("snapshot", "diff"):
            p.add_argument("--snapshot-file", required=True, help="path to the snapshot JSON")
    args = parser.parse_args(argv)
    if args.command == "scan":
        return cmd_scan(args)
    if args.command == "snapshot":
        return cmd_snapshot(args)
    return cmd_diff(args)


if __name__ == "__main__":
    sys.exit(main())
