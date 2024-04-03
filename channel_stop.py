import socket
import time

command = '<?xml version="1.0" encoding="UTF-8" ?>\n<bts version="1.0">\n <cmd>stop</cmd>\n \
   <list count = "1">\n  <stop ip="127.0.0.1" devtype="24" devid="58" subdevid="2" chlid="3">true</stop>\n </list>\n</bts>\n\n#\r\n'


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
s.connect(("192.168.1.250", 502))

s.send(command.encode())

time.sleep(2)
resp = s.recv(1024)

print(resp)
