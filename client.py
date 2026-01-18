import socket
import threading
from cryptography.fernet import Fernet

HOST = "127.0.0.1"
PORT = 5000

group_keys = {}   # group -> Fernet instance


def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break

            if data.startswith(b"NEW_KEY:"):
                key = data[len(b"NEW_KEY:"):]
                group_keys["current"] = Fernet(key)
                print("[+] Group key rotated")

            elif data.startswith(b"MSG"):
                _, group, enc_msg = data.split(b" ", 2)
                fernet = group_keys.get("current")
                if fernet:
                    message = fernet.decrypt(enc_msg).decode()
                    print(f"[{group.decode()}] {message}")

        except Exception as e:
            print("Receive error:", e)
            break


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    username = input("Username: ")
    sock.sendall(username.encode())

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        msg = input("> ")

        if msg.startswith("/join"):
            _, group = msg.split(maxsplit=1)
            sock.sendall(f"JOIN {group}".encode())

        elif msg.startswith("/leave"):
            _, group = msg.split(maxsplit=1)
            sock.sendall(f"LEAVE {group}".encode())

        else:
            if "current" not in group_keys:
                print("[-] Join a group first")
                continue

            encrypted = group_keys["current"].encrypt(msg.encode())
            sock.sendall(b"MSG group1 " + encrypted)


if __name__ == "__main__":
    main()
