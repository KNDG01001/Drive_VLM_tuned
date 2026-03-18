from .CAN import Can
import threading

class Battery:  
    ACT_VOLT = 0x0A0
    ACT_TEMP = 0x0A1
    BRD_VOLT = 0x1A0
    BRD_TEMP = 0x1A1

    def __init__(self,dev='can0',bitrate=500000):
        self.__can = Can(dev,bitrate)
        self.__func = None
        self.__param = None
        self.__thread = None 
        self.__stop = False
        self.__battery = {Battery.BRD_VOLT:None,Battery.BRD_TEMP:None}
        for f in self.__battery.keys():
            self.__can.setFilter(f)
            self.__battery[f] = 0

    def __del__(self):
        self.stop()

    def __callback(self):
        while not self.__stop:
            self.__battery = self.__battery.fromkeys(self.__battery.keys(),None)

            while not all(self.__battery.values()) and not self.__stop:
                id,dlc,payload = self.__can.read(timeout=0.1)

                if not payload:
                    continue
                elif id == Battery.BRD_VOLT or id == Battery.BRD_TEMP:
                    self.__battery[id] = (((payload[1]&0x0F)<<8)|payload[0])*0.1

            if not all(self.__battery.values()):
                return
            else:
                if self.__param:
                    self.__func(tuple([round(n,1) for n in self.__battery.values()]),self.__param)
                else:
                    self.__func(tuple([round(n,1) for n in self.__battery.values()]))

    def read(self):
        self.__can.write(Battery.ACT_VOLT,[0x00])
        
        try:
            self.__can.write(Battery.ACT_VOLT,[0x00])
            id,dlc,payload = self.__can.read(timeout=2.0)
            
            if id == Battery.BRD_VOLT:
                self.__battery[id] = (((payload[1]&0x0F)<<8)|payload[0])*0.1

            self.__can.write(Battery.ACT_TEMP,[0x00])
            id,dlc,payload = self.__can.read(timeout=2.0)
            
            if id == Battery.BRD_TEMP:
                self.__battery[id] = (((payload[1]&0x0F)<<8)|payload[0])*0.1

            volt = self.__battery[Battery.BRD_VOLT]
            temp = self.__battery[Battery.BRD_TEMP]

            return round(volt,1),round(temp,1)
        except:
            return None

    def callback(self,func,repeat=1,param=None):
        if not self.__thread:
            self.__func = func 
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__thread.start()
            self.__can.write(Battery.ACT_VOLT,[repeat&0xFF])
            self.__can.write(Battery.ACT_TEMP,[repeat&0xFF])

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None
            self.__can.write(Battery.ACT_VOLT,[0x00])
            self.__can.write(Battery.ACT_TEMP,[0x00])
