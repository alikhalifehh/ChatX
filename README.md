# ChatX
Install Python 3.10+

Ensure Tkinter is installed (included in most Python setups)

Start the server:

Open a terminal

Navigate to the project folder

Run python server.py

Start a client:

Open a new terminal

Navigate to the project folder

Run python client.py <username> <tcp_port> <udp_port>

Start additional clients:

Use unique usernames, TCP ports, and UDP ports for each client

Use the application:

The GUI launches automatically

Select a peer from the dropdown list

Send text messages (encrypted over TCP)

Send files (encrypted over UDP)

Received files appear as clickable links in the chat window

All events are logged in logs/activity.log

Optional cleanup:

Delete logs/activity.log to clear logs

Remove received files (saved as received_<filename>)