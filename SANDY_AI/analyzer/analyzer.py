"""
SANDY AI – Result Analyzer
Parses raw tool output into structured risk assessments.
"""

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class Finding:
    severity: str
    title: str
    detail: str
    fix: str = ""

    def emoji(self):
        return {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡",
                "LOW": "🟢", "INFO": "🔵"}.get(self.severity, "⚪")


@dataclass
class AnalysisResult:
    tool: str
    target: str
    findings: List[Finding] = field(default_factory=list)
    risk_score: int = 0
    summary: str = ""
    chain_suggestions: List[str] = field(default_factory=list)

    def risk_label(self):
        if self.risk_score >= 80: return "CRITICAL"
        if self.risk_score >= 60: return "HIGH"
        if self.risk_score >= 40: return "MEDIUM"
        if self.risk_score >= 20: return "LOW"
        return "MINIMAL"

    def risk_color(self):
        return {"CRITICAL": "#ff2244", "HIGH": "#ff6600",
                "MEDIUM": "#ffcc00", "LOW": "#44ff88", "MINIMAL": "#00ccff"
                }.get(self.risk_label(), "#aaaaaa")


def analyze_nmap(output: str, target: str = "") -> AnalysisResult:
    result = AnalysisResult(tool="nmap", target=target)
    findings = []
    risk = 0
    open_ports = re.findall(r'(\d+/\w+)\s+open\s+(\S+)(?:\s+(.+))?', output)
    for port_proto, service, version in open_ports:
        port_num = int(port_proto.split("/")[0])
        version = (version or "").strip()
        sev, fix = "LOW", "Review if this service needs to be publicly exposed."
        if port_num in [21, 23, 139, 445, 3389]:
            sev, risk = "HIGH", risk + 20
            fix = "High-risk service. Apply firewall rules or disable."
        elif port_num in [80, 443, 8080, 8443]:
            sev, risk = "MEDIUM", risk + 10
            fix = "Web service found. Run Nikto for web vulnerability scan."
            if "nikto" not in result.chain_suggestions:
                result.chain_suggestions.append("nikto")
        elif port_num == 22:
            sev, risk = "MEDIUM", risk + 10
            fix = "SSH exposed. Use key-based auth, disable root login."
            result.chain_suggestions.append("hydra")
        elif port_num == 3306:
            sev, risk = "HIGH", risk + 20
            fix = "MySQL exposed publicly! Should be firewalled."
            result.chain_suggestions.append("sqlmap")
        else:
            risk += 5
        findings.append(Finding(severity=sev,
                                title=f"Open Port: {port_proto} ({service})",
                                detail=version or f"{service} service", fix=fix))

    os_match = re.search(r'OS details?: (.+)', output)
    if os_match:
        findings.append(Finding(severity="INFO", title=f"OS: {os_match.group(1).strip()}",
                                detail="OS fingerprint detected", fix="Keep OS patched."))

    if "VULNERABLE" in output.upper():
        risk += 30
        findings.append(Finding(severity="CRITICAL", title="NSE Vulnerability Detected",
                                detail="Nmap script detected a vulnerability.",
                                fix="Apply patches immediately."))

    if not open_ports:
        findings.append(Finding(severity="INFO", title="No Open Ports",
                                detail="Host appears closed or filtered."))

    result.findings = findings
    result.risk_score = min(risk, 100)
    result.summary = f"Found {len(open_ports)} open port(s). Risk: {result.risk_label()}."
    return result


def analyze_nikto(output: str, target: str = "") -> AnalysisResult:
    result = AnalysisResult(tool="nikto", target=target)
    findings, risk = [], 0
    patterns = [
        (r'OSVDB-\d+:? (.+)',            "HIGH",     "Patch or update web server."),
        (r'CVE-\d{4}-\d+:? (.+)',        "CRITICAL", "Critical CVE – patch immediately."),
        (r'X-Frame-Options.*not set',    "MEDIUM",   "Set X-Frame-Options: DENY"),
        (r'X-XSS-Protection.*not set',  "MEDIUM",   "Enable X-XSS-Protection header."),
        (r'Allowed HTTP Methods: (.+)',  "MEDIUM",   "Disable unnecessary HTTP methods."),
        (r'Default account.+?: (.+)',    "HIGH",     "Change default credentials."),
        (r'SQL injection (.+)',          "CRITICAL", "Use parameterized queries."),
        (r'Directory indexing',          "MEDIUM",   "Disable directory listing."),
    ]
    for pattern, sev, fix in patterns:
        for match in re.finditer(pattern, output, re.IGNORECASE):
            detail = match.group(1) if match.lastindex else match.group(0)
            risk += {"CRITICAL":35,"HIGH":25,"MEDIUM":15,"LOW":5,"INFO":0}.get(sev,0)
            findings.append(Finding(severity=sev, title=f"Web: {sev}",
                                    detail=detail.strip(), fix=fix))
    if not findings:
        findings.append(Finding(severity="INFO", title="Scan Complete",
                                detail="No critical issues detected.", fix="Keep monitoring."))
    result.findings, result.risk_score = findings, min(risk, 100)
    result.summary = f"Web scan done. {len([f for f in findings if f.severity != 'INFO'])} issues found."
    return result


def analyze_sqlmap(output: str, target: str = "") -> AnalysisResult:
    result = AnalysisResult(tool="sqlmap", target=target)
    findings, risk = [], 0
    if re.search(r'is vulnerable|injectable|injection found', output, re.IGNORECASE):
        risk = 90
        db = (re.search(r'back-end DBMS:\s*(\S+)', output, re.IGNORECASE) or type('x', (), {'group': lambda s,i: 'Unknown'})()).group(1)
        findings.append(Finding(severity="CRITICAL", title=f"SQL Injection Found (DB: {db})",
                                detail="Target is vulnerable to SQL injection.",
                                fix="Use prepared statements. Sanitize all inputs."))
    else:
        findings.append(Finding(severity="INFO", title="No SQLi Found",
                                detail="Basic SQL injection tests passed.", fix="Try higher level/risk."))
    result.findings, result.risk_score = findings, risk
    result.summary = f"SQL test complete. Risk: {result.risk_label()}."
    return result


def analyze_hydra(output: str, target: str = "") -> AnalysisResult:
    result = AnalysisResult(tool="hydra", target=target)
    creds = re.findall(r'login:\s*(\S+)\s+password:\s*(\S+)', output, re.IGNORECASE)
    if creds:
        findings = [Finding(severity="CRITICAL", title=f"Credentials Found: {u}:{p}",
                            detail=f"Valid login: {u} / {p}",
                            fix="Change password immediately. Enable lockout policy.")
                    for u, p in creds]
        result.risk_score = 95
    else:
        findings = [Finding(severity="INFO", title="No Creds Found",
                            detail="Brute force completed without success.",
                            fix="Maintain strong password policy.")]
    result.findings = findings
    result.summary = f"Brute force done. {len(creds)} credential(s) found."
    return result


def analyze_output(tool: str, output: str, target: str = "") -> AnalysisResult:
    return {"nmap": analyze_nmap, "nmap_os": analyze_nmap,
            "nikto": analyze_nikto, "sqlmap": analyze_sqlmap,
            "hydra": analyze_hydra}.get(tool,
        lambda o, t: AnalysisResult(tool=tool, target=t,
            findings=[Finding(severity="INFO", title="Output", detail=o[:500])],
            summary="Analysis complete."))(output, target)
