# System Architecture Overview

This document explains how the entire chat application is structured. 
It describes the server, the client, the network communication, and the 
threads used in the system.

The system has three main components:

1. The central server  
2. The client application  
3. Direct communication between clients (TCP + UDP)

---

## 1. Server Architecture

The server is very simple. Its job is:
- Accept new client connections
- Receive registration messages
- Store the list of online peers (username, IP, ports)
- Send the peer list back when a client requests it

The server does NOT:
- relay chat messages  
- relay files  
- broadcast messages  

It is a "directory" server only.

### Server Flow (Text Diagram)

---

## 2. Client Architecture

Each client has several responsibilities:

1. Connect to the server and register  
2. Request the list of online peers  
3. Open a **TCP listener thread** (to receive chat messages)  
4. Open a **UDP listener thread** (to receive files)  
5. Allow the user to send:
   - chat messages (TCP)
   - files (UDP)
6. Display messages and file notifications in the GUI  

### Client Internal Structure
┌───────────────────────────────┐
│ Client │
│ │
│ ┌─────────────────────────┐ │
│ │ GUI │ │
│ └─────────────────────────┘ │
│ │
│ ┌──────────┐ ┌───────────┐ │
│ │ TCP Send │ │ UDP Send │ │
│ └──────────┘ └───────────┘ │
│ │
│ ┌──────────────┐ ┌──────────┐ │
│ │ TCP Listener │ │ UDP Listener│
│ └──────────────┘ └──────────┘ │
└───────────────────────────────┘
## 3. TCP Chat Communication

TCP is used for chat because:
- it guarantees delivery
- messages arrive in the correct order
- it's ideal for text

### TCP Chat Flow

---

## 4. UDP File Transfer Architecture

UDP is used for file transfer because:
- faster
- lightweight
- no connection overhead

The sender:
- reads file in chunks
- sends chunks over UDP
- sends "__END__" marker when done

The receiver:
- saves incoming chunks
- stops at "__END__"

### UDP Flow


---

## 5. Thread Overview

Each client runs:

### ✔ 1 TCP Listener Thread  
- waits for incoming chat messages

### ✔ 1 UDP Listener Thread  
- waits for incoming file chunks

### ✔ Main GUI Thread  
- user interactions
- sending chat
- browsing files
- updating UI

Threads allow the client to:
- receive messages while typing
- receive files while chatting
- keep the GUI responsive

---

## 6. Module/File Responsibilities

| File | Purpose |
|------|---------|
| **server.py** | Central directory server |
| **client.py** | Entry point for the client (starts GUI + threads) |
| **gui.py** | GUI layout and interactions |
| **network.py** | TCP/UDP communication functions |
| **threading_utils.py** | Helper functions for background threads |
| **protocol.md** | Defines the communication message formats |
| **architecture.md** | High-level system design |

---

## 7. High Level Data Flow (Very Simple Diagram)

        ┌──────────┐
        │  Server  │
        └────┬─────┘
             │
 Register    │   Peer List
             │
┌───────────────┴───────────────┐
│ │
│ Client A │
│ Client B │
│ Client C │
│ │
└─Chat (TCP)──────────────Chat (TCP)
└─File (UDP)──────────────File (UDP)