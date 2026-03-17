import json
import os
import shutil
import subprocess
import sys
import threading
from functools import partial
from pathlib import Path

import pystray
from PIL import Image, ImageDraw

_sf_cli_path = None
_app_dir = Path(__file__).resolve().parent

# Built-in defaults used when quick_pages.json is missing or invalid
_DEFAULT_QUICK_PAGES = [
    ("Home",              None),
    ("Setup",             "lightning/setup/SetupOneHome/home"),
    ("Dev Console",       "_ui/common/apex/debug/ApexCSIPage"),
    ("Flow Builder",      "lightning/setup/Flows/home"),
    ("Deployment Status", "lightning/setup/DeployStatus/home"),
]


def load_quick_pages():
    """Load quick-launch pages from quick_pages.json next to this script.

    Falls back to built-in defaults if the file is missing or malformed.
    """
    config_path = _app_dir / "quick_pages.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        return [(e["label"], e.get("path")) for e in entries]
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        return list(_DEFAULT_QUICK_PAGES)


def find_sf_cli():
    """Locate the sf CLI binary, searching PATH then common install locations."""
    global _sf_cli_path
    if _sf_cli_path is not None:
        return _sf_cli_path

    found = shutil.which("sf")
    if found:
        _sf_cli_path = found
        return _sf_cli_path

    candidates = []

    if sys.platform == "win32":
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        local_appdata = os.environ.get("LOCALAPPDATA", "")
        appdata = os.environ.get("APPDATA", "")

        candidates = [
            Path(program_files, "sf", "bin", "sf.cmd"),
            Path(program_files_x86, "sf", "bin", "sf.cmd"),
            Path(program_files, "sf", "bin", "sf.exe"),
            Path(program_files_x86, "sf", "bin", "sf.exe"),
        ]
        if local_appdata:
            candidates.append(Path(local_appdata, "sf", "bin", "sf.cmd"))
        if appdata:
            candidates.append(Path(appdata, "npm", "sf.cmd"))
            candidates.append(Path(appdata, "npm", "sf"))
    else:
        home = Path.home()
        candidates = [
            Path("/usr/local/bin/sf"),
            Path("/opt/homebrew/bin/sf"),
            home / ".local" / "bin" / "sf",
            Path("/usr/local/lib/node_modules/@salesforce/cli/bin/sf"),
        ]
        nvm_dir = home / ".nvm" / "versions" / "node"
        if nvm_dir.is_dir():
            for node_ver in sorted(nvm_dir.iterdir(), reverse=True):
                candidates.append(node_ver / "bin" / "sf")

    for path in candidates:
        if path.is_file():
            _sf_cli_path = str(path)
            return _sf_cli_path

    return None


