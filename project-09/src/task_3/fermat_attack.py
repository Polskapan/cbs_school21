from Crypto.Util.number import long_to_bytes, inverse

try:
    import gmpy2

    isqrt = gmpy2.isqrt
    _mpz = gmpy2.mpz
except ImportError:
    from math import isqrt as _pyisqrt

    isqrt = _pyisqrt
    _mpz = int


def fermat_factor(n: int, max_iterations: int = 200_000_000):
    """
    Факторизует n = p * q методом Ферма, предполагая, что p и q близки.
    Возвращает (p, q) с p >= q.

    Примечание: используется gmpy2 (если доступен) для быстрого isqrt на
    больших числах так как math.isqrt из stdlib заметно медленнее при
    переборе в десятки миллионов итераций.
    """
    n = _mpz(n)
    a = isqrt(n)
    if a * a < n:
        a += 1

    for i in range(max_iterations):
        b2 = a * a - n
        b = isqrt(b2)
        if b * b == b2:
            p = int(a + b)
            q = int(a - b)
            return p, q
        a += 1

    raise ValueError("Не удалось разложить N методом Ферма за отведённое число итераций "
                     "(p и q, вероятно, недостаточно близки для этого лимита)")


def main():
    # --- Исходные данные из crypto.py ---
    e = 65537
    n = 55089599753625499150129246679078411260946554356961748980861372828434789664694269460953507615455541204658984798121874916511031276020889949113155608279765385693784204971246654484161179832345357692487854383961212865469152326807704510472371156179457167612793412416133943976901478047318514990960333355366785001217

    with open("ciphertext.txt") as f:
        ciphertext_hex = f.read().strip()
    ciphertext_int = int(ciphertext_hex, 16)

    # --- 1. Атака Ферма: находим p и q ---
    print("[*] Запуск атаки Ферма...")
    p, q = fermat_factor(n)
    assert p * q == n, "Проверка p*q == n не пройдена!"
    print(f"[+] Найдены множители:")
    print(f"    p = {p}")
    print(f"    q = {q}")

    # --- 2. Вычисляем закрытую экспоненту d ---
    phi = (p - 1) * (q - 1)
    d = inverse(e, phi)
    print(f"[+] d вычислен (закрытая экспонента RSA)")

    # --- 3. Расшифровка ---
    plaintext_int = pow(ciphertext_int, d, n)
    flag = long_to_bytes(plaintext_int)
    print(f"[+] FLAG: {flag.decode(errors='replace')}")

    with open("solution.txt", "w") as f:
        f.write(flag.decode(errors="replace"))

    return flag


if __name__ == "__main__":
    main()
