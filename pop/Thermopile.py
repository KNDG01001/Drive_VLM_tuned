from .CAN import Can
import threading


class Thermopile:
    ACT_THERMO = 0x2A0
    BRD_THERMO = 0x3A0

    def __init__(self, dev="can0", bitrate=500000):
        self.__can = Can(dev, bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None
        self.__stop = False
        self.__can.setFilter(Thermopile.BRD_THERMO)

    def __del__(self):
        self.stop()

    def __callback(self):
        while not self.__stop:
            id, dlc, payload = self.__can.read(timeout=0.1)
            if not payload:
                continue
            elif id == Thermopile.BRD_THERMO:
                ir = (payload[1] << 8) | payload[0]
                if self.__param:
                    self.__func((ir), self.__param)
                else:
                    self.__func((ir))

    def read(self):
        try:
            self.__can.write(Thermopile.ACT_THERMO, [0x00])
            id, dlc, payload = self.__can.read(timeout=2.0)

            if id == Thermopile.BRD_THERMO:
                ir = (payload[1] << 8) | payload[0]

            return ir
        except:
            return None

    def callback(self, func, repeat=1, param=None):
        if not self.__thread:
            self.__func = func
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__thread.start()
            self.__can.write(Thermopile.ACT_THERMO, [repeat & 0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(Thermopile.ACT_THERMO, [0x00])
