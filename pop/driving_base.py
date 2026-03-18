from .CAN import Can
import math

class DrivingBase:
    WHEEL_ID = 0x010
    WHEEL_POS = 0x07
    WHEEL_CENTER = 100

    def __init__(self,dev='can0',bitrate=500000):
        self.__angle = 0        
        self.steer = 0
        self.__setting_throttle = False
        self.__spin = False
        self.__can = Can(dev,bitrate) 
        self.__stop()

    def __stop(self):
        self.__throttle = 0
        self.wheel_vec = [DrivingBase.WHEEL_CENTER, DrivingBase.WHEEL_CENTER, DrivingBase.WHEEL_CENTER]

    def __move(self):
        if (self.__angle == 0) or (self.__angle == 180):
            weight = self.throttle * 1.15
        else:
            weight = self.throttle 
          
        if self.__spin:
            self.wheel_vec[0] = DrivingBase.WHEEL_CENTER - self.throttle
            self.wheel_vec[1] = DrivingBase.WHEEL_CENTER - self.throttle
            self.wheel_vec[2] = DrivingBase.WHEEL_CENTER - self.throttle
        else:
            Vx = -1 * math.sin(math.radians(self.__angle)) * weight
            Vy = math.cos(math.radians(self.__angle)) * weight
    
            self.wheel_vec[2] = DrivingBase.WHEEL_CENTER - round(-1 * Vx)
            self.wheel_vec[0] = DrivingBase.WHEEL_CENTER - round((1/2) * Vx + (math.sqrt(3)/2)*Vy)                                
            self.wheel_vec[1] = DrivingBase.WHEEL_CENTER - round((1/2) * Vx - (math.sqrt(3)/2)*Vy)

        self.transfer()
        
    def transfer(self):
        payload = [DrivingBase.WHEEL_POS] + self.wheel_vec
        self.__can.write(DrivingBase.WHEEL_ID, payload)
        
    def move(self, angle, throttle=None):
        if throttle:
            self.__setting_throttle = True
            self.throttle = throttle
            self.__setting_throttle = False
        self.__angle = angle
        self.__spin = False
        self.__move()
        
    def rotate(self, throttle=None):        
        if throttle:
            self.throttle = throttle
            self.__spin = True
        self.__move()
            
    def stop(self):
        self.__stop()
        self.transfer()

    @property
    def throttle(self):
        return self.__throttle

    @throttle.setter
    def throttle(self, throttle):
        self.__throttle = throttle
        
        if not self.__setting_throttle:
            self.__move()

