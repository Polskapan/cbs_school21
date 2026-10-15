#!/bin/bash

set -e

# Проверка запуска от root
if [[ $EUID -ne 0 ]]; then
    echo "Запустите скрипт от root"
    exit 1
fi

# Создание групп
groupadd -f default_users
groupadd -f secret_users

# Создание пользователя user
if ! id "user" &>/dev/null; then
    useradd -m -s /bin/bash -g default_users user
fi

# Создание секретных пользователей
for u in secret_agent secret_spy secret_boss
do
    if ! id "$u" &>/dev/null; then
        useradd -m -s /bin/bash -g secret_users "$u"
    fi

    # Домашняя директория доступна только владельцу и группе secret_users
    chown "$u:secret_users" /home/"$u"
    # Запрет доступа остальным к home секретных пользователей
    chmod 770 /home/"$u"
done

# Директория /var доступна всем
chmod 755 /var

# Установка apache2
apt update
apt install -y apache2

# Запуск и включение в автозагрузку
systemctl enable apache2
systemctl start apache2

# Проверка состояния
echo "Состояние apache2:"
systemctl status apache2 --no-pager

# default_users без пароля через sudo
echo "%default_users ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/default_users
chmod 440 /etc/sudoers.d/default_users

echo "Готово."
