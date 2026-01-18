import socket
import threading
from cryptography.fernet import Fernet
from datetime import datetime
from flask import Flask, render_template

server_status = {
    "running": True,
    "clients": 0,
    "events": []
}

def log_event(msg):
    server_status["events"].append(
        f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    )

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("index.html", status=server_status)

def start_dashboard():
    app.run(port=8000, debug=False, use_reloader=False)


HOST = "127.0.0.1"
PORT = 5000

clients = {}         
groups = {}           

lock = threading.Lock()

def generate_group_key():
    return Fernet.generate_key()

def rotate_group_key(group):
    new_key = generate_group_key()
    groups[group]["key"] = new_key

    for member in groups[group]["members"]:
        try:
            member.sendall(b"NEW_KEY:" + new_key)
        except:
            pass

    log_event(f"Group '{group}' key rotated")


def handle_client(conn, addr):
    username = None
    joined_groups = set()

    try:
        username = conn.recv(1024).decode()

        with lock:
            clients[conn] = username
            server_status["clients"] = len(clients)

        log_event(f"Client connected: {username} ({addr})")

        while True:
            data = conn.recv(4096)
            if not data:
                break

            message = data.decode()

            if message.startswith("JOIN"):
                _, group = message.split(maxsplit=1)

                with lock:
                    if group not in groups:
                        groups[group] = {
                            "members": set(),
                            "key": generate_group_key()
                        }

                    groups[group]["members"].add(conn)
                    joined_groups.add(group)
                    rotate_group_key(group)

                log_event(f"{username} joined group '{group}'")

            elif message.startswith("LEAVE"):
                _, group = message.split(maxsplit=1)

                with lock:
                    if group in groups and conn in groups[group]["members"]:
                        groups[group]["members"].remove(conn)
                        joined_groups.discard(group)
                        rotate_group_key(group)

                log_event(f"{username} left group '{group}'")

            elif message.startswith("MSG"):
                _, group, enc_msg = message.split(" ", 2)

                with lock:
                    if group in groups:
                        for member in groups[group]["members"]:
                            if member != conn:
                                member.sendall(
                                    b"MSG " + group.encode() + b" " + enc_msg.encode()
                                )

    except Exception as e:
        log_event(f"Error with client {addr}: {e}")

    finally:
        with lock:
            for group in joined_groups:
                if group in groups and conn in groups[group]["members"]:
                    groups[group]["members"].remove(conn)
                    rotate_group_key(group)

            clients.pop(conn, None)
            server_status["clients"] = len(clients)

        conn.close()
        log_event(f"Client disconnected: {username}")


def start_server():
    threading.Thread(target=start_dashboard, daemon=True).start()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    log_event("Secure chat server started")
    print("Server running...")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        ).start()

if __name__ == "__main__":
    start_server()
