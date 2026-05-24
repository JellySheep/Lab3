#!/usr/bin/env python3

import json
import os
import platform
import subprocess
from pathlib import Path


OUTPUT_FILE = "result_task_4.json"


def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return ""

        return result.stdout.strip()

    except Exception:
        return ""


# =========================
# OS INFORMATION
# =========================

def get_os_info():
    os_info = {}

    os_release = {}

    if Path("/etc/os-release").exists():
        with open("/etc/os-release") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    os_release[key] = value.strip('"')

    name = os_release.get("NAME", "Unknown")
    version = os_release.get("VERSION", "Unknown")
    version_id = os_release.get("VERSION_ID", "Unknown")
    distro_id = os_release.get("ID", "Unknown")
    codename = os_release.get("VERSION_CODENAME")

    description = os_release.get("PRETTY_NAME")

    if not description:
        description = f"{name} {version}"

    os_info["name"] = name
    os_info["version"] = version
    os_info["arch"] = platform.machine()
    os_info["id"] = distro_id
    os_info["version_id"] = version_id
    os_info["description"] = description

    if codename:
        os_info["codename"] = codename

    return os_info


# =========================
# PACKAGE MANAGER DETECTION
# =========================

def detect_package_manager():
    managers = {
        "dpkg": "dpkg-query",
        "rpm": "rpm",
        "pacman": "pacman",
        "apk": "apk"
    }

    for manager, binary in managers.items():
        if run_command(f"which {binary}"):
            return manager

    return None


# =========================
# DPKG (Debian/Ubuntu)
# =========================

def get_dpkg_packages():
    packages = []

    command = r'''dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\t${Installed-Size}\t${binary:Summary}\n' '''

    output = run_command(command)

    for line in output.splitlines():
        parts = line.split("\t")

        if len(parts) < 5:
            continue

        name, version, arch, size, description = parts

        package = {
            "name": name,
            "version": version,
            "arch": arch
        }

        if description:
            package["description"] = description.split(".")[0]

        if size.isdigit():
            package["size"] = int(size) * 1024

        packages.append(package)

    return packages


# =========================
# RPM (Fedora/CentOS/RHEL)
# =========================

def get_rpm_packages():
    packages = []

    command = r'''rpm -qa --qf '%{NAME}\t%{VERSION}-%{RELEASE}\t%{ARCH}\t%{SIZE}\t%{SUMMARY}\n' '''

    output = run_command(command)

    for line in output.splitlines():
        parts = line.split("\t")

        if len(parts) < 5:
            continue

        name, version, arch, size, description = parts

        package = {
            "name": name,
            "version": version,
            "arch": arch
        }

        if description:
            package["description"] = description.split(".")[0]

        if size.isdigit():
            package["size"] = int(size)

        packages.append(package)

    return packages


# =========================
# PACMAN (Arch)
# =========================

def get_pacman_packages():
    packages = []

    package_names = run_command("pacman -Qq").splitlines()

    for pkg in package_names:

        info = run_command(f"pacman -Qi {pkg}")

        package = {}

        for line in info.splitlines():

            if ":" not in line:
                continue

            key, value = line.split(":", 1)

            key = key.strip()
            value = value.strip()

            if key == "Name":
                package["name"] = value

            elif key == "Version":
                package["version"] = value

            elif key == "Architecture":
                package["arch"] = value

            elif key == "Description":
                package["description"] = value.split(".")[0]

            elif key == "Installed Size":
                package["size"] = value

        if package:
            packages.append(package)

    return packages


# =========================
# APK (Alpine)
# =========================

def get_apk_packages():
    packages = []

    package_names = run_command("apk info").splitlines()

    for pkg in package_names:

        info = run_command(f"apk info -s {pkg}")

        lines = info.splitlines()

        if not lines:
            continue

        package = {
            "name": pkg
        }

        for line in lines:

            if "description:" in line.lower():
                desc = line.split(":", 1)[1].strip()
                package["description"] = desc.split(".")[0]

            elif "installed size:" in line.lower():
                size = line.split(":", 1)[1].strip()
                package["size"] = size

        version_info = run_command(f"apk info -e {pkg}")

        if version_info:
            package["version"] = version_info

        packages.append(package)

    return packages


# =========================
# MAIN
# =========================

def main():

    result = {
        "OS": get_os_info(),
        "packages": []
    }

    manager = detect_package_manager()

    if manager == "dpkg":
        result["packages"] = get_dpkg_packages()

    elif manager == "rpm":
        result["packages"] = get_rpm_packages()

    elif manager == "pacman":
        result["packages"] = get_pacman_packages()

    elif manager == "apk":
        result["packages"] = get_apk_packages()

    else:
        print("Unsupported package manager")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"[+] Inventory saved to {OUTPUT_FILE}")
    print(f"[+] Packages found: {len(result['packages'])}")


if __name__ == "__main__":
    main()
