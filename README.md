# SF Org Launcher

A lightweight system tray app that lets you open Salesforce orgs directly from your taskbar. Works on Windows and macOS.

## Prerequisites

- Python 3.8+
- [Salesforce CLI](https://developer.salesforce.com/tools/cli) (`sf`) installed and on your PATH
- At least one authenticated org (`sf org login web`)

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python org_launcher.py
```

A cloud icon appears in your system tray. Right-click it to see your orgs grouped by type (Dev Hubs, Sandboxes/Production, Scratch Orgs). Click any org to open it in your browser.

- **Refresh** -- re-fetches the org list from the CLI
- **Quit** -- exits the app

## Bundle as Executable (optional)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "SF Org Launcher" org_launcher.py
```

The resulting executable will be in the `dist/` folder.
