from .CAN import Can
import threading
import numpy as np


class Ultrasonic:
    ACT_ULTRASONIC = 0x030
    BRD_ULTRASONIC = 0x130

    def __init__(self, dev="can0", bitrate=500000):
        self.__can = Can(dev, bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None
        self.__stop = False
        self.__can.setFilter(Ultrasonic.BRD_ULTRASONIC)

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
                shape=(6,),
                dtype=np.uint8,
            )
            id, _, payload = self.__can.read(timeout=2.0)
            if id == Ultrasonic.BRD_ULTRASONIC:
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
            shape=(6,),
            dtype=np.uint8,
        )

        self.__can.write(Ultrasonic.ACT_ULTRASONIC, [0x3F, 0x00])
        id, _, payload = self.__can.read(timeout=2.0)
        if id == Ultrasonic.BRD_ULTRASONIC:
            data[:] = payload

        return self.__flatten(data)

    def callback(self, func, repeat=1, param=None):
        if not self.__thread:
            self.__func = func
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__thread.start()
            self.__can.write(Ultrasonic.ACT_ULTRASONIC, [0x3F, repeat & 0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(Ultrasonic.ACT_ULTRASONIC, [0x00, 0x00])
