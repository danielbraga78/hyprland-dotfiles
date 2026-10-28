#!/usr/bin/env python3
import fcntl
import json
import logging
import os
import socket
import subprocess
import time
from pathlib import Path

MIN_WORKSPACES = 3
RECONCILE_EVENTS = {
    "closewindow",
    "configreloaded",
    "createworkspace",
    "createworkspacev2",
    "destroyworkspace",
    "destroyworkspacev2",
    "movewindow",
    "movewindoworgroup",
    "movewindowv2",
    "openwindow",
    "workspace",
    "workspacev2",
}
DEBOUNCE_SECONDS = 0.15
RECONCILE_INTERVAL_SECONDS = 2


def hyprctl_json(command):
    result = subprocess.run(
        ["hyprctl", "-j", command],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def workspace_plan(workspaces):
    numeric = {
        int(workspace["id"]): int(workspace.get("windows", 0))
        for workspace in workspaces
        if int(workspace["id"]) > 0
    }
    occupied_ids = sorted(
        workspace_id
        for workspace_id, window_count in numeric.items()
        if window_count > 0
    )
    moves = {
        source_id: target_id
        for target_id, source_id in enumerate(occupied_ids, start=1)
        if source_id != target_id
    }

    desired_persistence = {
        workspace_id: True
        for workspace_id in range(1, MIN_WORKSPACES + 1)
    }
    desired_persistence.update(
        {workspace_id: False for workspace_id in numeric if workspace_id > MIN_WORKSPACES}
    )

    trailing_id = (
        len(occupied_ids) + 1
        if len(occupied_ids) >= MIN_WORKSPACES
        else None
    )
    create_id = None
    if trailing_id is not None:
        desired_persistence[trailing_id] = True
        if trailing_id not in numeric:
            create_id = trailing_id

    return desired_persistence, create_id, moves


def active_workspace_after_compaction(active_id, occupied_ids, moves):
    if active_id in moves:
        return moves[active_id]
    if (
        active_id > MIN_WORKSPACES
        and active_id not in occupied_ids
        and active_id not in moves.values()
    ):
        return max(MIN_WORKSPACES, len(occupied_ids) + 1)
    return None


def set_persistent(workspace_id, persistent):
    value = "true" if persistent else "false"
    expression = (
        f'hl.workspace_rule({{ workspace = "{workspace_id}", persistent = {value} }})'
    )
    result = subprocess.run(
        ["hyprctl", "eval", expression],
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip() != "ok":
        raise RuntimeError(
            f"Could not update persistence for workspace {workspace_id}: "
            f"{result.stdout.strip()}"
        )


def move_window(address, workspace_id):
    if not address.startswith("0x") or not all(
        character in "0123456789abcdefABCDEF"
        for character in address[2:]
    ):
        raise ValueError(f"Invalid Hyprland window address: {address!r}")

    expression = (
        "hl.dsp.window.move({ "
        f'workspace = "{workspace_id}", '
        f'window = "address:{address}", '
        "follow = false })"
    )
    result = subprocess.run(
        ["hyprctl", "dispatch", expression],
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip() != "ok":
        raise RuntimeError(f"Could not move window {address}: {result.stdout.strip()}")


def focus_workspace(workspace_id):
    expression = f'hl.dsp.focus({{ workspace = "{workspace_id}" }})'
    result = subprocess.run(
        ["hyprctl", "dispatch", expression],
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip() != "ok":
        raise RuntimeError(f"Could not focus workspace {workspace_id}: {result.stdout.strip()}")


def reconcile():
    rules = hyprctl_json("workspacerules")
    persistence = {
        int(rule["workspaceString"]): rule.get("persistent", False)
        for rule in rules
        if rule.get("workspaceString", "").isdecimal()
    }

    for workspace_id in range(1, MIN_WORKSPACES + 1):
        if not persistence.get(workspace_id, False):
            set_persistent(workspace_id, True)
            persistence[workspace_id] = True

    workspaces = hyprctl_json("workspaces")
    active_id = int(hyprctl_json("activeworkspace")["id"])
    desired, create_id, moves = workspace_plan(workspaces)
    occupied_ids = {
        int(workspace["id"])
        for workspace in workspaces
        if int(workspace["id"]) > 0 and int(workspace.get("windows", 0)) > 0
    }
    workspace_ids = {
        int(workspace["id"])
        for workspace in workspaces
        if int(workspace["id"]) > 0
    }
    focus_id = active_workspace_after_compaction(active_id, occupied_ids, moves)

    if moves:
        for workspace_id, persistent in desired.items():
            if persistent and not persistence.get(workspace_id, False):
                set_persistent(workspace_id, True)

        clients = hyprctl_json("clients")
        for client in clients:
            source_id = int(client.get("workspace", {}).get("id", 0))
            if source_id in moves:
                move_window(client["address"], moves[source_id])

        if focus_id is not None:
            focus_workspace(focus_id)

        logging.info("Compacted workspaces: %s", moves)
        return

    for workspace_id, persistent in desired.items():
        if (
            persistence.get(workspace_id, False) != persistent
            or (workspace_id in workspace_ids and workspace_id not in persistence)
        ):
            set_persistent(workspace_id, persistent)
            logging.info(
                "%s persistence for workspace %s",
                "Enabled" if persistent else "Disabled",
                workspace_id,
            )

    if focus_id is not None:
        focus_workspace(focus_id)

    if create_id is not None:
        logging.info("Created empty workspace %s", create_id)


def serve(socket_path):
    while True:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                connection.connect(socket_path)
                connection.settimeout(0.5)
                reconcile()
                pending_since = None
                last_reconcile = time.monotonic()
                buffer = b""

                while True:
                    try:
                        chunk = connection.recv(4096)
                    except socket.timeout:
                        chunk = None

                    if chunk is None:
                        now = time.monotonic()
                        if (
                            pending_since is not None
                            and now - pending_since >= DEBOUNCE_SECONDS
                        ) or (
                            now - last_reconcile >= RECONCILE_INTERVAL_SECONDS
                        ):
                            reconcile()
                            pending_since = None
                            last_reconcile = now
                        continue
                    if chunk == b"":
                        raise ConnectionError("Hyprland event socket closed")

                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        event_name = line.partition(b">>")[0].decode(
                            "utf-8",
                            errors="replace",
                        )
                        if event_name in RECONCILE_EVENTS:
                            pending_since = time.monotonic()

                    now = time.monotonic()
                    if (
                        pending_since is not None
                        and now - pending_since >= DEBOUNCE_SECONDS
                    ) or (
                        now - last_reconcile >= RECONCILE_INTERVAL_SECONDS
                    ):
                        reconcile()
                        pending_since = None
                        last_reconcile = now
        except (
            OSError,
            subprocess.CalledProcessError,
            json.JSONDecodeError,
            RuntimeError,
        ) as error:
            if not Path(socket_path).exists():
                logging.info("Hyprland session ended; stopping the workspace manager")
                return
            logging.error("Dynamic workspace manager will retry after an error: %s", error)
            time.sleep(1)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    signature = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if not runtime_dir or not signature:
        raise RuntimeError("Hyprland runtime environment is missing")

    runtime_path = Path(runtime_dir)
    lock_path = runtime_path / f"dynamic-workspaces-{signature}.lock"
    lock_file = lock_path.open("w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        logging.info("A dynamic workspace manager is already running")
        return

    socket_path = runtime_path / "hypr" / signature / ".socket2.sock"
    startup_deadline = time.monotonic() + 15
    while not socket_path.exists():
        if time.monotonic() >= startup_deadline:
            raise RuntimeError("Hyprland event socket did not become available")
        time.sleep(0.25)
    serve(str(socket_path))


if __name__ == "__main__":
    main()
