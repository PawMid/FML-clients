import threading
# from convNet1 import convModel
import pickle
import socket
import time
import utils


# from numba import cuda


class clientThread(threading.Thread):
    def __init__(self, host, listenPort, sendPort):
        super().__init__()
        self.__host = host
        self.__listenPort = listenPort
        self.__sendPort = sendPort
        self.__listenConnection = socket.socket()
        self.__sendConnection = socket.socket()
        self.__bufferSize = 1024
        self.__model = None
        self.__listenerBuffer = []
        self.__listenerMutex = threading.Lock()
        self.__senderBuffer = []
        self.__senderMutex = threading.Lock()

    def __listenerThread(self):
        while True:
            self.__listenerMutex.acquire()
            print('listener')
            try:
                received_data = b''
                while str(received_data)[-2] != '.':
                    data = self.__listenConnection.recv(self.__bufferSize)
                    received_data += data
                if received_data != b'':
                    print('self.__listenerBuffer write')
                    self.__listenerBuffer.append(pickle.loads(received_data))
            finally:
                self.__listenerMutex.release()
                print('listener-x')
                time.sleep(1)

    def __senderThread(self):
        while True:
            self.__senderMutex.acquire()

            try:
                while not utils.empty(self.__senderBuffer):
                    self.__sendConnection.sendall(pickle.dumps(self.__senderBuffer.pop(0)))
            finally:
                self.__senderMutex.release()
                # print('Sender released mutex')
                time.sleep(1)

    def __mainThread(self):
        while True:
            message = None
            self.__listenerMutex.acquire()
            print('Main acquired mutex')
            try:
                if not utils.empty(self.__listenerBuffer):
                    message = self.__listenerBuffer.pop(0)
                    print(message)
            finally:
                # pass
                self.__listenerMutex.release()
            self.__senderMutex.acquire()
            try:
                if message is not None:
                    print('writing')
                    self.__senderBuffer.append(message)
            finally:
                self.__senderMutex.release()
                print("main released")
                time.sleep(1)

    def run(self):

        self.__listenConnection.connect((self.__host, self.__listenPort))
        self.__sendConnection.connect((self.__host, self.__sendPort))
        print('Connected')

        listener = threading.Thread(target=self.__listenerThread)
        sender = threading.Thread(target=self.__senderThread)
        main = threading.Thread(target=self.__mainThread)
        main.start()
        sender.start()
        listener.start()
