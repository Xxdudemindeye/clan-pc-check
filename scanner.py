import os
import sys
import subprocess
import winreg
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import datetime

# ── Known Roblox executor / cheat signatures ──────────────────────────────────
EXECUTOR_NAMES = [
    # Process names (lowercase)
    "synapse x", "synapsecrashhandler", "sxlib",
    "krnl", "krnlss",
    "fluxus", "fluxuscrashhandler",
    "electron", "electronui",           # used by several exploits
    "scriptware", "sw_bootstrapper",
    "proxo", "proxo.exe",
    "arceus x", "arceusxui",
    "oxygen u", "oxygencrash",
    "trigon", "trigonevo",
    "codex", "codex_loader",
    "coco z", "cocoz",
    "evon", "evon_bootstrapper",
    "vega x", "vegax",
    "sentinel",
    "jjsploit", "jjsploit_bootstrapper",
    "calamari",
    "xeno", "xenoui",
    "wave",
    "hydroxide",          # Lua decompiler / exploit utility
    "roblox_hack",
    "rbxfps", "rbxunlockfps",   # FPS unlocker variants used to DLL-inject
    "rbxfpsunlocker",
    "fps_unlocker",
]

EXECUTOR_PATHS = [
    r"%LOCALAPPDATA%\Synapse X",
    r"%LOCALAPPDATA%\KRNL",
    r"%LOCALAPPDATA%\Fluxus",
    r"%LOCALAPPDATA%\Scriptware",
    r"%APPDATA%\Proxo",
    r"%LOCALAPPDATA%\Electron",
    r"%LOCALAPPDATA%\Trigon",
    r"%LOCALAPPDATA%\Codex",
    r"%LOCALAPPDATA%\CocoZ",
    r"%LOCALAPPDATA%\Evon",
    r"%LOCALAPPDATA%\VegaX",
    r"%LOCALAPPDATA%\Sentinel",
    r"%LOCALAPPDATA%\JJSploit",
    r"%APPDATA%\Calamari",
    r"%LOCALAPPDATA%\Xeno",
    r"%LOCALAPPDATA%\Wave",
    r"%APPDATA%\Synapse X",
    r"%APPDATA%\KRNL",
    r"%APPDATA%\Fluxus",
    r"%APPDATA%\Scriptware",
    r"%LOCALAPPDATA%\RbxFpsUnlocker",
    r"%USERPROFILE%\Downloads\Synapse",
    r"%USERPROFILE%\Downloads\KRNL",
    r"%USERPROFILE%\Desktop\Synapse X",
    r"%USERPROFILE%\Desktop\KRNL",
]

EXECUTOR_REG_KEYS = [
    (winreg.HKEY_CURRENT_USER,  r"Software\Synapse X"),
    (winreg.HKEY_CURRENT_USER,  r"Software\KRNL"),
    (winreg.HKEY_CURRENT_USER,  r"Software\Fluxus"),
    (winreg.HKEY_CURRENT_USER,  r"Software\Scriptware"),
    (winreg.HKEY_LOCAL_MACHINE, r"Software\Synapse X"),
    (winreg.HKEY_LOCAL_MACHINE, r"Software\KRNL"),
]

SUSPICIOUS_PROCESS_KEYWORDS = [
    "inject", "hook", "exploit", "cheat", "hack", "trainer",
    "loader", "bootstrapper", "executor",
]

# ── Scanner logic ─────────────────────────────────────────────────────────────

def expand(path):
    return os.path.expandvars(path)

def check_processes():
    hits = []
    try:
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=15
        )
        for line in result.stdout.splitlines():
            proc = line.strip().strip('"').split('","')[0].lower()
            for name in EXECUTOR_NAMES:
                if name in proc:
                    hits.append(f"Process: {proc}")
                    break
            else:
                for kw in SUSPICIOUS_PROCESS_KEYWORDS:
                    if kw in proc and "roblox" not in proc:
                        hits.append(f"Suspicious process: {proc}")
                        break
    except Exception as e:
        hits.append(f"[Warning] Could not scan processes: {e}")
    return hits

def check_paths():
    hits = []
    for raw in EXECUTOR_PATHS:
        path = expand(raw)
        if os.path.exists(path):
            hits.append(f"Folder/file found: {path}")
    return hits

def check_registry():
    hits = []
    for hive, key in EXECUTOR_REG_KEYS:
        try:
            winreg.OpenKey(hive, key)
            hits.append(f"Registry key found: {key}")
        except FileNotFoundError:
            pass
        except Exception as e:
            hits.append(f"[Warning] Registry error on {key}: {e}")
    return hits

