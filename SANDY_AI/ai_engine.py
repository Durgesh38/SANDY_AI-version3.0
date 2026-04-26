"""
SANDY AI - AI Engine / NLP Layer
Converts natural language input → structured action JSON
"""

import re

INTENT_PATTERNS = {
    "network_scan": [
        "scan network", "open ports", "port scan", "host discovery",
        "find devices", "discover hosts", "scan ip", "network enumeration",
        "nmap", "scan my network", "check ports"
    ],
    "web_scan": [
        "scan website", "web vulnerability", "web scan", "nikto",
        "check website", "web server", "http scan", "website security"
    ],
    "sql_injection": [
        "sql injection", "sqlmap", "database vulnerability", "inject",
        "sql vuln", "test sql", "sqli"
    ],
    "brute_force": [
        "brute force", "hydra", "crack password", "login attack",
        "password attack", "dictionary attack", "wordlist"
    ],
    "dir_scan": [
        "directory scan", "gobuster", "dirsearch", "find directories",
        "hidden paths", "dir brute", "endpoint scan", "file enumeration"
    ],
    "vuln_scan": [
        "vulnerability scan", "openvas", "full scan", "cve",
        "security audit", "complete scan", "assess"
    ],
    "help": [
        "help", "what can you do", "commands", "features",
        "how to use", "guide", "options"
    ],
    "report": [
        "generate report", "create report", "show report",
        "export", "pdf report", "summary"
    ],
    "clear": ["clear", "reset", "new session", "start over"]
}

def extract_target(text):
    ip_cidr   = re.search(r'\b(\d{1,3}(?:\.\d{1,3}){3}(?:/\d{1,2})?)\b', text)
    url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+)', text)
    domain    = re.search(r'\b([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)\b', text)
    if ip_cidr:   return ip_cidr.group(1)
    if url_match: return url_match.group(1)
    if domain:    return domain.group(1)
    return None

def interpret_command(user_input):
    text = user_input.lower().strip()
    detected_action = "unknown"
    for action, keywords in INTENT_PATTERNS.items():
        if any(kw in text for kw in keywords):
            detected_action = action
            break
    target = extract_target(user_input)
    return {
        "action":    detected_action,
        "target":    target,
        "raw_input": user_input,
    }

HELP_TEXT = """
╔══════════════════════════════════════════════════════╗
║              SANDY AI — COMMAND GUIDE               ║
╠══════════════════════════════════════════════════════╣
║  🌐 Network Scan   → "Scan network for open ports"  ║
║  🌍 Web Scan       → "Scan website vulnerabilities" ║
║  💉 SQL Injection  → "Test SQL injection on URL"    ║
║  🔐 Brute Force    → "Brute force SSH login"        ║
║  📁 Dir Scan       → "Find hidden directories"      ║
║  🔍 Vuln Scan      → "Full vulnerability scan"      ║
║  📄 Report         → "Generate report"              ║
║  ❓ Help           → "Help" / "What can you do?"    ║
╚══════════════════════════════════════════════════════╝
⚠️  Use ONLY on authorized systems you own or have
    explicit written permission to test.
"""
