import socket
import time
import logging
import xml.etree.ElementTree as ET

class CellCycler():
    """this is a class to control and communicate with Neware cell cyclers over their TCP API"""
    def __init__(self, ip_address="127.0.0.1", port=502, log_level=logging.INFO, timeout=1, delay=0, **kwargs):
        """initialize comms on a specified address and port"""
        self.__ip_address = ip_address
        self.__port = port
        self.__timeout = timeout
        self.__delay = delay
        comms_logger = logging.getLogger('socket')
        comms_logger.setLevel(log_level)
        self.XML_HEADER = '<?xml version="1.0" encoding="UTF-8" ?>\n<bts version="1.0">\n'
        self.XML_TAIL = ' </list>\n</bts>\n\n#\r\n'

        self.reconnect()

    def reconnect(self):
        if hasattr(self, "_socket"):
            self._socket.close()
        time.sleep(1)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self.__timeout)
        self._socket.connect((self.__ip_address, self.__port))

    def send_command(self, msg):
        time.sleep(self.__delay)
        self._socket.send(msg.encode())
        time.sleep(self.__delay)
        try:
            return self._socket.recv(1024).decode()
        except:
            print("response timed out")

    def xml_to_dict(self, xml_string):
        """takes in string form of xml response from Neware and returns a list of dictionaries for each item in the <list> element"""
        root = ET.fromstring(xml_string)
        cell_data = []
        for cell in root[1]:    #root[1] is <list>
            cell_data.append(cell.attrib)
        return cell_data

    def get_device_info(self):
        """request all active channels from entire server"""
        xml_command = ' <cmd>getdevinfo</cmd></bts>\n\n#\r\n'
        msg = self.XML_HEADER + xml_command
        resp = self.send_command(msg)
        #do something with response
        return resp

    def stop_channels(self, cells):
        """accepts a list of tuples, each containing the a cells address in the form (devid, subdevid, chlid) like (58,2,7)"""
        num_cells = len(cells)
        xml_command = f' <cmd>stop</cmd>\n <list count = "{num_cells}">\n'
        cell_addresses = ''
        for cell in cells:
            cell_addresses = cell_addresses + (f'  <stop ip={self.__ip_address} devtype="24" devid={cell[0]} subdevid={cell[1]} chlid={cell[2]}>true</stop>\n')
        msg = self.XML_HEADER + xml_command + cell_addresses + self.XML_TAIL
        resp = self.send_command(msg)
        return resp

    def get_channels_status(self, cells):
        """requests current working status of each channel"""
        """accepts a list of tuples, each containing the a cells address in the form (devid, subdevid, chlid) like (58,2,7)"""
        num_cells = len(cells)
        xml_command = f' <cmd>getchlstatus</cmd>\n <list count = "{num_cells}">\n'
        cell_addresses = ''
        for cell in cells:
            cell_addresses = cell_addresses + (f'  <status ip={self.__ip_address} devtype="24" devid={cell[0]} subdevid={cell[1]} chlid={cell[2]}>true</stop>\n')
        msg = self.XML_HEADER + xml_command + cell_addresses + self.XML_TAIL
        resp = self.send_command(msg)
        #do something with response
        return resp
    
    def get_channels_current_data(self, cells):
        """requests the realtime data from a list of cells (voltage, current, step type, temp, etc) """
        """accepts a list of tuples, each containing the a cells address in the form (devid, subdevid, chlid) like (58,2,7)"""
        num_cells = len(cells)
        xml_command = f' <cmd>inquire</cmd>\n <list count = "{num_cells}">\n'
        cell_addresses = ''
        for cell in cells:
            cell_addresses = cell_addresses + (f'  <status ip={self.__ip_address} devtype="24" devid={cell[0]} subdevid={cell[1]} chlid={cell[2]}>true</stop>\n')
        msg = self.XML_HEADER + xml_command + cell_addresses + self.XML_TAIL
        resp = self.send_command(msg)
        #pull lots of info out of the response

        return resp
