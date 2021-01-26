import threading
from convNet1 import convModel
import pickle
import socket
import time
import utils
from comunicationCodes import ComCodes
import sys
import zlib
import imgSrc
import tensorflow as tf
import random


class clientThread(threading.Thread):
    def __init__(self, host, listenPort, sendPort, name, trainPath, testerPort):
        super().__init__()
        graph = tf.Graph()
        with graph.as_default():
            self.__model = convModel(trainPath)
        self.__trainPath = trainPath
        self.__trained = True
        self.__trainRequestSent = False
        self.__accuracy = None

        # Federated server connection
        self.__host = host
        self.__listenPort = listenPort
        self.__sendPort = sendPort
        self.__listenConnection = socket.socket()
        self.__sendConnection = socket.socket()
        self.__bufferSize = 1024
        self.__listenerBuffer = []
        self.__listenerMutex = threading.Lock()
        self.__senderBuffer = []
        self.__senderMutex = threading.Lock()
        self.setName(name)

        # Tester connection
        self.__testerPort = testerPort
        self.__testerListenSocket = socket.socket()
        self.__testerListenSocket.bind((host, testerPort))
        self.__testerListenerBuffer = []
        self.__testerListenerMutex = threading.Lock()

        self.__testerSendSocket = socket.socket()
        self.__testerSendSocket.bind((host, testerPort + 1))

        self.__testerSendConnection = None
        self.__testerListenConnection = None


    def __listenerThread(self):
        while True:

            try:
                received_data = b''
                size = pickle.loads(self.__listenConnection.recv(self.__bufferSize))
                print('Device', self.getName(),'receiving data of size', size)
                while sys.getsizeof(received_data) < size:
                    data = self.__listenConnection.recv(self.__bufferSize)
                    received_data += data
                    # progressBar(size, sys.getsizeof(received_data))
                # progressBar(size, sys.getsizeof(received_data), True)
                self.__listenerMutex.acquire()
                if received_data != b'':
                    self.__listenerBuffer.append(pickle.loads(zlib.decompress(received_data)))
                self.__listenerMutex.release()
                print('Device', self.getName(), 'received all data of size', size)
            finally:
                time.sleep(1)

    def __testerListenerThread(self):
        while True:
            try:
                if self.__testerListenConnection is not None:
                    received_data = b''
                    size = pickle.loads(self.__testerListenConnection.recv(self.__bufferSize))
                    while sys.getsizeof(received_data) < size:
                        data = self.__testerListenConnection.recv(self.__bufferSize)
                        received_data += data
                    self.__testerListenerMutex.acquire()
                    if received_data != b'':
                        self.__testerListenerBuffer.append(pickle.loads(zlib.decompress(received_data)))
                    self.__testerListenerMutex.release()

            finally:
                time.sleep(1)

    def __send(self, mesage, server=True):
        resp = zlib.compress(pickle.dumps(mesage), 4)
        size = sys.getsizeof(resp)
        # print('sending', mesage)
        if server:
            self.__sendConnection.sendall(pickle.dumps(size))
            time.sleep(1)
            self.__sendConnection.sendall(resp)
        else:
            self.__testerSendConnection.sendall(pickle.dumps(size))
            time.sleep(1)
            self.__testerSendConnection.sendall(resp)

    def updateModel(self, summary=False):
        self.__send([ComCodes.GET_STRUCTURE])
        time.sleep(2)
        self.__send([ComCodes.GET_WEIGHTS])

        while True:
            if not utils.empty(self.__listenerBuffer):
                message = self.__listenerBuffer.pop(0)
                if message[0] is ComCodes.GET_STRUCTURE:
                    print('Device', self.getName(), 'is setting structure')
                    self.__model.setNet(message[1], summary=summary)
                elif message[0] is ComCodes.GET_WEIGHTS:
                    print('Device', self.getName(), 'is setting weights')
                    self.__model.setTrainableWeights(message[1])
                    return

    def trainModel(self):
        print('training')
        # Model initialization
        self.updateModel()

        print('model updated')
        sleep = random.uniform(1, 3)
        print('Device', self.getName(), 'is waiting for', sleep, 'secs')
        time.sleep(random.uniform(1, 3))
        self.__trainRequestSent = False
        self.__trained = False
        # time.sleep(1)
        self.__send([ComCodes.CAN_TRAIN])

        # Ask if haven`t trained yet
        while True:
            # if not self.__trained and not self.__trainRequestSent:
            #     self.__send([ComCodes.CAN_TRAIN])
            #     self.__trainRequestSent = True

            self.__listenerMutex.acquire()
            try:
                if not utils.empty(self.__listenerBuffer):
                    message = self.__listenerBuffer.pop(0)
                    # print('message', message)

                    if message[0] is ComCodes.CAN_TRAIN:
                        if message[1] is True:
                            self.__send([ComCodes.IS_PARTICIPANT, True], False)
                            print('training')
                            self.__model.trainModel()
                            self.__model.getConfusionMatrix(imgSrc.results)
                            self.__model.learningCurves(imgSrc.results)
                            print(self.getName(), 'getting accuracy')
                            self.__accuracy = self.__model.getAccuracy()[1]
                            response = [ComCodes.POST_WEIGHTS, self.__model.getTrainableWeights()]
                            self.__send(response)
                            self.__send([ComCodes.POST_ACCURACY, self.__accuracy], False)
                        if message[1] is False:
                            self.__send([ComCodes.IS_PARTICIPANT, False], False)
                        return
            finally:
                self.__listenerMutex.release()

    def __mainThread(self):
        while True:
            action = None
            try:
                self.__testerListenerMutex.acquire()
                if len(self.__testerListenerBuffer) > 0:
                    action = self.__testerListenerBuffer.pop()
                    print(self.getName(), action)
            finally:
                self.__testerListenerMutex.release()
            if action is not None:
                if action[0] == ComCodes.GET_ACCURACY:
                    self.updateModel()
                    self.__accuracy = self.__model.getAccuracy()[1]
                    self.__send([ComCodes.POST_ACCURACY, self.__accuracy], False)

                elif action[0] == ComCodes.RETRAIN_MODEL:
                    self.trainModel()
            time.sleep(1)

    def run(self):

        main = threading.Thread(target=self.__mainThread)
        main.setName(self.getName() + '-main')
        main.start()

        print(self.getName(), 'is waiting for tester to connect. On ports:', self.__testerPort, self.__testerPort + 1)
        self.__testerListenSocket.listen(1)
        self.__testerSendSocket.listen(1)
        self.__testerSendConnection, sendAddr = self.__testerSendSocket.accept()
        self.__testerListenConnection, addr = self.__testerListenSocket.accept()

        print('Tester connected to host:', self.getName())

        testerListener = threading.Thread(target=self.__testerListenerThread,
                                          name=self.getName() + '_tester_listener')

        testerListener.start()

        self.__listenConnection.connect((self.__host, self.__listenPort))
        self.__sendConnection.connect((self.__host, self.__sendPort))
        print('Connected')

        listener = threading.Thread(target=self.__listenerThread)
        listener.setName(self.getName() + '-listener')

        listener.start()
