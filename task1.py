import json
import os

result = []
ecosystem = 'npm'
seen = set()

# Проход по всем директориям, игнорируя node_modules
for root, dirs, files in os.walk('.'):
    if 'node_modules' in root:
        continue
    if 'package.json' in files:
        filepath = os.path.join(root, 'package.json')
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Сбор dependencies и devDependencies
            deps = data.get('dependencies', {})
            dev_deps = data.get('devDependencies', {})
            all_deps = {**deps, **dev_deps}
            
            for name, version in all_deps.items():
                # Чистка версии от спецсимволов npm (^, ~)
                clean_version = version.replace('^', '').replace('~', '').strip()
                
                # Пропуск локальных workspace-зависимости монорепозитория
                if clean_version.startswith('workspace:') or clean_version == '*':
                    continue
                    
                # Проверка дубликатов
                identifier = f"{name}@{clean_version}"
                if identifier in seen:
                    continue
                seen.add(identifier)
                
                # Формирирование м PURL (символ @ заменяется на %40 по стандарту)
                purl_name = name.replace('@', '%40')
                
                item = {
                    "name": name,
                    "version": clean_version,
                    "ecosystem": ecosystem,
                    "url": f"https://www.npmjs.com/package/{name}/v/{clean_version}",
                    "purl": f"pkg:npm/{purl_name}@{clean_version}"
                }
                result.append(item)
        except Exception as e:
            pass

# Запись в файл
with open('result_task_1.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=4)

print(f"Сбор завершен. Найдено уникальных пакетов: {len(result)}")
print(f"Сводка по экосистемам:\n- npm: {len(result)}")
