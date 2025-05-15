#!/usr/bin/python3
import sys
import serial
import time
class TemperatureController:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.open_comport()
        self.close_comport()
    def __str__(self):
        return f'Chiller controller object on comport {self.serial_port}'
    def open_comport(self):
        self.serial_port = serial.Serial(self.port, baudrate=self.baudrate, bytesize=8, parity='N', stopbits=1, timeout=self.timeout)
    def close_comport(self, retries = 5):
        for attempt in range(1, retries+1):
            self.serial_port.close()
            if not self.serial_port.is_open:
                break
            else:
                attempt += 1
    def set_temperature(self, temperature):
        command = f"SS{temperature}"
        self._send_command(command)
        response = self.serial_port.readline().decode().strip()
        self.close_comport()
        return response
    def read_temperature(self):
        self._send_command("RT")
        response = self.serial_port.readline().decode().strip()
        #print(f"chiller temp: {response}")
        if response == '!':
            response == "command received"
            return response
        elif response == '?':
            response = "unknown command"
        else:
            response.replace('+', '')
            try:
                response = float(response)
            except:
                print('bad chiller message')
        self.close_comport()
        return response
    def _send_command(self, command):
        if self.serial_port is None or not self.serial_port.is_open:
            self.open_comport()
        try:
            self.serial_port.write(command.encode() + b'\r')
        except serial.SerialException as e:
            print(f'Serial Error: {e}')
