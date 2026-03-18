from .CAN import Can
import threading


class Analog:
    ACT_Analog = 0x260
    BRD_Analog = 0x360

    def __init__(self, dev="can0", bitrate=500000):
        self.__can = Can(dev, bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None
        self.__stop = False
        self.__can.setFilter(Analog.BRD_Analog)

    def __del__(self):
        self.stop()

    def __callback(self):
        cds, ntc, vr = 0, 0, 0

        while not self.__stop:
            id, dlc, payload = self.__can.read(timeout=0.1)

            if not payload:
                continue
            elif id == Analog.BRD_Analog:
                cds = (payload[1] << 8) | payload[0]
                ntc = (payload[3] << 8) | payload[2]
                vr = (payload[5] << 8) | payload[4]

            if self.__param:
                self.__func((cds, ntc, vr), self.__param)
            else:
                self.__func((cds, ntc, vr))

    def read(self):
        try:
            self.__can.write(Analog.ACT_Analog, [0x1F, 0x00])
            id, dlc, payload = self.__can.read(timeout=2.0)

            if id == Analog.BRD_Analog:
                cds = (payload[1] << 8) | payload[0]
                ntc = (payload[3] << 8) | payload[2]
                vr = (payload[5] << 8) | payload[4]

            return cds, ntc, vr
        except:
            return None

    def callback(self, func, repeat=1, param=None):
        if not self.__thread:
            self.__func = func
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__thread.start()
            self.__can.write(Analog.ACT_Analog, [0x1F, repeat & 0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(Analog.ACT_Analog, [0x0, 0x00])
