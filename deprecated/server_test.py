# import socket
# import time

# socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket.bind(("100.76.18.55", 80))
# socket.listen()
# conn, addr = socket.accept()
# with conn:
#     print(f"Connected by {addr}")
#     while True:
#         data = conn.recv(1024)
#         print(data.decode())

from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = "100.76.18.55"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")