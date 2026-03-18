from .CAN import Can
import threading
import numpy as np


class Psd:
    ACT_PSD = 0x040
    BRD_PSD = 0x140

    def __init__(self, dev="can0", bitrate=500000):
        self.__can = Can(dev, bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None
        self.__stop = False
        self.__can.setFilter(Psd.BRD_PSD)

    def __del__(self):
        self.stop()

    def __flatten(self, data):
        result = []
        
        for i in range(len(data)):
            result.append(data[i])
            
        return result

    def __callback(self):
        while not self.__stop:
            data = np.ndarray(
                shape=(3,),
                dtype=np.uint8,
            )
            id, dlc, payload = self.__can.read(timeout=2.0)
            if id == Psd.BRD_PSD:
                data[:] = payload
            if self.__param:
                self.__func(
                    self.__flatten(data),
                    self.__param,
                )
            else:
                self.__func(
                    self.__flatten(data)
                )

    def read(self):
        data = np.ndarray(
            shape=(3,),
            dtype=np.uint8,
        )
        self.__can.write(Psd.ACT_PSD, [0x07, 0x00])
        id, dlc, payload = self.__can.read(timeout=2.0)
        if id == Psd.BRD_PSD:
            data[:] = payload

        return self.__flatten(data)

    def callback(self, func, repeat=1, param=None):
        if not self.__thread:
            self.__func = func
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__thread.start()
            self.__can.write(Psd.ACT_PSD, [0x07, repeat & 0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(Psd.ACT_PSD, [0x00, 0x00])
