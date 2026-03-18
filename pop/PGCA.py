from .CAN import Can
import threading


class PGCA:
    INIT_PGCA = 0x290
    ACT_PGCA = 0x291
    BRD_PGCA_P = 0x390
    BRD_PGCA_G = 0x391
    BRD_PGCA_C = 0x392
    BRD_PGCA_A = 0x393

    def __init__(self, dev="can0", bitrate=500000):
        self.__can = Can(dev, bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None
        self.__stop = False

        self.__pgca = {
            PGCA.BRD_PGCA_P: None,
            PGCA.BRD_PGCA_G: None,
            PGCA.BRD_PGCA_C: None,
            PGCA.BRD_PGCA_A: None,
        }
        for f in self.__pgca.keys():
            self.__can.setFilter(f)
        self.__can.write(PGCA.INIT_PGCA, [0xFF])

    def __del__(self):
        self.stop()

    # def __callback(self):
    #     while not self.__stop:
    #         id, dlc, payload = self.__can.read(timeout=0.1)

    #         if not payload:
    #             continue
    #         elif id == PGCA.BRD_PGCA_P:
    #             self.__pgca[id] = payload[0]
    #         elif id == PGCA.BRD_PGCA_G:
    #             if payload[0] == 1:
    #                 self.__pgca[id] = "Up"
    #             elif payload[0] == 2:
    #                 self.__pgca[id] = "Down"
    #             elif payload[0] == 4:
    #                 self.__pgca[id] = "Left"
    #             elif payload[0] == 8:
    #                 self.__pgca[id] = "Right"
    #         elif id == PGCA.BRD_PGCA_C:
    #             self.__pgca[id] = (
    #                 (payload[1] << 8) | payload[0],
    #                 (payload[3] << 8) | payload[2],
    #                 (payload[5] << 8) | payload[4],
    #                 (payload[7] << 8) | payload[6],
    #             )
    #         elif id == PGCA.BRD_PGCA_A:
    #             self.__pgca[id] = (payload[1] << 8) | payload[0]

    #         if self.__param:
    #             self.__func(tuple(self.__pgca.values()), self.__param)
    #         else:
    #             self.__func(tuple(self.__pgca.values()))

    def Proximity(self):
        try:
            self.__can.write(PGCA.ACT_PGCA, [0x01, 0x00])
            id, dlc, payload = self.__can.read(timeout=2.0)

            if id == PGCA.BRD_PGCA_P:
                self.__pgca[id] = payload[0]

            return self.__pgca[id]
        except:
            return None

    def Gesture(self):
        try:
            self.__can.write(PGCA.ACT_PGCA, [0x02, 0x00])
            id, dlc, payload = self.__can.read(timeout=2.0)

            if id == PGCA.BRD_PGCA_G:
                if payload[0] == 1:
                    self.__pgca[id] = "Up"
                elif payload[0] == 2:
                    self.__pgca[id] = "Down"
                elif payload[0] == 4:
                    self.__pgca[id] = "Left"
                elif payload[0] == 8:
                    self.__pgca[id] = "Right"
                else:
                    return None

            return self.__pgca[id]
        except:
            return None

    def Color(self):
        try:
            self.__can.write(PGCA.ACT_PGCA, [0x04, 0x00])
            id, dlc, payload = self.__can.read(timeout=2.0)

            if id == PGCA.BRD_PGCA_C:
                self.__pgca[id] = (
                    (payload[1] << 8) | payload[0],
                    (payload[3] << 8) | payload[2],
                    (payload[5] << 8) | payload[4],
                    (payload[7] << 8) | payload[6],
                )
                return self.__pgca[id]
            else:
                return None
        except:
            return None

    def ALS(self):
        try:
            self.__can.write(PGCA.ACT_PGCA, [0x08, 0x00])
            id, dlc, payload = self.__can.read(timeout=2.0)

            if id == PGCA.BRD_PGCA_A:
                self.__pgca[id] = (payload[1] << 8) | payload[0]
                return self.__pgca[id]
            else:
                return None
        except:
            return None

    # def callback(self, func, repeat=1, param=None):
    #     if not self.__thread:
    #         self.__func = func
    #         self.__param = param
    #         self.__stop = False
    #         self.__thread = threading.Thread(target=self.__callback)
    #         self.__thread.start()
    #         self.__can.write(PGCA.ACT_PGCA, [0x0F, repeat & 0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(PGCA.ACT_PGCA, [0x0, 0x00])
