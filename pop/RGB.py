from .CAN import Can
import threading


class RGB:
    ACT_RGB = 0x250

    def __init__(self, dev="can0", bitrate=500000):
        self.__can = Can(dev, bitrate)
        self.address = 0x0F

    def __del__(self):
        self.stop()

    def SetLed(self, id):
        assert isinstance(id, tuple) or isinstance(id, int), "[Error] You must use () to control individual LEDs."
        
        if type(id) == int:
            assert 0 < id < 5, "[Error] Value should be between 0 to 5."

            self.address = 1 << (id-1)
        else:
            assert len(set(id)) == len(id), "[Error] Do not put same number."            
            assert len(id) <= 4, "[Error] Do not put more than 4 values in the ()."
            assert all(0 < x < 5 for x in id), "[Error] Value should be between 0 to 5."
        
            self.address = sum(1 << (i - 1) for i in id)

    def On(self, rgb=[255, 255, 255]):            
        self.__can.write(RGB.ACT_RGB, [self.address, rgb[0], rgb[1], rgb[2]])

    def AllOn(self, rgb=[255, 255, 255]):   
        self.__can.write(RGB.ACT_RGB, [0x0F, rgb[0], rgb[1], rgb[2]])
    
    def AllOff(self):
        self.__can.write(RGB.ACT_RGB, [0x0F, 0, 0, 0])

