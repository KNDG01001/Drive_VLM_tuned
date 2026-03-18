from .CAN import Can
import threading


class Switch:
    ACT_SWITCH = 0x240
    BRD_SWITCH = 0x340

    def __init__(self, dev="can0", bitrate=500000):
        self.__can = Can(dev, bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None
        self.__stop = False
        self.__can.setFilter(Switch.BRD_SWITCH)

    def __del__(self):
        self.stop()

    def __callback(self):
        while not self.__stop:
            id, dlc, payload = self.__can.read(timeout=0.1)

            if not payload:
                continue
            elif id == Switch.BRD_SWITCH:
                if self.__param:
                    self.__func((payload[0], payload[1], payload[2], payload[3]), self.__param)
                else:
                    self.__func((payload[0], payload[1], payload[2], payload[3]))

    def read(self):
        try:
            self.__can.write(Switch.ACT_SWITCH, [0x00])
            id, dlc, payload = self.__can.read(timeout=2.0)

            if id == Switch.BRD_SWITCH:
                switch = (payload[0], payload[1], payload[2], payload[3])

            return switch
        except:
            return None

    def callback(self, func, repeat=1, param=None):
        if not self.__thread:
            self.__func = func
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__thread.start()
            self.__can.write(Switch.ACT_SWITCH, [repeat & 0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(Switch.ACT_SWITCH, [0x00])
