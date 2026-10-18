"""Compare a fresh scan against a snapshot and flag drift."""


def diff_snapshot(scan_results, snapshot):
    """Return list of finding dicts: {plugin, kind, severity, detail}."""
    findings = []
    snap_plugins = snapshot.get("plugins", {})

    for pid, snap in snap_plugins.items():
        cur = scan_results.get(pid)
        if cur is None or "error" in cur:
            findings.append({
                "plugin": pid, "kind": "PLUGIN_REMOVED", "severity": "high",
                "detail": "plugin was in snapshot but is no longer installed",
            })
            continue
        if cur["version"] != snap.get("version"):
            findings.append({
                "plugin": pid, "kind": "VERSION_DRIFT", "severity": "high",
                "detail": "version changed %s -> %s%s" % (
                    snap.get("version"), cur["version"],
                    " with auto-update ON: behavior may have changed silently"
                    if cur.get("auto_update") else ""),
            })
        old_mcp, new_mcp = set(snap.get("mcp_servers", [])), set(cur.get("mcp_servers", []))
        for server in sorted(new_mcp - old_mcp):
            findings.append({
                "plugin": pid, "kind": "NEW_MCP_SERVER", "severity": "high",
                "detail": "new bundled MCP server appeared since snapshot: %s" % server,
            })
        for server in sorted(old_mcp - new_mcp):
            findings.append({
                "plugin": pid, "kind": "MCP_SERVER_REMOVED", "severity": "medium",
                "detail": "bundled MCP server disappeared since snapshot: %s" % server,
            })
        old_files, new_files = snap.get("files", {}), cur.get("files", {})
        for rel in sorted(set(new_files) - set(old_files)):
            findings.append({
                "plugin": pid, "kind": "FILE_ADDED", "severity": "medium",
                "detail": "new file since snapshot: %s" % rel,
            })
        for rel in sorted(set(old_files) - set(new_files)):
            findings.append({
                "plugin": pid, "kind": "FILE_REMOVED", "severity": "medium",
                "detail": "file missing since snapshot: %s" % rel,
            })
        for rel in sorted(set(old_files) & set(new_files)):
            if old_files[rel] != new_files[rel]:
                findings.append({
                    "plugin": pid, "kind": "FILE_CHANGED", "severity": "high",
                    "detail": "file content changed since snapshot: %s" % rel,
                })

    for pid, cur in scan_results.items():
        if "error" in cur:
            continue
        if pid not in snap_plugins:
            findings.append({
                "plugin": pid, "kind": "PLUGIN_ADDED", "severity": "medium",
                "detail": "plugin installed after snapshot was taken (%s)" % cur.get("origin"),
            })
        elif not cur.get("official"):
            findings.append({
                "plugin": pid, "kind": "SIDELOADED_ORIGIN", "severity": "low",
                "detail": "declared origin is not the official directory: %s (declared, not independently verified)" % cur.get("origin"),
            })

    return findings