def check_installed_programs():
    hits = []
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, reg_path in reg_paths:
        try:
            key = winreg.OpenKey(hive, reg_path)
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    sub = winreg.OpenKey(key, winreg.EnumKey(key, i))
                    try:
                        name, _ = winreg.QueryValueEx(sub, "DisplayName")
                        name_lower = name.lower()
                        for exe in EXECUTOR_NAMES:
                            if exe in name_lower:
                                hits.append(f"Installed program: {name}")
                                break
                    except FileNotFoundError:
                        pass
                except Exception:
                    pass
        except Exception:
            pass
    return hits

def run_scan():
    results = {
        "processes":  check_processes(),
        "paths":      check_paths(),
        "registry":   check_registry(),
        "installed":  check_installed_programs(),
    }
    return results

# ── GUI ───────────────────────────────────────────────────────────────────────

BG       = "#0f0f1a"
CARD     = "#1a1a2e"
ACCENT   = "#e94560"
GREEN    = "#00d084"
YELLOW   = "#f5a623"
TEXT     = "#e0e0f0"
SUBTEXT  = "#8888aa"
FONT     = "Segoe UI"

class ClanCheckApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clan PC Check  •  Anti-Cheat Scanner")
        self.geometry("720x560")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=CARD, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🛡  CLAN PC CHECK", font=(FONT, 18, "bold"),
                 fg=ACCENT, bg=CARD).pack()
        tk.Label(hdr, text="Roblox Executor & Cheat Scanner",
                 font=(FONT, 10), fg=SUBTEXT, bg=CARD).pack()

        # Status banner
        self.banner_var = tk.StringVar(value="Ready to scan.")
        self.banner_color = tk.StringVar(value=SUBTEXT)
        self.banner = tk.Label(self, textvariable=self.banner_var,
                               font=(FONT, 13, "bold"), fg=SUBTEXT, bg=BG, pady=10)
        self.banner.pack(fill="x")

        # Log box
        log_frame = tk.Frame(self, bg=BG, padx=18, pady=4)
        log_frame.pack(fill="both", expand=True)
        self.log = scrolledtext.ScrolledText(
            log_frame, font=("Consolas", 9), bg="#12121f", fg=TEXT,
            insertbackground=TEXT, relief="flat", bd=0, wrap="word",
            state="disabled", height=18
        )
        self.log.pack(fill="both", expand=True)

        # Tag colours
        self.log.tag_config("ok",    foreground=GREEN)
        self.log.tag_config("fail",  foreground=ACCENT)
        self.log.tag_config("warn",  foreground=YELLOW)
        self.log.tag_config("head",  foreground=SUBTEXT)
        self.log.tag_config("info",  foreground=TEXT)

        # Bottom bar
        bot = tk.Frame(self, bg=CARD, pady=10)
        bot.pack(fill="x", side="bottom")
        self.scan_btn = tk.Button(
            bot, text="▶  START SCAN", font=(FONT, 11, "bold"),
            bg=ACCENT, fg="white", activebackground="#c73652",
            activeforeground="white", relief="flat", padx=28, pady=8,
            cursor="hand2", command=self._start_scan
        )
        self.scan_btn.pack()

    def _log(self, text, tag="info"):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _set_banner(self, text, color):
        self.banner_var.set(text)
        self.banner.config(fg=color)

    def _start_scan(self):
        self.scan_btn.config(state="disabled")
        self._clear_log()
        self._set_banner("Scanning…", YELLOW)
        threading.Thread(target=self._do_scan, daemon=True).start()

    def _do_scan(self):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log(f"Scan started: {ts}\n", "head")

        sections = [
            ("Running Processes",    "processes"),
            ("Known Cheat Folders",  "paths"),
            ("Registry Keys",        "registry"),
            ("Installed Programs",   "installed"),
        ]

        results = run_scan()
        total_hits = 0

        for label, key in sections:
            self._log(f"── {label} ──────────────────────────", "head")
            hits = results[key]
            if hits:
                for h in hits:
                    self._log(f"  ✖  {h}", "fail")
                    total_hits += 1
            else:
                self._log("  ✔  Nothing detected", "ok")
            self._log("")

        self._log("─" * 56, "head")
        if total_hits == 0:
            self._log("  RESULT:  ✅  PASS — No cheats detected.", "ok")
            self.after(0, lambda: self._set_banner("✅  PASS — Clean system!", GREEN))
        else:
            self._log(f"  RESULT:  ❌  FAIL — {total_hits} issue(s) found.", "fail")
            self._log("  Member must remove flagged software before joining.", "warn")
            self.after(0, lambda: self._set_banner(
                f"❌  FAIL — {total_hits} issue(s) detected", ACCENT))

        self._log(f"\nScan complete: {datetime.datetime.now().strftime('%H:%M:%S')}", "head")
        self.after(0, lambda: self.scan_btn.config(state="normal"))


if __name__ == "__main__":
    app = ClanCheckApp()
    app.mainloop()
