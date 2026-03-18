from .CAN import Can
import threading


class ToF:
    INIT_ToF = 0x270
    ACT_ToF = 0x271
    BRD_ToF = 0x370

    def __init__(self, dev="can0", bitrate=500000):
        self.__can = Can(dev, bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None
        self.__stop = False
        self.__can.setFilter(ToF.BRD_ToF)
        self.__can.write(ToF.INIT_ToF, [0xFF])

    def __del__(self):
        self.stop()

    def __callback(self):
        while not self.__stop:
            id, dlc, payload = self.__can.read(timeout=0.1)
            if not payload:
                continue
            elif id == ToF.BRD_ToF:
                range = (payload[1] << 8) | payload[0]

                if self.__param:
                    self.__func((range), self.__param)
                else:
                    self.__func((range))

    def read(self):
        try:
            self.__can.write(ToF.ACT_ToF, [0x00])
            id, dlc, payload = self.__can.read(timeout=2.0)

            if id == ToF.BRD_ToF:
                range = (payload[1] << 8) | payload[0]

            return range
        except:
            return None

    def callback(self, func, repeat=1, param=None):
        if not self.__thread:
            self.__func = func
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__thread.start()
            self.__can.write(ToF.ACT_ToF, [repeat & 0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(ToF.ACT_ToF, [0x0])
