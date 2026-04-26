"""
SANDY AI - Nmap Executor
Network scanning & enumeration
"""
import subprocess, shutil, datetime

def check_nmap():
    return shutil.which("nmap") is not None

def run_nmap(target: str, scan_type: str = "standard") -> dict:
    if not check_nmap():
        return {"success": False, "output": "❌ Nmap not installed. Run: apt install nmap -y", "tool": "nmap"}

    profiles = {
        "quick":    ["nmap", "-T4", "-F", target],
        "standard": ["nmap", "-A", "-T4", target],
        "stealth":  ["nmap", "-sS", "-T2", target],
        "full":     ["nmap", "-A", "-p-", "-T4", target],
        "vuln":     ["nmap", "--script=vuln", "-T4", target],
    }
    command = profiles.get(scan_type, profiles["standard"])

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=300
        )
        return {
            "success":   True,
            "output":    result.stdout or result.stderr,
            "tool":      "nmap",
            "command":   " ".join(command),
            "target":    target,
            "timestamp": datetime.datetime.now().isoformat(),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "⏱️ Scan timed out (5 min limit)", "tool": "nmap"}
    except Exception as e:
        return {"success": False, "output": f"❌ Error: {str(e)}", "tool": "nmap"}
