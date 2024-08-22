from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo



token = '28d0mndtu8r8wwp2cc3u'

telemetry = {"temperature": 41.9, "enabled": False, "currentFirmwareVersion": "v1.2.2", "dict": {"item1": 123, "item2": 456}}
client = TBDeviceMqttClient("mqtt.thingsboard.cloud", username=token)
# Connect to ThingsBoard
client.connect()
# Sending telemetry without checking the delivery status
client.send_telemetry(telemetry) 
# Sending telemetry and checking the delivery status (QoS = 1 by default)
result = client.send_telemetry(telemetry)
# get is a blocking call that awaits delivery status  
success = result.get() == TBPublishInfo.TB_ERR_SUCCESS
# Disconnect from ThingsBoard
client.disconnect()