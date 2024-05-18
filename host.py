import socket
import threading
import queue

HOST = '0.0.0.0'  
PORT = 5555      

clients = {}  

def handle_client(client_socket, client_address):
    print(f"New connection: {client_address}")

    try:
        client_name = client_socket.recv(1024).decode().strip()
        clients[client_address] = (client_socket, client_name)

        while True:
            data = client_socket.recv(1024)

            if not data:
                break 

            sender_name = clients[client_address][1]
            message = f"{sender_name}: {data.decode()}"
            message_queue.put(message)

    except ConnectionResetError:
        print(f"Connection lost: {client_address}")
    finally:
        client_socket.close()
        del clients[client_address]
        print(f"Connection closed: {client_address}")

def broadcast_messages():
    while True:
        while not message_queue.empty():
            message = message_queue.get()
            for (addr, (sock, name)) in clients.items():
                try:
                    sock.sendall(message.encode())
                except:
                    del clients[addr]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    print(f"Server is listening on {HOST}:{PORT}...")

    server_socket.listen()

    message_queue = queue.Queue()

    broadcast_thread = threading.Thread(target=broadcast_messages)
    broadcast_thread.start()

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

    except KeyboardInterrupt:
        print("Server is shutting down...")

    finally:
        server_socket.close()