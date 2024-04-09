#!/usr/bin/python3
import sys
import serial
import time
class TemperatureController:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.serial_port = serial.Serial(port, baudrate=baudrate, bytesize=8, parity='N', stopbits=1, timeout=timeout)
    def set_temperature(self, temperature):
        command = f"SS{temperature}"
        self._send_command(command)
        response = self.serial_port.readline().decode().strip()
        return response
    def read_temperature(self):
        self._send_command("RT")
        response = self.serial_port.readline().decode().strip()
        print(f"chiller temp: {response}")
        if response == '!':
            response == "command recieved"
            return response
        if response == '?':
            response = "unknown command"
        elif response and (response[0] == '+' or response[0] == '-') and response[1:].isdigit():
            response = float(response)
        return response
    def wait_for_temperature(self, target_temperature, threshold, timeout=None):
        start_time = time.time()

        while True:
            current_temperature = float(self.read_temperature())
            if current_temperature > (target_temperature - threshold) and current_temperature < (target_temperature + threshold):
                break

            if timeout is not None and (time.time() - start_time) > timeout:
                raise TimeoutError("Timeout waiting for the target temperature")
            time.sleep(5)  # Adjust the sleep interval as needed
        return current_temperature
    def _send_command(self, command):
        self.serial_port.write(command.encode() + b'\r')
