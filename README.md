# SANDY_AI-version3.0
# 🔐 SANDY AI – Cybersecurity Automation Assistant

SANDY AI is an AI-powered cybersecurity automation assistant built for ethical hacking and security testing labs.

It converts natural language or voice commands into real security scans using popular penetration testing tools.

⚠️ **This project is made for educational purposes and authorized security testing only.**

---

## ✨ Features

* 🧠 AI-based task mapping
  Converts commands like:

  * “Scan my network for open ports”
  * “Check website vulnerabilities”
  * “Test SQL Injection”

  into real tool executions.

* 🎤 Voice command support

* ⚡ Quick scan buttons

* 📊 PDF / JSON report generation

* 🔍 Integrated tools:

  * Nmap
  * Nikto
  * SQLMap
  * Hydra
  * Gobuster

---

# 📂 Project Structure

```bash
SANDY_AI/
├── app.py
├── ai_engine.py
├── task_mapper.py
├── requirements.txt
├── README.md
├── executor/
│   ├── __init__.py
│   ├── nmap_scan.py
│   ├── nikto_scan.py
│   ├── sqlmap_scan.py
│   ├── hydra_scan.py
│   └── gobuster_scan.py
├── analyzer/
│   ├── __init__.py
│   └── analyzer.py
├── reports/
│   ├── __init__.py
│   ├── report_generator.py
│   └── output/
└── voice/
    ├── __init__.py
    └── voice_input.py
```

---

# 🖥️ Supported OS

✅ Linux only

Recommended:

* Kali Linux
* Parrot OS
* Ubuntu

❌ Windows not supported
❌ macOS not tested

---

# ⚙️ Installation

## 1 Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/SANDY_AI.git
cd SANDY_AI
```

## 2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 3 Install Required Linux Packages

```bash
sudo apt update
sudo apt install nmap nikto sqlmap hydra gobuster portaudio19-dev -y
pip install pyaudio
```

---

# 🚀 Run Project

```bash
streamlit run app.py
```

Open browser:

```bash
http://localhost:8501
```

---

# 🎮 Usage

### Example Commands

```bash
Scan my network for open ports
```

```bash
Scan website for vulnerabilities
```

```bash
Test SQL injection
```

---

# 🧪 Legal Practice Targets

* 127.0.0.1
* 192.168.1.0/24
* http://testphp.vulnweb.com
* HackTheBox Labs
* TryHackMe Labs

---

# 📄 Report Export

Generated reports are saved in:

```bash
reports/output/
```

Formats:

* PDF
* JSON

---

# ⚠️ Disclaimer

This tool is for:

* educational use
* lab testing
* authorized penetration testing only

The developer is not responsible for misuse.

---

# 👨‍💻 Author

Durgesh Pandey
Cybersecurity Student / Ethical Hacker

```
```
