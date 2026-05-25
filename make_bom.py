import json
import subprocess
import uuid
import sys

if len(sys.argv) < 2:
    print("Ошибка! Укажите имя файла. Пример: python3 make_bom.py bom_before.cdx.json")
    sys.exit(1)

output_filename = sys.argv[1]

cmd = ['dpkg-query', '-W', '-f=${Package}|${Version}|${Architecture}\n']
output = subprocess.check_output(cmd, text=True)
components = []

for line in output.splitlines():
    if not line.strip():
        continue
    parts = line.split('|')
    if len(parts) == 3:
        name, version, arch = parts[0], parts[1], parts[2]
        components.append({
            "type": "application",
            "name": name,
            "version": version,
            "purl": f"pkg:deb/debian/{name}@{version}?arch={arch}"
        })

bom = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.4",
    "serialNumber": f"urn:uuid:{uuid.uuid4()}",
    "version": 1,
    "components": components
}

with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(bom, f, indent=4, ensure_ascii=False)
print(f"[+] SBOM файл успешно сохранен: {output_filename}")
