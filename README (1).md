# 🛡 Clan PC Check — Anti-Cheat Scanner

A lightweight Windows tool for clan leaders to verify that applicants don't have Roblox executors, exploits, or cheat software installed.

## What It Scans

| Check | Details |
|---|---|
| **Running Processes** | Detects executor processes currently running |
| **Known Folders** | Checks AppData/LocalAppData for cheat installs |
| **Registry Keys** | Looks for leftover registry entries |
| **Installed Programs** | Checks Add/Remove Programs for cheat software |

### Executors Detected
Synapse X, KRNL, Fluxus, Scriptware, Proxo, Arceus X, Oxygen U, Trigon, Codex, Coco Z, Evon, Vega X, Sentinel, JJSploit, Calamari, Xeno, Wave, and more.

## Usage

1. Download `ClanCheck.exe` from [Releases](../../releases)
2. Have your applicant run it on their PC
3. They screenshot or report the **PASS / FAIL** result to you

## Build From Source

```bash
# Install dependencies
pip install pyinstaller

# Build the .exe
pyinstaller --onefile --windowed --name ClanCheck src/scanner.py
# Output: dist/ClanCheck.exe
```

## Adding More Executors

Edit `EXECUTOR_NAMES` and `EXECUTOR_PATHS` in `src/scanner.py` to add new cheats as they appear.

## Notes
- Runs entirely locally — no data is sent anywhere
- Requires Windows (uses `winreg` and `tasklist`)
- May need to be run as Administrator for full registry access
