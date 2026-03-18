from .CAN import Can
import threading, struct


class Encoder:
    ACT_ENCODER = 0x011
    BRD_ENCODER = 0x111

    def __init__(self, dev="can0", bitrate=500000):
        self.__can = Can(dev, bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None
        self.__stop = False
        self.__can.setFilter(Encoder.BRD_ENCODER)

    def __del__(self):
        self.stop()

    def __callback(self):
        while not self.__stop:
            id, _, payload = self.__can.read(timeout=2.0)

            if not payload:
                continue
            elif id == Encoder.BRD_ENCODER:
                status = payload[0]
                enc_data = struct.unpack("hhh", struct.pack("BBBBBB", *(payload[1:])))

                if self.__param:
                    self.__func(
                        (status, enc_data[0], enc_data[1], enc_data[2]),
                        self.__param,
                    )
                else:
                    self.__func((status, enc_data[0], enc_data[1], enc_data[2]))

    def callback(self, func, repeat=1, param=None):
        if not self.__thread:
            self.__func = func
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__thread.start()
            self.__can.write(Encoder.ACT_ENCODER, [0x07, repeat & 0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(Encoder.ACT_ENCODER, [0x0, 0x00])
