import can
import time


class Can:
    def __init__(self, dev="can0", bitrate=500000, fd=True):
        self._bus = can.interface.Bus(
            channel=dev, bustype="socketcan", bitrate=bitrate, fd=True
        )
        self.__filter = []

    def __del__(self):
        self._bus.shutdown()

    def write(self, msg_id, buf, is_extended=False):
        msg = can.Message(arbitration_id=msg_id, is_extended_id=is_extended, data=buf)
        try:
            self._bus.send(msg)
            time.sleep(0.005)
            # time.sleep(0.020)
        except can.CanError:
            print("Can Interface Message does not Send")

    def read(self, timeout=2):
        msg = self._bus.recv(timeout=timeout)
        if msg:
            return msg.arbitration_id, msg.dlc, list(msg.data)
        else:
            return (None, None, None)

    def setFilter(self, can_id, mask=0x7FF):
        for i, f in enumerate(self.__filter):
            if f["can_id"] == can_id:
                if mask == 0:
                    del self.__filter[i]
                    return
                else:
                    self.__filter[i]["can_mask"] = mask
                    break
        else:
            self.__filter.append({"can_id": can_id, "can_mask": mask})
        self._bus.set_filters(self.__filter)
