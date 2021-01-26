from clientThread import clientThread
from utils import getClientsNumber, getTesterPort


listenPort = 5001
sendPort = 5000
host = 'localhost'
testerPort = getTesterPort()

# 3 devices ok
nDevices = getClientsNumber()
devicesArray = []
logical = []

for i in range(nDevices):
    devicesArray.append(clientThread(host, listenPort, sendPort, 'client_'+str(i), 'device_'+str(i), testerPort + 2 * i))

for device in devicesArray:
    device.start()