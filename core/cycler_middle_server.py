import socket
import threading
import queue
import time
from collections import deque

# Configuration
HOST = 'localhost'
PORT = 9000
CELL_CYCLER_HOST = "127.0.0.1"
CELL_CYCLER_PORT = 502
RECONNECT_DELAY = 5  # seconds
MAX_MESSAGE_SIZE = 38768  # bytes
SERVER_SIDE_TIMEOUT = 1.0  # seconds
CLIENT_SIDE_TIMEOUT = 1.0

# FIFO Queue: (client_socket, address, message) or None as sentinel for shutdown
message_queue = queue.Queue()

# Debug events ring buffer
_events_lock = threading.Lock()
_events = deque(maxlen=500)
_stop_event = threading.Event()
_server_socket = None

def _log_event(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    with _events_lock:
        _events.append(line)
    print(line)

def get_debug_events():
    with _events_lock:
        return list(_events)

def cell_cycler_worker():
    """Worker thread that maintains a persistent connection to the cell cycler server with reconnection logic"""
    cc_sock = None

    while not _stop_event.is_set():
        if cc_sock is None:
            try:
                cc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cc_sock.settimeout(SERVER_SIDE_TIMEOUT)
                cc_sock.connect((CELL_CYCLER_HOST, CELL_CYCLER_PORT))
                _log_event("[*] Connected to downstream cell cycler server")
            except Exception as e:
                _log_event(f"[!] Failed to connect to downstream cell cycler server: {e}. Retrying in {RECONNECT_DELAY} seconds...")
                time.sleep(RECONNECT_DELAY)
                continue

        item = message_queue.get()
        if item is None or _stop_event.is_set():
            break
        client_socket, address, message = item

        try:
            # Send message to cell cycler
            _log_event(f"[>] Forwarding {len(message)} bytes from client {address} to downstream")
            cc_sock.send(message)

            # Read response (fixed size)
            response = cc_sock.recv(MAX_MESSAGE_SIZE)

            # Send response back to client
            _log_event(f"[<] Received {len(response)} bytes from downstream; returning to client {address}")
            client_socket.sendall(response)

        except Exception as e:
            _log_event(f"[!] Error forwarding to downstream: {e}")
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
    # Cleanup
    try:
        if cc_sock is not None:
            cc_sock.close()
    except:
        pass

def client_thread(client_socket, address):
    _log_event(f"[+] Client connected: {address}")
    try:
        client_socket.settimeout(CLIENT_SIDE_TIMEOUT)

        while not _stop_event.is_set():
            try:
                data = client_socket.recv(MAX_MESSAGE_SIZE)
                if not data:
                    _log_event(f"[-] Client disconnected: {address}")
                    break   #socket closed the connection
                _log_event(f"[~] Received {len(data)} bytes from client {address}")
                message_queue.put((client_socket, address, data))
            except socket.timeout:
                continue    #allow for socket timeouts

    except Exception as e:
        _log_event(f"[!] Error with client {address}: {e}")
    finally:
        client_socket.close()
        _log_event(f'[-] Socket closed at {address}')

def start_server():
    global _server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.settimeout(1.0)
    _server_socket = server_socket

    _log_event(f"[*] Middle server listening on {HOST}:{PORT}")

    # Start persistent cell cycler worker thread
    threading.Thread(target=cell_cycler_worker, daemon=True).start()

    try:
        while not _stop_event.is_set():
            try:
                client_sock, addr = server_socket.accept()
                threading.Thread(target=client_thread, args=(client_sock, addr), daemon=True).start()
            except socket.timeout:
                continue    #this allows periodic checking for a ctrl-c interrupt
            except OSError:
                # Likely server_socket closed during shutdown
                if _stop_event.is_set():
                    break
                else:
                    continue
    except KeyboardInterrupt:
        _log_event('[!] Server shutting down...')
    finally:
        server_socket.close()
        _server_socket = None

def stop_server():
    """Signal the middle server to stop and close sockets."""
    if _stop_event.is_set():
        return
    _log_event('[!] Stop requested for middle server')
    _stop_event.set()
    try:
        # Close listening socket to break accept()
        if _server_socket is not None:
            _server_socket.close()
    except:
        pass
    # Wake the worker thread
    try:
        message_queue.put_nowait(None)
    except:
        pass

if __name__ == "__main__":
    start_server()
