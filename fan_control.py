import serial

class FanController:
    def __init__(self, port, baudrate=19200, timeout=1):
        self.serial_port = serial.Serial(port, baudrate=baudrate, timeout=timeout)
    def turn_on(self, relayNum):
        cmd = f"relay on {relayNum}\n\r"
        self.serial_port.write(cmd.encode())
        resp = self.serial_port.read(100).decode()
        return resp
    def turn_off(self, relayNum):
        cmd = f"relay off {relayNum}\n\r"
        self.serial_port.write(cmd.encode())
        resp = self.serial_port.read(100).decode()
        return resp
    def get_relay_state(self, relayNum):
        cmd = f"relay read {relayNum}\n\r"
        self.serial_port.write(cmd.encode())
        resp = self.serial_port.read(100).decode()
        if (resp.find('on') > 0):
            return 'on'
        elif (resp.find('off') > 0):
            return 'off'
