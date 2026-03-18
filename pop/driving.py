from .driving_base import DrivingBase

class Driving(DrivingBase):
    ACT_PID = 0x012
    PID_ON = 0xFF
    PID_OFF = 0x00 

    def __init__(self, dev='can0', bitrate=500000):
        super().__init__(dev, bitrate)
        self.__pid = False
        self.steering = 0.0 

    def forward(self, throttle=None):        
        self.move(0,throttle)

    def backward(self,throttle=None):
        self.move(180,throttle)
        
    def spin(self,throttle=None):
        self.rotate(throttle)        

    @property
    def steering(self):
        return((self.wheel_vec[2] - DrivingBase.WHEEL_CENTER)/100) * -1

    @steering.setter
    def steering(self, r):
        assert(-1.0 <= r <= 1.0)
        self.steer = r
        self.wheel_vec[2] = (DrivingBase.WHEEL_CENTER + round(r * 100) * -1)
        self.transfer()

    @property
    def pid(self):
        return self.__pid

    @pid.setter
    def pid(self, on):
        self.__pid = on
        self.__can.write(Driving.ACT_PID, Driving.PID_ON if self.__pid else Driving.PID_OFF)