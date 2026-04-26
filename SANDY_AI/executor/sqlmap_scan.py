"""SANDY AI – SQLMap Executor"""
import subprocess
import shutil


def run_sqlmap(url: str, level: int = 1, risk: int = 1) -> dict:
    if not shutil.which("sqlmap"):
        return {"success": False, "output": "❌ SQLMap not found. Install: sudo apt install sqlmap -y", "tool": "sqlmap"}

    command = ["sqlmap", "-u", url, "--batch",
               f"--level={level}", f"--risk={risk}",
               "--output-dir=/tmp/sqlmap_output"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = result.stdout or result.stderr
        return {"success": True, "output": output, "tool": "sqlmap", "target": url, "command": " ".join(command)}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "⏱️ SQLMap timed out.", "tool": "sqlmap"}
    except Exception as e:
        return {"success": False, "output": f"Error: {e}", "tool": "sqlmap"}
