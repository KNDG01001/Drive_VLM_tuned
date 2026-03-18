from .CAN import Can
import threading, struct

class Imu:
    ACT_IMU         =   0x020
    BRD_ACCEL       =   0x121
    BRD_MAGNETIC    =   0x122
    BRD_GYRO        =   0x123
    BRD_EULER       =   0x124
    BRD_QUAT        =   0x126

    def __init__(self, dev='can0', bitrate=500000):
        self.__can = Can(dev,bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None
        self.__stop = False
        self.__imu = {Imu.BRD_ACCEL:None, Imu.BRD_MAGNETIC:None, Imu.BRD_GYRO:None, Imu.BRD_EULER:None, Imu.BRD_QUAT:None}
        for f in self.__imu.keys():
            self.__can.setFilter(f)

    def __del__(self):
        self.stop()

    def __calc_accel_xyz(self, payload): #ACCEL
        xyz_scale = struct.unpack('hhh',struct.pack('BBBBBB',*payload))
        xyz = tuple(map(lambda n:n/100, xyz_scale[:]))
        return xyz

    def __calc_magnetic_xyz(self,payload): #MAGNETIC
        xyz_scale = struct.unpack('hhh',struct.pack('BBBBBB',*payload))
        xyz = tuple(map(lambda n:n/16, xyz_scale[:]))
        return xyz

    def __calc_gyro_xyz(self,payload): #GYRO
        xyz_scale = struct.unpack('hhh',struct.pack('BBBBBB',*payload))
        xyz = tuple(map(lambda n:n/916,xyz_scale[:]))
        return xyz

    def __calc_euler_xyz(self,payload): #EULER
        xyz_scale = struct.unpack('hhh',struct.pack('BBBBBB',*payload))
        xyz = tuple(map(lambda n:n/16,xyz_scale[:]))
        return xyz

    def __calc_wxyz(self,payload): #QUAT
        raw_wxyz = struct.unpack('hhhh',struct.pack('BBBBBBBB',*payload))
        wxyz = tuple(map(lambda n:n/(1<<14),raw_wxyz))
        return wxyz

    def __callback(self):
        while not self.__stop:
            self.__imu = self.__imu.fromkeys(self.__imu.keys(), None)
            while not all(self.__imu.values()) and not self.__stop:
                id, _, payload = self.__can.read(timeout=0.1)
                
                if not payload:
                    continue
                else:
                    if id == Imu.BRD_ACCEL:
                        self.__imu[id] = self.__calc_accel_xyz(payload)
                    elif id == Imu.BRD_MAGNETIC:
                        self.__imu[id] = self.__calc_magnetic_xyz(payload)
                    elif id == Imu.BRD_GYRO:
                        self.__imu[id] = self.__calc_gyro_xyz(payload)
                    elif id == Imu.BRD_EULER:
                        self.__imu[id] = self.__calc_euler_xyz(payload)
                    elif id == Imu.BRD_QUAT:
                        self.__imu[id] = self.__calc_wxyz(payload)
            if not all(self.__imu.values()):
                return
            else:
                if self.__param:
                    self.__func(tuple(self.__imu.values()),self.__param)
                else:
                    self.__func(tuple(self.__imu.values()))

    def accel(self):
        self.__can.write(Imu.ACT_IMU,[0x02,0x00])
        _,_,payload = self.__can.read(timeout=2.0)
        return self.__calc_accel_xyz(payload)

    def magnetic(self):
        self.__can.write(Imu.ACT_IMU,[0x04,0x00])
        _,_,payload = self.__can.read(timeout=2.0)
        return self.__calc_magnetic_xyz(payload)

    def gyro(self):
        self.__can.write(Imu.ACT_IMU,[0x08,0x00])
        _,_,payload = self.__can.read(timeout=2.0)
        return self.__calc_gyro_xyz(payload)

    def euler(self):
        self.__can.write(Imu.ACT_IMU,[0x10,0x00])
        _,_,payload = self.__can.read(timeout=2.0)
        return self.__calc_euler_xyz(payload)

    def quat(self):
        self.__can.write(Imu.ACT_IMU,[0x40,0x00])
        _,_,payload = self.__can.read(timeout=2.0)
        return self.__calc_wxyz(payload)

    def callback(self,func,repeat=1,param=None):
        if not self.__thread:
            self.__func = func
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__thread.start()
            self.__can.write(Imu.ACT_IMU,[0x1F,repeat&0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(Imu.ACT_IMU,[0x00,0x00])
