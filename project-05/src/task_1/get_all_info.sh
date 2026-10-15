#!/bin/bash

# Скрипт должен запускаться только от root
if [[ "$EUID" -ne 0 ]]; then
    echo "Запустите скрипт от root."
    exit 1
fi

INFO_FILE="info"
ARCHIVE_NAME="OS_RESULT.tar"

# Очищаем старый файл
> "$INFO_FILE"

echo "===== ИНФОРМАЦИЯ О СИСТЕМЕ =====" >> "$INFO_FILE"
echo "" >> "$INFO_FILE"

# Версия ядра
echo "===== ВЕРСИЯ ЯДРА =====" >> "$INFO_FILE"
uname -r >> "$INFO_FILE"
echo "" >> "$INFO_FILE"

# Версия ОС
echo "===== ВЕРСИЯ ОПЕРАЦИОННОЙ СИСТЕМЫ =====" >> "$INFO_FILE"
if [[ -f /etc/os-release ]]; then
    cat /etc/os-release >> "$INFO_FILE"
else
    uname -a >> "$INFO_FILE"
fi
echo "" >> "$INFO_FILE"

# Установка cowsay и sl
echo "===== УСТАНОВКА ПАКЕТОВ cowsay И sl =====" >> "$INFO_FILE"

if command -v apt >/dev/null 2>&1; then
    apt update >> "$INFO_FILE" 2>&1
    apt install -y cowsay sl >> "$INFO_FILE" 2>&1

elif command -v dnf >/dev/null 2>&1; then
    dnf install -y cowsay sl >> "$INFO_FILE" 2>&1

elif command -v yum >/dev/null 2>&1; then
    yum install -y cowsay sl >> "$INFO_FILE" 2>&1

elif command -v pacman >/dev/null 2>&1; then
    pacman -Sy --noconfirm cowsay sl >> "$INFO_FILE" 2>&1

else
    echo "Не найден поддерживаемый пакетный менеджер." >> "$INFO_FILE"
fi

echo "" >> "$INFO_FILE"

# Установленные пакеты
echo "===== УСТАНОВЛЕННЫЕ ПАКЕТЫ =====" >> "$INFO_FILE"

if command -v dpkg >/dev/null 2>&1; then
    dpkg -l >> "$INFO_FILE"
elif command -v rpm >/dev/null 2>&1; then
    rpm -qa >> "$INFO_FILE"
elif command -v pacman >/dev/null 2>&1; then
    pacman -Q >> "$INFO_FILE"
fi

echo "" >> "$INFO_FILE"

# Запущенные процессы
echo "===== ЗАПУЩЕННЫЕ ПРОЦЕССЫ =====" >> "$INFO_FILE"
ps aux >> "$INFO_FILE"
echo "" >> "$INFO_FILE"

# Открытые порты
echo "===== ОТКРЫТЫЕ ПОРТЫ =====" >> "$INFO_FILE"

if command -v ss >/dev/null 2>&1; then
    ss -tulnp >> "$INFO_FILE"
elif command -v netstat >/dev/null 2>&1; then
    netstat -tulnp >> "$INFO_FILE"
fi

echo "" >> "$INFO_FILE"

# Удаляем старый архив, если есть
rm -f "$ARCHIVE_NAME"

# Создание архива
tar -cf "$ARCHIVE_NAME" "$INFO_FILE"

# Удаляем файл info
rm -f "$INFO_FILE"

echo "Готово. Информация сохранена в $INFO_FILE и упакована в $ARCHIVE_NAME"
