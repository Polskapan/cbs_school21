#!/bin/bash
#
# check_pki.sh — проверка структуры директории pki на соответствие
# требованиям задания.
#
# Ожидаемая структура:
#   pki/
#     certs/CAcert.crt
#     certs/server.crt
#     private/CAkey.key
#     newcerts/server.csr
#
# Использование: ./check_pki.sh [путь_к_pki]
# По умолчанию путь_к_pki = ./pki

PKI_DIR="${1:-./pki}"

REQUIRED_DIRS=(
    "certs"
    "private"
    "newcerts"
)

REQUIRED_FILES=(
    "certs/CAcert.crt"
    "private/CAkey.key"
    "private/server.key"
    "newcerts/server.csr"
    "certs/server.crt"
)

ok=true

echo "Проверка структуры PKI в: $PKI_DIR"
echo "----------------------------------------"

if [ ! -d "$PKI_DIR" ]; then
    echo "[FAIL] Директория $PKI_DIR не найдена"
    exit 1
fi

for d in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$PKI_DIR/$d" ]; then
        echo "[ OK ] Поддиректория присутствует: $d/"
    else
        echo "[FAIL] Отсутствует поддиректория: $d/"
        ok=false
    fi
done

echo "----------------------------------------"

for f in "${REQUIRED_FILES[@]}"; do
    if [ -f "$PKI_DIR/$f" ]; then
        size=$(stat -c%s "$PKI_DIR/$f" 2>/dev/null || stat -f%z "$PKI_DIR/$f")
        echo "[ OK ] Файл присутствует: $f (${size} байт)"
    else
        echo "[FAIL] Отсутствует файл: $f"
        ok=false
    fi
done

echo "----------------------------------------"

# Дополнительно: проверка, что server.crt действительно подписан CAcert.crt
if [ -f "$PKI_DIR/certs/CAcert.crt" ] && [ -f "$PKI_DIR/certs/server.crt" ]; then
    if openssl verify -CAfile "$PKI_DIR/certs/CAcert.crt" "$PKI_DIR/certs/server.crt" > /dev/null 2>&1; then
        echo "[ OK ] server.crt успешно проверяется цепочкой CAcert.crt"
    else
        echo "[FAIL] server.crt НЕ проходит проверку по CAcert.crt"
        ok=false
    fi
fi

echo "----------------------------------------"

if $ok; then
    echo "РЕЗУЛЬТАТ: структура PKI корректна."
    exit 0
else
    echo "РЕЗУЛЬТАТ: обнаружены проблемы (см. FAIL выше)."
    exit 1
fi
