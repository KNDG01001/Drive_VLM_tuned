from .CAN import Can
import threading


class TPHG:
    INIT_TPHG = 0x280
    ACT_TPHG = 0x281
    BRD_TPHG = 0x380

    def __init__(self, dev="can0", bitrate=500000):
        self.__can = Can(dev, bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None
        self.__stop = False
        self.__can.setFilter(TPHG.BRD_TPHG)
        self.__can.write(TPHG.INIT_TPHG, [0xFF])

    def __del__(self):
        self.stop()

    def __callback(self):
        while not self.__stop:
            id, dlc, payload = self.__can.read(timeout=0.1)
            if not payload:
                continue
            elif id == TPHG.BRD_TPHG:
                temp = payload[0]
                press = (payload[2] << 8) | payload[1]
                humi = payload[3]
                gas = (
                    (payload[7] << 24)
                    | (payload[6] << 16)
                    | (payload[5] << 8)
                    | payload[4]
                )

                if self.__param:
                    self.__func((temp, press, humi, gas), self.__param)
                else:
                    self.__func((temp, press, humi, gas))

    def read(self):
        try:
            self.__can.write(TPHG.ACT_TPHG, [0x0f,0x00])
            id, dlc, payload = self.__can.read(timeout=2.0)

            if id == TPHG.BRD_TPHG:
                temp = payload[0]
                press = (payload[2] << 8) | payload[1]
                humi = payload[3]
                gas = (
                    (payload[7] << 24)
                    | (payload[6] << 16)
                    | (payload[5] << 8)
                    | payload[4]
                )

            return temp, press, humi, gas
        except:
            return None

    def callback(self, func, repeat=1, param=None):
        if not self.__thread:
            self.__func = func
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__thread.start()
            self.__can.write(TPHG.ACT_TPHG, [0x0f,repeat & 0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(TPHG.ACT_TPHG, [0x0, 0x00])
