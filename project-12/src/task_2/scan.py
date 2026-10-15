#!/usr/bin/env python3
import argparse
import ipaddress
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except ImportError:
    print("Требуется библиотека pymongo. Установите её: "
          "pip install pymongo", file=sys.stderr)
    sys.exit(1)


# Стандартные порты MongoDB: mongod, а также shard/config-серверы.
DEFAULT_PORTS = [27017, 27018, 27019]


def parse_targets(target):
    """
    Разворачивает цель в список хостов.

    Поддерживается:
      - CIDR-нотация:   192.168.1.0/24
      - одиночный IP:   192.168.1.10
      - имя хоста:      db.example.local
    """
    if "/" in target:
        net = ipaddress.ip_network(target, strict=False)
        hosts = [str(ip) for ip in net.hosts()]
        # Для /32 и /31 net.hosts() может быть пустым — берём сам адрес сети.
        return hosts or [str(net.network_address)]
    return [target]


def port_open(host, port, timeout):
    """Быстрая проверка: принимает ли хост TCP-соединение на этом порту."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def check_mongo_no_auth(host, port, timeout):
    """
    Пытается подключиться к MongoDB и получить список баз данных без пароля.

    На корректно защищённом сервере команда list_database_names() бросит
    исключение (требуется аутентификация) — тогда возвращаем None.
    На открытом сервере команда выполнится успешно — возвращаем список имён баз.
    """
    ms = int(timeout * 1000)
    client = None
    try:
        client = MongoClient(
            host,
            port,
            serverSelectionTimeoutMS=ms,
            connectTimeoutMS=ms,
            socketTimeoutMS=ms,
            directConnection=True,
        )
        return client.list_database_names()
    except PyMongoError:
        return None
    finally:
        if client is not None:
            client.close()


def scan_host(host, ports, timeout):
    """Проверяет один хост по всем указанным портам. Возвращает список находок."""
    results = []
    for port in ports:
        if not port_open(host, port, timeout):
            continue
        dbs = check_mongo_no_auth(host, port, timeout)
        if dbs is not None:
            results.append((host, port, dbs))
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Сканирование сети на наличие MongoDB без аутентификации.")
    parser.add_argument("target",
                        help="Цель: CIDR (192.168.1.0/24), IP или имя хоста")
    parser.add_argument("-p", "--ports", default=",".join(map(str, DEFAULT_PORTS)),
                        help="Порты через запятую (по умолчанию 27017,27018,27019)")
    parser.add_argument("-t", "--threads", type=int, default=100,
                        help="Число потоков (по умолчанию 100)")
    parser.add_argument("--timeout", type=float, default=2.0,
                        help="Таймаут соединения в секундах (по умолчанию 2.0)")
    args = parser.parse_args()

    ports = [int(p) for p in args.ports.split(",") if p.strip()]
    targets = parse_targets(args.target)

    print(f"[*] Целей для сканирования: {len(targets)}")
    print(f"[*] Порты: {ports}")
    print("[*] Поиск открытых MongoDB (без пароля)...\n")

    found = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(scan_host, host, ports, args.timeout): host
                   for host in targets}
        for future in as_completed(futures):
            for host, port, dbs in future.result():
                found.append((host, port, dbs))
                print(f"[!] ОТКРЫТА без пароля: {host}:{port}")
                print(f"    Базы данных: {', '.join(dbs) if dbs else '(пусто)'}")

    print(f"\n[*] Готово. Найдено уязвимых экземпляров: {len(found)}")
    if not found:
        print("[*] Открытых MongoDB без аутентификации не обнаружено.")


if __name__ == "__main__":
    main()
