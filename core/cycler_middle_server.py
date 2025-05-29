import socket
import threading
import queue
import time

# Configuration
HOST = 'localhost'
PORT = 9000
CELL_CYCLER_HOST = "127.0.0.1"
CELL_CYCLER_PORT = 502
RECONNECT_DELAY = 5  # seconds
MAX_MESSAGE_SIZE = 38768  # bytes
SERVER_SIDE_TIMEOUT = 1.0  # seconds
CLIENT_SIDE_TIMEOUT = 1.0

# FIFO Queue: (client_socket, message)
message_queue = queue.Queue()

def cell_cycler_worker():
    """Worker thread that maintains a persistent connection to the cell cycler server with reconnection logic"""
    cc_sock = None

    while True:
        if cc_sock is None:
            try:
                cc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cc_sock.settimeout(SERVER_SIDE_TIMEOUT)
                cc_sock.connect((CELL_CYCLER_HOST, CELL_CYCLER_PORT))
                print("[*] Connected to cell cycler server")
            except Exception as e:
                print(f"[!] Failed to connect to cell cycler server: {e}. Retrying in {RECONNECT_DELAY} seconds...")
                time.sleep(RECONNECT_DELAY)
                continue

        client_socket, message = message_queue.get()

        try:
            # Send message to cell cycler
            cc_sock.send(message)

            # Read response (fixed size)
            response = cc_sock.recv(MAX_MESSAGE_SIZE)

            # Send response back to client
            client_socket.sendall(response)

        except Exception as e:
            print(f"[!] Error forwarding to cell cycler: {e}")
            try:
                client_socket.sendall(b"ERROR\n")
            except:
                pass
            # Drop the connection to force reconnect
            try:
                cc_sock.close()
            except:
                pass
            cc_sock = None
        finally:
            pass

def client_thread(client_socket, address):
    print(f"[+] Connected: {address}")
    try:
        client_socket.settimeout(CLIENT_SIDE_TIMEOUT)

        while True:
            try:
                data = client_socket.recv(MAX_MESSAGE_SIZE)
                if not data:
                    print(f"[-] Client disconnected: {address}")
                    break   #socket closed the connection
                message_queue.put((client_socket, data))
            except socket.timeout:
                continue    #allow for socket timeouts

    except Exception as e:
        print(f"[!] Error with client {address}: {e}")
    finally:
        client_socket.close()
        print(f'[-] Socket closed at {address}')

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.settimeout(1.0)

    print(f"[*] Server listening on {HOST}:{PORT}")

    # Start persistent cell cycler worker thread
    threading.Thread(target=cell_cycler_worker, daemon=True).start()

    try:
        while True:
            try:
                client_sock, addr = server_socket.accept()
                threading.Thread(target=client_thread, args=(client_sock, addr), daemon=True).start()
            except socket.timeout:
                continue    #this allows periodic checking for a ctrl-c interrupt
    except KeyboardInterrupt:
        print('\n[!] Server shutting down...')
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
