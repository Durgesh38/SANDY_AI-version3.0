# 🔐 SANDY AI — Web-Based Security Intelligence System

## 🚀 Quick Start

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install security tools (Kali Linux)
apt install nmap nikto sqlmap hydra gobuster -y

# 3. Launch the web server
python server.py

# 4. Open your browser
http://localhost:8000
```

## 📁 Structure

```
SANDY_AI/
├── server.py                   ← FastAPI web server (start here)
├── ai_engine.py                ← NLP command interpreter
├── task_mapper.py              ← Tool routing
├── requirements.txt
├── static/
│   └── index.html              ← Full web UI (single file)
├── executor/
│   ├── nmap_scan.py
│   ├── nikto_scan.py
│   ├── sqlmap_scan.py
│   ├── hydra_scan.py
│   └── gobuster_scan.py
├── analyzer/
│   └── analyzer.py
├── reports/
│   ├── report_generator.py
│   └── output/
└── voice/
    └── voice_input.py
```

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web dashboard |
| WS | `/ws/scan` | Real-time scan streaming |
| POST | `/api/interpret` | Parse command |
| GET | `/api/history` | Get scan history |
| DELETE | `/api/history` | Clear history |
| GET | `/api/stats` | Session statistics |
| POST | `/api/report/json` | Generate JSON report |
| POST | `/api/report/pdf` | Generate PDF report |

## 🎤 Voice Input
Uses the **Web Speech API** (built into Chrome/Edge). No extra setup needed!
Just click the 🎤 VOICE button and speak your command.

## ⚠️ Legal
For authorized use only. Only test systems you own or have explicit written permission to test.
