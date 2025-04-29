import socket
from dotenv import load_dotenv
from colorama import Fore, Style
import random
import sympy

HOST = '127.0.0.1'
PORT = 65432

def generate_prime(bits=5):
    while True:
        p = random.randint(10**(bits-1), 10**bits - 1)
        if sympy.isprime(p):
            return p

def generate_rsa_keys():
    print(Fore.GREEN + "[*] Generating RSA Key Pair..." + Style.RESET_ALL)
    p = generate_prime(5)
    q = generate_prime(5)
    while q == p:
        q = generate_prime(5)

    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = pow(e, -1, phi)

    print(Fore.YELLOW + f"[+] Prime p: {p}")
    print(f"[+] Prime q: {q}")
    print(f"[+] Modulus n = p * q: {n}")
    print(f"[+] Public Key (e, n): ({e}, {n})")
    print(f"[+] Private Key (d, n): ({d}, {n})" + Style.RESET_ALL)

    with open(".env", "w") as f:
        f.write(f"PUBLIC_KEY_E={e}\n")
        f.write(f"PUBLIC_KEY_N={n}\n")

    return (d, n)

def decrypt_block(d, n, block_int):
    decrypted_int = pow(block_int, d, n)
    return decrypted_int.to_bytes((decrypted_int.bit_length() + 7) // 8, 'big')

def start_server():
    load_dotenv()
    d, n = generate_rsa_keys()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(Fore.CYAN + f"\n[*] Receiver is waiting for sender on {HOST}:{PORT}...\n" + Style.RESET_ALL)
        conn, addr = s.accept()
        with conn:
            print(Fore.GREEN + f"[+] Connected by {addr}\n" + Style.RESET_ALL)
            data = conn.recv(4096).decode('utf-8')
            print(Fore.BLUE + f"[>] Received Cipher Blocks:\n{data}\n" + Style.RESET_ALL)

            try:
                cipher_blocks = [int(x.strip()) for x in data.split(',')]
                decrypted_bytes = b''.join([decrypt_block(d, n, c) for c in cipher_blocks])
                message = decrypted_bytes.decode('utf-8')
                print(Fore.MAGENTA + f"\n[✓] Decrypted Message:\n{message}" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"[!] Error decrypting message: {e}" + Style.RESET_ALL)

def main():
    print(Fore.CYAN + "=== RSA RECEIVER ===" + Style.RESET_ALL)
    start_server()

if __name__ == "__main__":
    main()