def create_icon_image():
    """Generate a small Salesforce-style cloud icon programmatically."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse([8, 20, 36, 48], fill="#1B96FF")
    draw.ellipse([20, 12, 52, 44], fill="#1B96FF")
    draw.ellipse([36, 18, 58, 50], fill="#1B96FF")
    draw.rectangle([18, 30, 52, 48], fill="#1B96FF")

    draw.ellipse([14, 26, 30, 42], fill="white")
    draw.ellipse([24, 18, 46, 38], fill="white")
    draw.ellipse([38, 24, 52, 44], fill="white")
    draw.rectangle([22, 32, 46, 42], fill="white")

    return img


def fetch_orgs():
    """Run sf org list --json and return parsed org info."""
    sf = find_sf_cli()
    if sf is None:
        return None, "SF CLI not found. Install it from https://developer.salesforce.com/tools/cli"

    try:
        result = subprocess.run(
            [sf, "org", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=120,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except subprocess.TimeoutExpired:
        return None, "SF CLI timed out"
    except Exception as e:
        return None, f"Error: {e}"

    try:
        data = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError):
        return None, "Failed to parse SF CLI output"

    orgs = []
    seen_usernames = set()
    result_data = data.get("result", {})

    for category in ("devHubs", "nonScratchOrgs", "sandboxes", "scratchOrgs", "other"):
        for org in result_data.get(category, []):
            alias = org.get("alias", "")
            username = org.get("username", "")
            status = org.get("connectedStatus", "Unknown")
            is_default = org.get("isDefaultUsername", False) or org.get("isDefaultDevHubUsername", False)
            instance_url = org.get("instanceUrl", "")

            identifier = alias or username
            if not identifier:
                continue

            dedup_key = username or identifier
            if dedup_key in seen_usernames:
                continue
            seen_usernames.add(dedup_key)

            if org.get("isDevHub"):
                org_type = "devhub"
            elif ".sandbox." in instance_url:
                org_type = "sandbox"
            elif ".scratch." in instance_url or category == "scratchOrgs":
                org_type = "scratch"
            else:
                org_type = "production"

            orgs.append({
                "alias": alias,
                "username": username,
                "identifier": identifier,
                "status": status,
                "is_default": is_default,
                "org_type": org_type,
            })

    return orgs, None


def open_org(alias_or_username, path=None):
    """Open an org in the default browser via sf org open.

    If *path* is given it is forwarded with --path so the browser lands
    directly on that Salesforce page (e.g. Setup, Dev Console).
    """
    sf = find_sf_cli()
    if sf is None:
        return
    cmd = [sf, "org", "open", "-o", alias_or_username]
    if path:
        cmd.extend(["--path", path])
    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except Exception:
        pass


def make_org_label(org):
    """Build a clean label: alias only, with markers for default/expired."""
    label = org["alias"] if org["alias"] else org["username"]

    if org["is_default"]:
        label = f"* {label}"

    status = (org["status"] or "").lower()
    if status not in ("connected", "active", "unknown", ""):
        label = f"{label}  [{org['status']}]"

    return label


def build_menu(icon):
    """Build the tray menu with current orgs."""
    orgs, error = fetch_orgs()

    if error:
        return pystray.Menu(
            pystray.MenuItem(error, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Refresh", lambda: refresh(icon)),
            pystray.MenuItem("Quit", lambda: icon.stop()),
        )

    if not orgs:
        return pystray.Menu(
            pystray.MenuItem("No orgs found", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Refresh", lambda: refresh(icon)),
            pystray.MenuItem("Quit", lambda: icon.stop()),
        )

    grouped = {}
    for org in orgs:
        grouped.setdefault(org["org_type"], []).append(org)

    items = []

    sections = [
        ("production", "Production"),
        ("sandbox", "Sandboxes"),
        ("scratch", "Scratch Orgs"),
        ("devhub", "Dev Hubs"),
    ]

    for key, section_label in sections:
        org_list = grouped.get(key, [])
        if not org_list:
            continue

        org_list.sort(key=lambda o: (not o["is_default"], o["identifier"].lower()))

        if items:
            items.append(pystray.Menu.SEPARATOR)
        items.append(pystray.MenuItem(f"  {section_label}", None, enabled=False))

        for org in org_list:
            org_label = make_org_label(org)
            ident = org["identifier"]

            # Build a submenu with quick-launch page shortcuts
            page_items = []
            for page_label, page_path in load_quick_pages():
                cb = partial(
                    lambda i, p, *_: open_org(i, p), ident, page_path
                )
                page_items.append(pystray.MenuItem(page_label, cb))

            items.append(
                pystray.MenuItem(org_label, pystray.Menu(*page_items))
            )

    if not items:
        items.append(pystray.MenuItem("No orgs found", None, enabled=False))

    items.append(pystray.Menu.SEPARATOR)
    items.append(pystray.MenuItem("Refresh", lambda *_: refresh(icon)))
    items.append(pystray.MenuItem("Quit", lambda *_: icon.stop()))

    return pystray.Menu(*items)


def refresh(icon):
    """Refresh the menu in a background thread to avoid blocking."""
    def _refresh():
        icon.menu = build_menu(icon)
        icon.update_menu()
    threading.Thread(target=_refresh, daemon=True).start()


def main():
    icon = pystray.Icon(
        name="sf-org-launcher",
        icon=create_icon_image(),
        title="SF Org Launcher",
    )
    icon.menu = build_menu(icon)
    icon.run()


if __name__ == "__main__":
    main()
