import json

def analyze_vulnerabilities(input_file, output_md):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    table_data = []

    for item in data:
        name = item.get('name', 'N/A')
        version = item.get('version', 'N/A')
        ecosystem = item.get('ecosystem', 'N/A')
        vulns = item.get('vulnerabilities', [])
        secure_version = item.get('secure_version', 'Нет данных')

        # Считает количество уязвимостей по группам критичности
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MODERATE': 0, 'LOW': 0}
        for v in vulns:
            sev = v.get('severity', 'UNKNOWN').upper()
            if sev in severity_counts:
                severity_counts[sev] += 1
            else:
                severity_counts[sev] = 1 

        total_vulns = len(vulns)

        # Формирование рекомендуемых стратегий
        if secure_version != 'Нет данных':
            strategy = f"Обновить пакет до версии {secure_version}"
            
            # Проверка на мажорное обновление (может сломать совместимость)
            try:
                curr_major = int(version.split('.')[0])
                sec_major = int(secure_version.split('.')[0])
                if sec_major > curr_major:
                    strategy += " (внимание: мажорное обновление, требует проверки совместимости кода)"
            except Exception:
                pass
        else:
            strategy = "Найти безопасный аналог или применить патч вручную"

        # Формирует строку со статистикой критичности
        sev_str = ", ".join([f"{k}: {v}" for k, v in severity_counts.items() if v > 0])

        table_data.append({
            'name': name,
            'version': version,
            'ecosystem': ecosystem,
            'severities': sev_str,
            'total_vulns': total_vulns,
            'secure_version': secure_version,
            'strategy': strategy
        })

    # Сортируется по убыванию общего количества уязвимостей
    table_data.sort(key=lambda x: x['total_vulns'], reverse=True)

    # Запись результата в Markdown файл для отчета
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("| Наименование | Версия | Экосистема | Уязвимости (по критичности) | Версия без уязв. | Рекомендуемая стратегия |\n")
        f.write("|---|---|---|---|---|---|\n")
        for row in table_data:
            f.write(f"| {row['name']} | {row['version']} | {row['ecosystem']} | **Всего: {row['total_vulns']}** ({row['severities']}) | {row['secure_version']} | {row['strategy']} |\n")

    print(f"Анализ завершен! Таблица сохранена в файл: {output_md}")

if __name__ == "__main__":
    analyze_vulnerabilities('result_task_2.json', 'result_task_3.md')
