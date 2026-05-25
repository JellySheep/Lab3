Необходимость для задания 2:
* Нужно создать токен гитхаба с возможностью чтения и залить его в файл .env в папке проекта, формат ввода - echo "GITHUB_TOKEN=" > .env

Файлы названы в соответствии с заданиями, make_bom.py и analyze.py требуются для задания №5:
* make_bom.py - проводит инвентаризацию аналогично четвёртому, но в формате, который понимает сканер. Принимает аргумент выходного файла, лучше всего использовать make_bom.py bom_before.cdx.json и bom_after.cdx.json.
* analyze.py проводит сравнение файлов скана и bom`ов, после чего выдает краткий итог.

Установка сканера:
```
wget https://github.com/google/osv-scanner/releases/latest/download/osv-scanner_linux_amd64 -O osv-scanner

chmod +x osv-scanner
```

4е и 5е задания:
```
python3 task4.py

python3 make_bom.py bom_before.cdx.json

./osv-scanner -L bom_before.cdx.json --format json > scan_before.json

apt update && apt upgrade -y

python3 make_bom.py bom_after.cdx.json

./osv-scanner -L bom_after.cdx.json --format json > scan_after.json

python3 analyze.py
```




