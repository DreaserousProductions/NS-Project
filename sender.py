import socket
import os
from dotenv import load_dotenv
from colorama import Fore, Style

HOST = '127.0.0.1'
PORT = 65432

def split_into_blocks(data: bytes, block_size: int):
    return [data[i:i+block_size] for i in range(0, len(data), block_size)]

def encrypt_message(e, n, message: str):
    message_bytes = message.encode('utf-8')
    max_block_len = (n.bit_length() - 1) // 8
    blocks = split_into_blocks(message_bytes, max_block_len)
    return [pow(int.from_bytes(block, 'big'), e, n) for block in blocks]

def main():
    load_dotenv()
    try:
        e = int(os.getenv("PUBLIC_KEY_E"))
        n = int(os.getenv("PUBLIC_KEY_N"))
    except:
        print(Fore.RED + "[!] Failed to load public key from .env" + Style.RESET_ALL)
        return

    print(Fore.CYAN + "=== RSA SENDER ===" + Style.RESET_ALL)
    msg = input(Fore.MAGENTA + "\nEnter message to encrypt and send: " + Style.RESET_ALL)
    encrypted_blocks = encrypt_message(e, n, msg)

    cipher_str = ','.join(str(b) for b in encrypted_blocks)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(Fore.YELLOW + f"\n[*] Connecting to receiver at {HOST}:{PORT}..." + Style.RESET_ALL)
        s.connect((HOST, PORT))
        s.sendall(cipher_str.encode('utf-8'))
        print(Fore.GREEN + "\n[✓] Message sent successfully!" + Style.RESET_ALL)

if __name__ == "__main__":
    main()