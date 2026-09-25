import platform
import socket
import getpass
import psutil
from datetime import datetime


def system_information():
    print("\n===== SYSTEM INFORMATION =====")

    print("Operating System :", platform.system())
    print("Hostname         :", socket.gethostname())
    print("Kernel Version   :", platform.release())
    print("Architecture     :", platform.machine())
    print("Username         :", getpass.getuser())
    print("Processor        :", platform.processor())


def running_processes():
    print("\n===== RUNNING PROCESSES =====")

    print(f"{'PID':<10}{'PROCESS NAME'}")
    print("-" * 40)

    for process in psutil.process_iter(['pid', 'name']):
        try:
            print(f"{process.info['pid']:<10}{process.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def network_information():
    print("\n===== NETWORK INFORMATION =====")

    hostname = socket.gethostname()

    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = "Unable to determine"

    print("Hostname   :", hostname)
    print("IP Address :", ip_address)

    print("\nNetwork Interfaces:")

    interfaces = psutil.net_if_addrs()

    for interface, addresses in interfaces.items():
        print("\n", interface)

        for address in addresses:
            print("  Address:", address.address)


def security_report():
    print("\n===== SECURITY REPORT =====")

    print("Report generated:",
          datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    print("\n--- SYSTEM INFORMATION ---")
    print("Operating System :", platform.system())
    print("Hostname         :", socket.gethostname())
    print("Kernel Version   :", platform.release())
    print("Architecture     :", platform.machine())
    print("Username         :", getpass.getuser())

    print("\n--- NETWORK INFORMATION ---")

    try:
        print("IP Address :", socket.gethostbyname(socket.gethostname()))
    except socket.gaierror:
        print("IP Address : Unable to determine")

    print("\n--- RUNNING PROCESS COUNT ---")

    processes = list(psutil.process_iter())

    print("Running Processes:", len(processes))

    print("\nSecurity report completed.")


def main():

    while True:

        print("\n===== SYSTEM SECURITY TOOL =====")
        print("1. System Information")
        print("2. Running Processes")
        print("3. Network Information")
        print("4. Generate Full Security Report")
        print("5. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            system_information()

        elif choice == "2":
            running_processes()

        elif choice == "3":
            network_information()

        elif choice == "4":
            security_report()

        elif choice == "5":
            print("\nExiting program...")
            break

        else:
            print("\nInvalid choice. Please try again.")


main()