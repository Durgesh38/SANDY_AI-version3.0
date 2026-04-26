"""
SANDY AI — FastAPI Web Server
Serves the frontend + handles all scan API calls via REST + WebSocket
Run: uvicorn server:app --host 0.0.0.0 --port 8000 --reload
"""

import sys, os, json, datetime, asyncio, subprocess, threading, queue
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from ai_engine  import interpret_command, HELP_TEXT
from task_mapper import map_task, get_tool_description
from analyzer.analyzer import analyze_output

app = FastAPI(title="SANDY AI", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# ── Serve static frontend ─────────────────────────────────────────
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ── In-memory scan history ────────────────────────────────────────
scan_history: list = []

# ═════════════════════════════════════════════════════════════════
#  REQUEST MODELS
# ═════════════════════════════════════════════════════════════════
class CommandRequest(BaseModel):
    command: str
    target: Optional[str] = ""
    scan_profile: Optional[str] = "standard"
    ssh_user:     Optional[str] = "admin"
    wordlist:     Optional[str] = "/usr/share/wordlists/rockyou.txt"
    gobuster_wl:  Optional[str] = "/usr/share/wordlists/dirb/common.txt"

class InterpretRequest(BaseModel):
    command: str

# ═════════════════════════════════════════════════════════════════
#  REST ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.post("/api/interpret")
async def api_interpret(req: InterpretRequest):
    intent = interpret_command(req.command)
    task   = map_task(intent)
    return {"intent": intent, "task": task, "help": HELP_TEXT}

@app.get("/api/history")
async def api_history():
    return scan_history

@app.delete("/api/history")
async def api_clear_history():
    scan_history.clear()
    return {"status": "cleared"}

@app.post("/api/report/json")
async def api_report_json():
    if not scan_history:
        raise HTTPException(400, "No scans to report")
    from reports.report_generator import generate_json_report
    path = generate_json_report(scan_history, output_dir="reports/output")
    return {"path": path, "status": "generated"}

@app.post("/api/report/pdf")
async def api_report_pdf():
    if not scan_history:
        raise HTTPException(400, "No scans to report")
    from reports.report_generator import generate_pdf_report
    path = generate_pdf_report(scan_history, output_dir="reports/output")
    if path.startswith("PDF generation requires"):
        raise HTTPException(500, path)
    return {"path": path, "status": "generated"}

@app.get("/api/download/report")
async def api_download_report(path: str):
    if os.path.exists(path):
        return FileResponse(path, filename=os.path.basename(path))
    raise HTTPException(404, "Report not found")

@app.get("/api/stats")
async def api_stats():
    total    = len(scan_history)
    risk_map = {}
    tool_map = {}
    for s in scan_history:
        r = s.get("analysis", {}).get("overall_risk", "UNKNOWN")
        t = s.get("tool", "unknown")
        risk_map[r] = risk_map.get(r, 0) + 1
        tool_map[t] = tool_map.get(t, 0) + 1
    return {
        "total":      total,
        "risk_dist":  risk_map,
        "tool_dist":  tool_map,
        "critical":   risk_map.get("CRITICAL", 0),
        "high":       risk_map.get("HIGH", 0),
    }

# ═════════════════════════════════════════════════════════════════
#  WEBSOCKET — Real-time scan streaming
# ═════════════════════════════════════════════════════════════════

async def stream_subprocess(ws: WebSocket, command: list, tool: str, target: str,
                             scan_profile: str = "standard"):
    """Run a subprocess and stream its output line-by-line over WebSocket."""
    await ws.send_json({"type": "status", "msg": f"Launching {tool.upper()}...",  "pct": 5})
    await ws.send_json({"type": "cmd",    "msg": "$ " + " ".join(command)})

    try:
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        full_output = []
        pct = 10
        async for line in proc.stdout:
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                full_output.append(text)
                pct = min(pct + 1, 88)
                await ws.send_json({"type": "line", "msg": text, "pct": pct})

        await proc.wait()
        raw = "\n".join(full_output)

        await ws.send_json({"type": "status", "msg": "Analyzing results...", "pct": 92})
        analysis = analyze_output(raw, tool=tool)

        record = {
            "tool":      tool,
            "target":    target,
            "timestamp": datetime.datetime.now().isoformat(),
            "raw":       raw,
            "analysis":  analysis,
            "command":   " ".join(command),
        }
        scan_history.insert(0, record)
        if len(scan_history) > 50:
            scan_history.pop()

        await ws.send_json({"type": "done", "pct": 100, "analysis": analysis,
                             "record": record})

    except FileNotFoundError:
        await ws.send_json({"type": "error",
                             "msg": f"'{tool}' not found. Install: apt install {tool} -y"})
    except Exception as e:
        await ws.send_json({"type": "error", "msg": str(e)})


@app.websocket("/ws/scan")
async def websocket_scan(ws: WebSocket):
    await ws.accept()
    try:
        data = await ws.receive_json()
        command_text  = data.get("command", "")
        target        = data.get("target", "")
        scan_profile  = data.get("scan_profile", "standard")
        ssh_user      = data.get("ssh_user", "admin")
        wordlist      = data.get("wordlist", "/usr/share/wordlists/rockyou.txt")
        gobuster_wl   = data.get("gobuster_wl", "/usr/share/wordlists/dirb/common.txt")

        intent = interpret_command(command_text)
        task   = map_task(intent)
        tool   = task["tool"]
        action = task["action"]

        effective_target = target or intent.get("target", "")

        if action == "help":
            await ws.send_json({"type": "help", "msg": HELP_TEXT})
            return
        if action == "clear":
            scan_history.clear()
            await ws.send_json({"type": "cleared"})
            return
        if action == "unknown":
            await ws.send_json({"type": "unknown",
                                 "msg": "Command not recognized. Try: 'scan network', 'scan website', etc."})
            return
        if not effective_target:
            await ws.send_json({"type": "error", "msg": "No target detected. Please enter a target."})
            return

        await ws.send_json({"type": "intent", "action": action, "tool": tool,
                             "target": effective_target})

        # ── Build command per tool ──────────────────────────────────
        if tool == "nmap":
            profiles = {
                "quick":    ["nmap", "-T4", "-F", effective_target],
                "standard": ["nmap", "-A", "-T4", effective_target],
                "stealth":  ["nmap", "-sS", "-T2", effective_target],
                "full":     ["nmap", "-A", "-p-", "-T4", effective_target],
                "vuln":     ["nmap", "--script=vuln", "-T4", effective_target],
            }
            cmd = profiles.get(scan_profile, profiles["standard"])

        elif tool == "nikto":
            tgt = effective_target if effective_target.startswith("http") else "http://" + effective_target
            cmd = ["nikto", "-h", tgt]

        elif tool == "sqlmap":
            tgt = effective_target if effective_target.startswith("http") else "http://" + effective_target
            cmd = ["sqlmap", "-u", tgt, "--batch", "--level=2", "--risk=1"]

        elif tool == "hydra":
            cmd = ["hydra", "-l", ssh_user, "-P", wordlist,
                   effective_target, "ssh", "-t", "4", "-V"]

        elif tool == "gobuster":
            tgt = effective_target if effective_target.startswith("http") else "http://" + effective_target
            cmd = ["gobuster", "dir", "-u", tgt, "-w", gobuster_wl, "-t", "20", "-q"]

        else:
            await ws.send_json({"type": "error",
                                 "msg": f"Tool '{tool}' is Phase 3 — not yet integrated."})
            return

        await stream_subprocess(ws, cmd, tool, effective_target, scan_profile)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "msg": str(e)})
        except:
            pass

# ── Run directly ──────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
