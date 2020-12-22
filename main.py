from clientThread import clientThread
from utils import readConfig

listenPort = 5001
sendPort = 5000
host = 'localhost'

nDevices = readConfig() * 2
devicesArray = []

# th1 = clientThread(host, listenPort, sendPort)
# th1.start()
# th2 = clientThread('localhost', 5000)
# th2.start()