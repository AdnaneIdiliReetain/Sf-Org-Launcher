# SF Org Launcher

A lightweight system tray app that lets you open Salesforce orgs directly from your taskbar. Works on **macOS** and **Windows**.

Right-click the cloud icon to see your orgs grouped by type. Hover over any org to quick-launch **Setup**, **Dev Console**, **Flow Builder**, and more.

## Prerequisites

- Python 3.8+
- [Salesforce CLI](https://developer.salesforce.com/tools/cli) (`sf`) installed and on your PATH
- At least one authenticated org (`sf org login web`)

## Quick Start (from source)

```bash
pip install -r requirements.txt
python org_launcher.py
```

## Build as Standalone App

### macOS

```bash
./build.sh
```

Output: `dist/SF Org Launcher.app` — double-click to run (no Python required).

### Windows

```cmd
build.bat
```

Output: `dist\SF Org Launcher.exe` — double-click to run (no Python required).

## Install & Launch at Login

### macOS

```bash
./install.sh
```

This copies the app to `/Applications` and registers it to start automatically at login.

To start immediately: `open -a "SF Org Launcher"`

### Windows

```cmd
install.bat
```

This copies the exe to `%LOCALAPPDATA%\SF Org Launcher` and adds it to your startup programs.

## macOS: First Launch

Because the app is not signed with an Apple Developer certificate, macOS Gatekeeper will show a warning on the first launch. To open it:

1. **Right-click** (or Control-click) the app and choose **Open**
2. In the dialog that appears, click **Open** again

This only needs to be done once — macOS remembers your choice and won't ask again.

Alternatively, if you used `install.sh`, the quarantine flag is automatically stripped and the app should open without any warning.

## Customising Quick-Launch Pages

Edit `quick_pages.json` to add, remove, or reorder the pages shown in each org's submenu:

```json
[
    { "label": "Home",              "path": null },
    { "label": "Setup",             "path": "lightning/setup/SetupOneHome/home" },
    { "label": "Dev Console",       "path": "_ui/common/apex/debug/ApexCSIPage" },
    { "label": "Flow Builder",      "path": "lightning/setup/Flows/home" },
    { "label": "Deployment Status", "path": "lightning/setup/DeployStatus/home" }
]
```

Set `"path": null` for the default org home page. Changes take effect on the next **Refresh**.

## Menu Overview

- **Org submenu** → Home · Setup · Dev Console · Flow Builder · Deployment Status
- **Refresh** — re-fetches the org list from the CLI
- **Quit** — exits the app
