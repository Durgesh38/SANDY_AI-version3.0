"""SANDY AI – Nikto Web Scanner Executor"""
import subprocess
import shutil


def run_nikto(target: str, ssl: bool = False) -> dict:
    if not shutil.which("nikto"):
        return {"success": False, "output": "❌ Nikto not found. Install: sudo apt install nikto -y", "tool": "nikto"}

    if not target.startswith("http"):
        target = ("https://" if ssl else "http://") + target

    command = ["nikto", "-h", target, "-nointeractive"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = result.stdout or result.stderr
        return {"success": True, "output": output, "tool": "nikto", "target": target, "command": " ".join(command)}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "⏱️ Nikto scan timed out.", "tool": "nikto"}
    except Exception as e:
        return {"success": False, "output": f"Error: {e}", "tool": "nikto"}
