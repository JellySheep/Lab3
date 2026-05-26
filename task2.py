import json
import urllib.request
import urllib.error
import os
import re
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

if not GITHUB_TOKEN:
    print("Ошибка: GITHUB_TOKEN не найден в .env!")
    exit(1)
URL = 'https://api.github.com/graphql'
HEADERS = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Content-Type': 'application/json',
}

# GraphQL запрос к GHSA
QUERY = """
query($package: String!, $ecosystem: SecurityAdvisoryEcosystem!) {
  securityVulnerabilities(ecosystem: $ecosystem, package: $package, first: 100) {
    nodes {
      advisory {
        ghsaId
      }
      severity
      vulnerableVersionRange
      firstPatchedVersion {
        identifier
      }
    }
  }
}
"""

def parse_version(v_str):
    """Парсит строку версии в кортеж чисел для корректного сравнения."""
    # Удаленик лишних префиксов, если они есть
    v_str = re.sub(r'^[vV= ]+', '', v_str).strip()
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)', v_str)
    if match:
        return tuple(map(int, match.groups()))
 
    parts = [int(p) for p in re.findall(r'\d+', v_str)[:3]]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)

def match_range(version_str, range_str):
    """Проверяет, входит ли текущая версия пакета в диапазон уязвимых версий GHSA."""
    if not range_str or range_str == '*':
        return True
    
    current_v = parse_version(version_str)
    # Разбивает сложные диапазоны (например, ">= 1.0.0, < 2.0.0")
    clauses = [c.strip() for c in range_str.split(',')]
    
    for clause in clauses:
        match = re.match(r'^(>=|<=|>|<|=)?\s*(.*)$', clause)
        if not match:
            continue
        op, v_part = match.groups()
        if not op:
            op = '='
        
        clause_v = parse_version(v_part)
        
        if op == '=' and current_v != clause_v: return False
        elif op == '>' and current_v <= clause_v: return False
        elif op == '>=' and current_v < clause_v: return False
        elif op == '<' and current_v >= clause_v: return False
        elif op == '<=' and current_v > clause_v: return False
        
    return True

def fetch_vulns_for_package(pkg):
    """Делает сетевой запрос к GitHub API для одного пакета."""
    name = pkg['name']
    version = pkg['version']
    ecosystem = pkg['ecosystem']
    
    variables = {
        "package": name,
        "ecosystem": ecosystem.upper()
    }
    
    data = json.dumps({'query': QUERY, 'variables': variables}).encode('utf-8')
    req = urllib.request.Request(URL, data=data, headers=HEADERS)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            nodes = res_json.get('data', {}).get('securityVulnerabilities', {}).get('nodes', [])
            
            vulnerabilities_list = []
            secure_versions = set()
            
            for v in nodes:
                range_str = v.get('vulnerableVersionRange', '')
                
                # Фильтр: применима ли уязвимость к НАШЕЙ версии
                if not match_range(version, range_str):
                    continue
                    
                first_patched = v.get('firstPatchedVersion')
                patched_version = first_patched.get('identifier') if first_patched else "None"
                
                if patched_version != "None":
                    secure_versions.add(patched_version)
                
                vulnerabilities_list.append({
                    "name": v['advisory']['ghsaId'],
                    "severity": v['severity'],
                    "vulnerable_range": range_str,
                    "first_patched_version": patched_version
                })
            
            if vulnerabilities_list:
                # Находит безопасную версию из списка исправленных
                try:
                    secure_version = max(secure_versions, key=parse_version)
                except ValueError:
                    secure_version = "No secure version known"
                    
                return {
                    "name": name,
                    "version": version,
                    "ecosystem": ecosystem,
                    "url": pkg['url'],
                    "purl": pkg['purl'],
                    "vulnerabilities": vulnerabilities_list,
                    "secure_version": secure_version
                }
    except Exception as e:
        print(f"[-] Ошибка при обработке {name}: {e}")
        
    return None

def main():
    try:
        with open('result_task_1.json', 'r', encoding='utf-8') as f:
            packages = json.load(f)
    except FileNotFoundError:
        print("Файл result_task_1.json не найден!")
        return

    print(f"[+] Запуск сканирования ({len(packages)} пакетов)...")
    result_task_2 = []

    # Запуск пул из 4 параллельных рабочих потоков
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Получает результаты по мере их готовности
        futures = executor.map(fetch_vulns_for_package, packages)
        
        for index, res in enumerate(futures, 1):
            pkg_data = packages[index-1]
            print(f"[{index}/{len(packages)}] Обработан: {pkg_data['name']}@{pkg_data['version']}")
            if res:
                print(f"    --> НАЙДЕНЫ УЯЗВИМОСТИ: {len(res['vulnerabilities'])}")
                result_task_2.append(res)

    with open('result_task_2.json', 'w', encoding='utf-8') as f:
        json.dump(result_task_2, f, indent=4)

    print(f"\n[+] Сканирование завершено.")
    print(f"[+] Всего уязвимых зависимостей: {len(result_task_2)}")

if __name__ == '__main__':
    main()
