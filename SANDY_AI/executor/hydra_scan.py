"""SANDY AI – Hydra Brute Force Executor"""
import subprocess
import shutil
import os


DEFAULT_WORDLIST = "/usr/share/wordlists/rockyou.txt"
FALLBACK_WORDLIST = "/usr/share/wordlists/fasttrack.txt"


def get_wordlist() -> str:
    for wl in [DEFAULT_WORDLIST, FALLBACK_WORDLIST]:
        if os.path.exists(wl):
            return wl
    return DEFAULT_WORDLIST  # will error if missing – user must provide


def run_hydra(target: str, service: str = "ssh",
              username: str = "admin", wordlist: str = None) -> dict:
    if not shutil.which("hydra"):
        return {"success": False, "output": "❌ Hydra not found. Install: sudo apt install hydra -y", "tool": "hydra"}

    wl = wordlist or get_wordlist()
    if not os.path.exists(wl):
        return {"success": False,
                "output": f"❌ Wordlist not found: {wl}\nInstall: sudo gunzip /usr/share/wordlists/rockyou.txt.gz",
                "tool": "hydra"}

    command = ["hydra", "-l", username, "-P", wl,
               "-t", "4", "-f", f"{service}://{target}"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = result.stdout or result.stderr
        return {"success": True, "output": output, "tool": "hydra", "target": target, "command": " ".join(command)}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "⏱️ Hydra timed out.", "tool": "hydra"}
    except Exception as e:
        return {"success": False, "output": f"Error: {e}", "tool": "hydra"}
