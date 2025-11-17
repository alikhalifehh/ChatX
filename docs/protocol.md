# Project Protocol Specification

This document defines the communication protocol used between:
- The central server
- All clients
- Peer-to-peer messaging (TCP)
- Peer-to-peer file transfers (UDP)

---

## 1. Server Communication Protocol

Clients communicate with the server using **JSON messages over TCP**.

### 1.1. Register Message (Client → Server)
Sent when a client first connects to the server.

{
  "type": "register",
  "username": "<string>",
  "tcp_port": <int>,
  "udp_port": <int>
}

The server stores:
- username
- client IP
- TCP port
- UDP port

---

### 1.2. Peer List Request (Client → Server)

{
  "type": "peer_list"
}

The client sends this to ask for the list of currently connected peers.

---

### 1.3. Peer List Response (Server → Client)

{
  "type": "peer_list",
  "peers": [
    {
      "username": "<string>",
      "ip": "<string>",
      "tcp_port": <int>,
      "udp_port": <int>
    }
  ]
}

The server responds with all active peers except the requesting client.

---

## 2. Peer-to-Peer TCP Chat Protocol

Chat messages are sent directly **between clients** using TCP.

Format:

{
  "type": "chat",
  "from": "<sender_username>",
  "message": "<text_message>"
}

Clients must:
1. Have a TCP listener running in a background thread
2. Receive JSON messages
3. Display them in the GUI chat window

---

## 3. File Transfer Protocol (UDP)

File transfers occur directly **between clients**, using UDP sockets.

### 3.1. Sending a File
- The sender opens the file in binary mode
- Reads it in fixed-size chunks (example: 4096 bytes)
- Sends each chunk using UDP to the receiver's UDP port

### 3.2. End of Transmission
After sending the last chunk, the sender must send:

__END__

(As bytes)

Example:
b"__END__"

The receiver:
- Writes each incoming chunk into a file
- Stops when it receives the end marker

---

## 4. Summary of Message Types

| Message Type | Direction          | Purpose |
|--------------|--------------------|---------|
| register     | Client → Server    | Register new peer |
| peer_list    | Client → Server    | Request list of peers |
| peer_list    | Server → Client    | Provide list of peers |
| chat         | Client → Client    | Send chat message |
| file chunks  | Client → Client    | Send file data (UDP) |
| __END__      | Client → Client    | End of UDP file transfer |

---

## 5. Notes

- All TCP messages are JSON-encoded UTF-8 strings.
- UDP messages are raw bytes.
- The project uses:
  - **TCP for chat (reliable delivery)**
  - **UDP for file transfer (fast, no connection overhead)**
- Each client maintains:
  - 1 TCP listener thread
  - 1 UDP listener thread
