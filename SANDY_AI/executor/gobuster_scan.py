"""SANDY AI – Gobuster Directory Scanner Executor"""
import subprocess
import shutil
import os


DEFAULT_WORDLIST = "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt"
DIRB_WORDLIST    = "/usr/share/dirb/wordlists/common.txt"


def get_wordlist() -> str:
    for wl in [DEFAULT_WORDLIST, DIRB_WORDLIST]:
        if os.path.exists(wl):
            return wl
    return DEFAULT_WORDLIST


def run_gobuster(target: str, wordlist: str = None, extensions: str = "php,html,txt") -> dict:
    if not shutil.which("gobuster"):
        # Try dirsearch as fallback
        if shutil.which("dirsearch"):
            return run_dirsearch(target, extensions)
        return {"success": False,
                "output": "❌ Gobuster not found. Install: sudo apt install gobuster -y",
                "tool": "gobuster"}

    if not target.startswith("http"):
        target = "http://" + target

    wl = wordlist or get_wordlist()
    command = ["gobuster", "dir", "-u", target, "-w", wl,
               "-x", extensions, "--no-error", "-q"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = result.stdout or result.stderr
        return {"success": True, "output": output, "tool": "gobuster", "target": target, "command": " ".join(command)}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "⏱️ Gobuster timed out.", "tool": "gobuster"}
    except Exception as e:
        return {"success": False, "output": f"Error: {e}", "tool": "gobuster"}


def run_dirsearch(target: str, extensions: str = "php,html,txt") -> dict:
    command = ["dirsearch", "-u", target, "-e", extensions, "--plain-text-report=/tmp/dirsearch_out.txt"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = result.stdout or result.stderr
        return {"success": True, "output": output, "tool": "dirsearch", "target": target}
    except Exception as e:
        return {"success": False, "output": f"Error: {e}", "tool": "dirsearch"}
