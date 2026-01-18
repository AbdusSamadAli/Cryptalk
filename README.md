🔐 Cryptalk

Cryptalk is a Python-based secure group messaging system that implements end-to-end encryption with dynamic key rotation to protect group communications from eavesdropping, insider threats, and unauthorized access after membership changes.

The project focuses on cryptographic correctness, key lifecycle management, and secure system design, with a minimal monitoring dashboard for observability.

🚨 Problem Statement

Traditional encrypted chat systems often rely on a single shared key per session or group.
This approach introduces serious security risks:

Former group members can decrypt future messages

Key compromise exposes all past and future communication

No cryptographic access revocation exists when users leave

Cryptalk addresses these gaps by introducing dynamic key rotation and strict access revocation while keeping the server blind to message contents.

🔑 Key Management & Security Flow

A client joins a group

Server generates a new Fernet key

Key is distributed only to active group members

Messages are encrypted client-side

Server forwards ciphertext only

On membership change → key rotation enforced

Disconnected users lose cryptographic access

🔐 Security Validation (Tested & Verified)

✔ Verified end-to-end encryption by inspecting server-side payloads (ciphertext only)

✔ Confirmed integrity enforcement via HMAC tamper detection

✔ Tested dynamic key rotation on group membership changes

✔ Ensured access revocation for disconnected clients

✔ Verified server never accesses plaintext messages

✨ Features

End-to-end encrypted group messaging

Dynamic key rotation on join / leave / disconnect

Protection against insider threats

Multi-threaded TCP server for concurrent clients

Server-side blindness to plaintext

Minimal Flask dashboard for security monitoring

Clean separation of encryption, routing, and observability

🧰 Tech Stack
Core

Python 3

Socket Programming (TCP/IP)

Threading

Cryptography

cryptography (Fernet)

AES-128 encryption

HMAC for integrity

Timestamp-based replay protection

Monitoring

Flask (minimal, read-only dashboard)

HTML (single static template)
