import subprocess
import platform
import os
import socket
import ctypes
from datetime import datetime

IS_WIN = platform.system() == "Windows"


def run(cmd):
    try:
        return subprocess.check_output(
            cmd, shell=True, text=True, encoding="utf-8",
            errors="replace", stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "N/A"


def section(title):
    return f"\n{'=' * 60}\n{title}\n{'=' * 60}\n"


def is_admin():
    try:
        if IS_WIN:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        return os.geteuid() == 0
    except Exception:
        return False


def listening_ports():
    """Return list of (proto, bind_address, port)."""
    result = []
    if IS_WIN:
        for line in run("netstat -ano").splitlines():
            p = line.split()
            if len(p) >= 4 and p[0] in ("TCP", "UDP"):
                if p[0] == "TCP" and "LISTENING" not in p:
                    continue
                addr, _, port = p[1].rpartition(":")
                if port.isdigit():
                    result.append((p[0], addr, int(port)))
    else:
        for line in run("ss -tuln").splitlines()[1:]:
            p = line.split()
            if len(p) >= 5:
                addr, _, port = p[4].rpartition(":")
                if port.isdigit():
                    result.append((p[0].upper(), addr, int(port)))
    return result


def system_info():
    out = section("SYSTEM INFORMATION")
    out += f"Hostname     : {socket.gethostname()}\n"
    out += f"OS           : {platform.system()} {platform.release()} ({platform.version()})\n"
    out += f"Architecture : {platform.machine()}\n"
    out += f"Python       : {platform.python_version()}\n"
    if IS_WIN:
        out += f"Current User : {run('whoami')}\n"
    else:
        out += f"Uname        : {run('uname -a')}\n"
        out += f"Uptime       : {run('uptime -p')}\n"
        out += f"Current User : {os.getenv('USER')}\n"
    out += f"Admin/Root   : {is_admin()}\n"
    return out


def process_info():
    out = section("RUNNING PROCESSES (top 15)")
    if IS_WIN:
        lines = run("tasklist").splitlines()[:18]
    else:
        lines = run("ps aux --sort=-%cpu").splitlines()[:16]
    return out + "\n".join(lines) + "\n"


def network_info():
    out = section("LISTENING PORTS")
    out += f"{'PROTO':<6}{'ADDRESS':<25}{'PORT':<8}\n"
    for proto, addr, port in listening_ports():
        out += f"{proto:<6}{addr:<25}{port:<8}\n"
    return out


RISKY_PORTS = {
    21: "FTP (unencrypted)",
    23: "Telnet (unencrypted)",
    25: "SMTP",
    69: "TFTP",
    110: "POP3 (unencrypted)",
    135: "MS RPC",
    139: "NetBIOS",
    445: "SMB",
    1433: "MSSQL exposed",
    3306: "MySQL exposed",
    3389: "RDP",
    5900: "VNC",
}


def security_checks():
    out = section("SECURITY CHECKS")
    findings = []
    ports = listening_ports()

    for proto, addr, port in ports:
        if port in RISKY_PORTS:
            findings.append(f"[WARN] {proto} port {port} open on {addr} - {RISKY_PORTS[port]}")

    exposed = [x for x in ports if x[1] in ("0.0.0.0", "[::]", "*", "::")]
    if exposed:
        findings.append(f"[INFO] {len(exposed)} socket(s) listening on all interfaces")

    if is_admin():
        findings.append("[WARN] Script is running with admin/root privileges")

    if IS_WIN:
        fw = run("netsh advfirewall show allprofiles state")
        if "OFF" in fw.upper():
            findings.append("[WARN] Windows Firewall is OFF on at least one profile")

        guest = run("net user guest")
        if "Account active               Yes" in guest:
            findings.append("[WARN] Guest account is active")

        av = run("powershell -Command \"(Get-MpComputerStatus).RealTimeProtectionEnabled\"")
        if av.lower() == "false":
            findings.append("[WARN] Defender real-time protection is disabled")

        out += "Local users:\n" + run("net user") + "\n\n"
    else:
        ssh = run("grep -i '^PermitRootLogin' /etc/ssh/sshd_config")
        if "yes" in ssh.lower():
            findings.append("[WARN] SSH root login is enabled")

        shadow = run("stat -c '%a' /etc/shadow")
        if shadow not in ("N/A", "640", "600", "000", "0"):
            findings.append(f"[WARN] /etc/shadow permissions are {shadow}")

        uid0 = run("awk -F: '$3==0 {print $1}' /etc/passwd").split()
        if len(uid0) > 1:
            findings.append(f"[WARN] Multiple UID 0 accounts: {', '.join(uid0)}")

        empty = run("awk -F: '($2==\"\") {print $1}' /etc/shadow")
        if empty not in ("", "N/A"):
            findings.append(f"[CRIT] Accounts with empty password: {empty}")

        if "inactive" in run("ufw status").lower():
            findings.append("[WARN] UFW firewall is inactive")

        out += "Recent logins:\n" + run("last -n 5") + "\n\n"

    if findings:
        out += "Findings:\n" + "\n".join(f" - {f}" for f in findings) + "\n"
    else:
        out += "No major issues found.\n"
    return out


def main():
    report = f"SYSTEM & SECURITY REPORT - {datetime.now():%Y-%m-%d %H:%M:%S}\n"
    report += system_info()
    report += process_info()
    report += network_info()
    report += security_checks()

    print(report)

    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print("\nReport saved to report.txt")


if __name__ == "__main__":
    main()