from .lidar2d_imp import (
    _object,
    _swig_setattr,
    _swig_getattr,
    _swig_repr,
    _lidar2d,
    __builtin__,
)
import numpy as np
import time

class Rplidar(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Rplidar, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Rplidar, name)
    __repr__ = _swig_repr

    BAUDRATE_A2 = 256_000
    BAUDRATE_S2 = 1000_000

    MODE_STANDARD = 0  # 4KHz
    MODE_S2_BOOST = 1  # 32KHz
    MODE_A2_BOOST = 2  # 8KHz

    PORT = "/dev/ttyUSB0"

    def __init__(self, port=PORT, baudrate=BAUDRATE_S2):
        this = _lidar2d.new_Lidar2D()
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this
        assert self.connect(port, baudrate) and "Unknown serial..."

    __swig_destroy__ = _lidar2d.delete_Lidar2D
    __del__ = lambda self: None

    def connect(self, port=PORT, baudrate=BAUDRATE_A2):
        return _lidar2d.Lidar2D_connect(self, port, baudrate)

    def startMotor(self, mode=MODE_S2_BOOST):
        status = _lidar2d.Lidar2D_startScan(self, mode)
        time.sleep(1)
        return status

    def stopMotor(self):
        return _lidar2d.Lidar2D_stopScan(self)

    def getVectors(self, limit_distance=0, degree=True, quality=True):
        ret = np.array(_lidar2d.Lidar2D_getData(self, limit_distance, degree, quality))
        return ret

    def getXY(self, limit_distance=0, quality=True):
        return np.array(_lidar2d.Lidar2D_getXY(self, limit_distance, quality))[:, ::-1]

    def getMap(self, size=(300, 300), limit_distance=12000, quality=True):
        pixmap = np.zeros(size[::-1])

        width, height = (None, None)

        if type(size) in (tuple, list):
            width, height = (size[0] / 2, size[1] / 2)
        elif type(size) in (str, int, float):
            size = int(size)
            width, height = (size / 2, size / 2)
        else:
            raise (ValueError("The argument 'size' is not available."))

        coords = np.array(self.getXY(limit_distance=limit_distance, quality=quality))

        is_ranged = np.mean(np.abs(coords) < limit_distance, axis=1) == 1.0

        for i in range(len(is_ranged)):
            if is_ranged[i]:
                x, y = ((coords[i] * (1.0, -1.0)) / limit_distance) * (
                    width,
                    height,
                ) + (width, height)
                pixmap[int(y), int(x)] += 1

        std = np.mean(pixmap) + np.std(pixmap)

        if std != 0:
            pixmap = np.where(pixmap > std, std, pixmap)
            pixmap = (pixmap / std) * 255

        # pixmap = np.rot90(pixmap)
        return pixmap


Lidar2D_swigregister = _lidar2d.Lidar2D_swigregister
Lidar2D_swigregister(Rplidar)
