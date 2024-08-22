from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo

class Thingsboard():
    def __init__(self):
        self.token = '28d0mndtu8r8wwp2cc3u'
        self.host = 'mqtt.thingsboard.cloud'
        self.client = TBDeviceMqttClient(self.host, username=self.token)
        #self.connect()

    def connect(self):
       self.client.connect()

    def disconnect(self):
        self.client.disconnect()

    def sendTelemetry(self, telemetry):
        self.connect()
        self.client.send_telemetry(telemetry)
        self.disconnect()
