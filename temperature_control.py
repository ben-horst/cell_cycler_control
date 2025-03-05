#!/usr/bin/python3
import sys
import serial
import time
class TemperatureController:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.serial_port = serial.Serial(port, baudrate=baudrate, bytesize=8, parity='N', stopbits=1, timeout=timeout)
    def __str__(self):
        return f'Chiller controller object on comport {self.serial_port}'
    def set_temperature(self, temperature):
        command = f"SS{temperature}"
        self._send_command(command)
        response = self.serial_port.readline().decode().strip()
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
