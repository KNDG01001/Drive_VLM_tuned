from .CAN import Can
import threading


class Light:
    ACT_LIGHT = 0x0B0
    BRD_LIGHT = 0x1B0

    def __init__(self, dev="can0", bitrate=500000):
        self.__can = Can(dev, bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None
        self.__stop = False
        self.__light = {Light.BRD_LIGHT: None}
        self.__can.setFilter(Light.BRD_LIGHT)

    def __del__(self):
        self.stop()

    def __callback(self):
        while not self.__stop:
            id, dlc, payload = self.__can.read(timeout=0.1)
            if not payload:
                continue
            else:
                light = ((payload[0] << 8) | payload[1]) / 2.4
                if self.__param:
                    self.__func((light), self.__param)
                else:
                    self.__func((light))

    def read(self):
        try:
            self.__can.write(Light.ACT_LIGHT, [0x00])
            id, dlc, payload = self.__can.read(timeout=2.0)

            if id == Light.BRD_LIGHT:
                light = ((payload[0] << 8) | payload[1]) / 2.4

            return light
        except:
            return None

    def callback(self, func, repeat=1, param=None):
        if not self.__thread:
            self.__func = func
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__thread.start()
            self.__can.write(Light.ACT_LIGHT, [repeat & 0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(Light.ACT_LIGHT, [0x0])
