import json

def get_stats(scan_file, bom_file):
    try:
        with open(bom_file) as f: b = json.load(f)
        total_pkgs = len(b.get("components", []))
    except: total_pkgs = 0

    try:
        with open(scan_file) as f: s = json.load(f)
        vulns = s.get("results", [{}])[0].get("packages", [])
        total_vulns = sum(len(p.get("vulnerabilities", [])) for p in vulns)
        vuln_pkgs = len(vulns)
    except:
        total_vulns, vuln_pkgs = 0, 0
    return total_pkgs, vuln_pkgs, total_vulns

p1, vp1, v1 = get_stats("scan_before.json", "bom_before.cdx.json")
p2, vp2, v2 = get_stats("scan_after.json", "bom_after.cdx.json")

print("\n=== ДАННЫЕ ДЛЯ ТВОЕГО ОТЧЕТА ===")
print(f"ДО ОБНОВЛЕНИЯ: Всего пакетов: {p1}, Уязвимых пакетов: {vp1}, Найдено уязвимостей: {v1}")
print(f"ПОСЛЕ ОБНОВЛЕНИЯ: Всего пакетов: {p2}, Уязвимых пакетов: {vp2}, Найдено уязвимостей: {v2}")
