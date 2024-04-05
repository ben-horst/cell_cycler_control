import socket
import time
import logging
import xml.etree.ElementTree as ET
from barcode_manager import BarcodeManager

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
        self.barcode_manager = BarcodeManager()

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
            return self._socket.recv(38768).decode()
        except:
            print("response timed out")

    def chlcodes_to_tuples(self, chlcodes):
        """takes a list of channel codes in the form of (devid)(subdevid)(chlid) like "580206" and converts to tuple like (58,2,6)"""
        tuple_list = []
        for chlcode in chlcodes:
            chlcode = str(chlcode)
            devid = int(chlcode[0:2])
            subdevid = int(chlcode[2:4])
            chlid = int(chlcode[4:6])
            tuple_list.append((devid,subdevid,chlid))
        return tuple_list

    def get_device_info(self):
        """request all active channels from entire server"""
        xml_command = ' <cmd>getdevinfo</cmd></bts>\n\n#\r\n'
        msg = self.XML_HEADER + xml_command
        xml_string = self.send_command(msg)
        root = ET.fromstring(xml_string.replace('#',''))
        ip_data = root[1][0].attrib #root[1] is ip_data -- currently not returned
        channel_data = []
        for channel in root[2]:    #root[2] is channel info
            channel_data.append(channel.attrib)
        return channel_data

    def stop_channels(self, chlcodes):
        """accepts a list of channel codes in the form string "580206" and stops those channels"""
        cells = self.chlcodes_to_tuples(chlcodes)
        num_cells = len(cells)
        xml_command = f' <cmd>stop</cmd>\n <list count = "{num_cells}">\n'
        cell_addresses = ''
        for cell in cells:
            cell_addresses = cell_addresses + (f'  <stop ip="{self.__ip_address}" devtype="24" devid="{cell[0]}" subdevid="{cell[1]}" chlid="{cell[2]}">true</stop>\n')
        msg = self.XML_HEADER + xml_command + cell_addresses + self.XML_TAIL
        xml_string = self.send_command(msg)
        root = ET.fromstring(xml_string.replace('#',''))
        channel_data = []
        for channel in root[1]:    #root[1] is channel info under <list>
            dict = channel.attrib
            dict.update({"stop result": channel.text})
            channel_data.append(dict)
        return channel_data

    def get_channels_status(self, chlcodes):
        """requests current working status of each channel"""
        """accepts a list of channel codes in the form string "580206" and stops those channels"""
        cells = self.chlcodes_to_tuples(chlcodes)
        num_cells = len(cells)
        xml_command = f' <cmd>getchlstatus</cmd>\n <list count = "{num_cells}">\n'
        cell_addresses = ''
        for cell in cells:
            cell_addresses = cell_addresses + (f'  <status ip="{self.__ip_address}" devtype="24" devid="{cell[0]}" subdevid="{cell[1]}" chlid="{cell[2]}">true</status>\n')
        msg = self.XML_HEADER + xml_command + cell_addresses + self.XML_TAIL
        resp = self.send_command(msg)
        xml_string = self.send_command(msg)
        root = ET.fromstring(xml_string.replace('#',''))
        channel_data = []
        for channel in root[1]:    #root[1] is channel info in <list>
            channel_data.append(channel.attrib)
        return channel_data
    
    def get_channels_current_data(self, chlcodes):
        """requests the realtime data from a list of cells (voltage, current, step type, temp, etc) """
        """accepts a list of tuples, each containing the a cells address in the form (devid, subdevid, chlid) like (58,2,7)"""
        """accepts a list of channel codes in the form string "580206" and stops those channels"""
        cells = self.chlcodes_to_tuples(chlcodes)
        num_cells = len(cells)
        xml_command = f' <cmd>inquire</cmd>\n <list count = "{num_cells}">\n'
        cell_addresses = ''
        for cell in cells:
            cell_addresses = cell_addresses + (f'  <inquire ip="{self.__ip_address}" devtype="24" devid="{cell[0]}" subdevid="{cell[1]}" chlid="{cell[2]}">true</inquire>\n')
        msg = self.XML_HEADER + xml_command + cell_addresses + self.XML_TAIL
        resp = self.send_command(msg)
        xml_string = self.send_command(msg)
        root = ET.fromstring(xml_string.replace('#',''))
        channel_data = []
        for channel in root[1]:    #root[1] is channel info in <list>
            channel_data.append(channel.attrib)
        return channel_data
    
    def start_channels(self, chlcodes, profile_path):
        """accepts a list of channel codes in the form string "580206" and stops those channels
        also accepts path to test profile. automatically finds barcodes for each channel"""
        cells = self.chlcodes_to_tuples(chlcodes)
        barcodes = self.barcode_manager.barcodes_from_chlcodes(chlcodes)
        num_cells = len(cells)
        xml_command = f' <cmd>start</cmd>\n <list count = "{num_cells}">\n'
        cell_addresses = ''
        for cell, barcode in zip(cells, barcodes):
            cell_addresses = cell_addresses + (f'  <start ip="{self.__ip_address}" devtype="24" devid="{cell[0]}" subdevid="{cell[1]}" chlid="{cell[2]}" barcode="{barcode}">{profile_path}</start>\n')
        msg = self.XML_HEADER + xml_command + cell_addresses + self.XML_TAIL
        xml_string = self.send_command(msg)
        root = ET.fromstring(xml_string.replace('#',''))
        channel_data = []
        for channel in root[1]:    #root[1] is channel info in <list>
            channel_data.append(channel.attrib)
        #return channel_data
        return xml_string