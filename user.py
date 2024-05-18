import tkinter as tk
import socket
import threading
import json
import os

HOST = '5.tcp.eu.ngrok.io'
PORT = 13896 

message_history = []

def load_message_history():
    global message_history
    if os.path.exists("message_history.json"):
        with open("message_history.json", "r") as file:
            message_history = json.load(file)

def save_message_history():
    with open("message_history.json", "w") as file:
        json.dump(message_history, file)

def receive_messages(client_socket, chat_text, client_name):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            received_message = data.decode()
            sender_name, message = received_message.split(": ", 1)
            if sender_name == client_name:
                chat_text.insert(tk.END, f"{message}\n")
            else:
                chat_text.insert(tk.END, f"{received_message}\n")
            message_history.append(received_message)
    except ConnectionResetError:
        chat_text.insert(tk.END, "Server connection closed.\n")

def send_message(event=None):
    message = entry_message.get()
    if message.lower() == 'exit':
        root.destroy()
        return
    client_socket.sendall(f"{client_name}: {message}".encode())
    entry_message.delete(0, tk.END)
    sent_message = f"{client_name}: {message}"
    message_history.append(sent_message)
    text_chat.insert(tk.END, f"{sent_message}\n")

def connect_to_server():
    global client_socket, client_name
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        client_name = entry_name.get()
        client_socket.sendall(client_name.encode())
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, text_chat, client_name))
        receive_thread.start()
        entry_name.config(state=tk.DISABLED)
        entry_message.config(state=tk.NORMAL)
        button_send.config(state=tk.NORMAL)
        for message in message_history:
            text_chat.insert(tk.END, f"{message}\n")
    except ConnectionRefusedError:
        text_chat.insert(tk.END, "Connection refused. Is the server running?\n")

root = tk.Tk()
root.title("Chat Application")

load_message_history()

label_name = tk.Label(root, text="Your Name:")
label_name.pack(pady=5)
entry_name = tk.Entry(root, width=30)
entry_name.pack(pady=5)

button_connect = tk.Button(root, text="Connect", command=connect_to_server)
button_connect.pack(pady=5)

text_chat = tk.Text(root, width=50, height=20)
text_chat.pack(pady=10)

entry_message = tk.Entry(root, width=50)
entry_message.pack(pady=5)

button_send = tk.Button(root, text="Send", command=send_message)
button_send.pack(pady=5)

entry_message.bind("<Return>", send_message)

root.mainloop()

save_message_history()