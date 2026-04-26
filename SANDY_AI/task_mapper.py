"""
SANDY AI - Task Mapper
Maps detected intent → tool name + config
"""

TOOL_MAP = {
    "network_scan":  {"tool": "nmap",      "phase": 1, "icon": "🌐"},
    "web_scan":      {"tool": "nikto",     "phase": 1, "icon": "🌍"},
    "sql_injection": {"tool": "sqlmap",    "phase": 2, "icon": "💉"},
    "brute_force":   {"tool": "hydra",     "phase": 2, "icon": "🔐"},
    "dir_scan":      {"tool": "gobuster",  "phase": 2, "icon": "📁"},
    "vuln_scan":     {"tool": "openvas",   "phase": 3, "icon": "🔍"},
    "help":          {"tool": "help",      "phase": 0, "icon": "❓"},
    "report":        {"tool": "report",    "phase": 0, "icon": "📄"},
    "clear":         {"tool": "clear",     "phase": 0, "icon": "🔄"},
}

def map_task(intent: dict) -> dict:
    action = intent.get("action", "unknown")
    info   = TOOL_MAP.get(action, {"tool": "unknown", "phase": 0, "icon": "❓"})
    return {
        **info,
        "action": action,
        "target": intent.get("target"),
    }

def get_tool_description(tool: str) -> str:
    descriptions = {
        "nmap":     "Network mapper — discovers hosts, open ports, services & OS fingerprinting",
        "nikto":    "Web server scanner — checks for dangerous files, misconfigs & CVEs",
        "sqlmap":   "Automated SQL injection detection & database extraction tool",
        "hydra":    "Parallel network login cracker — tests authentication services",
        "gobuster": "Directory & DNS brute-forcing tool written in Go",
        "openvas":  "Full-featured vulnerability scanner by Greenbone Networks",
    }
    return descriptions.get(tool, "Security testing tool")
