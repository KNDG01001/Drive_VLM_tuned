import time,os 
import __main__
from traitlets.config.configurable import SingletonConfigurable

__main__._camera_flip_method = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# JupyterNotebook Checker
def isnotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True
        else:
            return False
    except NameError:
        return False

__main__.isnotebook = isnotebook()

##################################################################

def bgr8_to_jpeg(value):
    global cv2
    import cv2
    return bytes(cv2.imencode('.jpg', value)[1])

class _camera(SingletonConfigurable):
    cap_mode_table = {0:(3264, 2464, 21), 1:(3264, 1848, 28), 2:(1920, 1080, 30), 3:(1280, 720, 60), 4:(1280, 720, 120)}

    import traitlets
    value = traitlets.Any()
    width = traitlets.Integer(default_value=224).tag(config=True)
    height = traitlets.Integer(default_value=224).tag(config=True)
    cap_mode = traitlets.Integer(default_value=0).tag(config=True)

    def __init__(self, *args, **kwargs):
        import os
        global cv2
        global np
        import cv2
        import numpy as np
        import atexit
        
        super(_camera, self).__init__(*args, **kwargs)

        #os.system("echo soda | sudo -S systemctl restart nvargus-daemon")

        capture_width, capture_height, fps = self.cap_mode_table[self.cap_mode]
        gst_str = 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=%d, height=%d, format=(string)NV12, framerate=(fraction)%d/1 ! nvvidconv flip-method=%s ! video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! videoconvert ! appsink' % (capture_width, capture_height, fps, __main__._camera_flip_method, self.width, self.height)

        self.value = np.empty((self.height, self.width, 3), dtype=np.uint8)
        try:
            self.cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

            success, tmp = self.cap.read()
            if not success:
                raise RuntimeError('Could not read image from camera.')

            self.start()
        except:
            raise RuntimeError('Could not initialize camera.  Please see error trace.')

        atexit.register(self.stop)

    def __del__(self):
        self.stop()
        self.cap.release()

    def _capture_frames(self):
        while not self._is_stop :
            success, self.value = self.cap.read()
            if not success:
                raise RuntimeError('Could not read image from camera.')

    def start(self):
        global Thread
        from threading import Thread
        
        if not hasattr(self, '_thread') or not self._thread.isAlive():
            self._is_stop = False
            #self._thread = Thread(target=self._capture_frames,daemon=True)
            self._thread = Thread(target=self._capture_frames)
            self._thread.start()
        
    def stop(self):       
        if hasattr(self, '_thread'):
            self._is_stop = True
            self._thread.join()
            self.value = np.empty((self.height, self.width, 3), dtype=np.uint8)

    def restart(self):
        self.stop()
        self.start()
#----------------------------------------------------------------------------------------#
class IPyCamera:
    code="7377EF6E7F5DC659B18B3A089F8BD812"
    camera=None
    camera_link=None
    image=None
    width=None
    height=None

    def __init__(self, width=224, height=224, cap_mode=0, auto_load=True):
        self.width=width
        self.height=height
        self.cap_mode=cap_mode

        if auto_load:
            self.load()

    def destroy(self):
        self.camera.stop()
        self.camera.cap.release()

    def __call__(self):
        #self.camera_link.link()
        return self.image

    def load(self):
        import os
        import ipywidgets.widgets as widgets
        import traitlets
        
        self.camera = _camera.instance(width=self.width, height=self.height, cap_mode=self.cap_mode)
        self.image = widgets.Image(format='jpeg', width=self.width, height=self.height)
        self.camera_link = traitlets.dlink((self.camera, 'value'), (self.image, 'value'), transform=bgr8_to_jpeg)

    def show(self):
        from IPython.display import display
        import traitlets
        
        if self.camera is None:
            self.load()

        if self.camera_link is None:
            self.camera_link = traitlets.dlink((self.camera, 'value'), (self.image, 'value'), transform=bgr8_to_jpeg)
            display(self.image)
        else:
            #self.camera_link.link()
            display(self.image)

    def stop(self):
        if self.camera_link is not None:
            self.camera_link.unlink()

    @property
    def value(self):
        return self.camera.value
    
class Camera:
    import cv2
    
    code="7377EF6E7F5DC659B18B3A089F8BD812"
    width=None
    height=None
    
    def __init__(self, width=224, height=224, cap_mode=0, auto_load=True): 
        self.width=width
        self.height=height
        self.cap_mode=cap_mode

        if auto_load:
            self._loop = True
            self.load()

    def destroy(self):
        self.camera.stop()
        self.camera.cap.release()

    
    def load(self):        
        self.camera = _camera.instance(width=self.width, height=self.height, cap_mode=self.cap_mode)

    def show(self, frame_data='frame', value=None):
        if self.camera is None:
            self._loop = True
            self.load()
            
        frame_name = frame_data
            
        if value is not None:
            cv2.imshow(frame_name, value)
        else:
            cv2.imshow(frame_name, self.camera.value)            

        if cv2.waitKey(1) & 0xFF == ord('q'):
            self._loop = False
            cv2.destroyAllWindows()
            self.destroy()

    @property
    def value(self):
        return self.camera.value
    
    @property
    def loop(self):
        return self._loop
    
    @loop.setter
    def loop(self, value):
        self._loop = value

try:
    import subprocess as sp
    if '2b03:f780' in str(sp.check_output(['lsusb | grep 2b03'], shell=True)) and '2b03:f781' in str(sp.check_output(['lsusb | grep 2b03'], shell=True)): #Detected ZED Camera
        from .__stereo_camera__  import Stereo_Camera, RESOLUTION, DEPTH_MODE
except: pass

##################################################################
# Audio classes

class Audio:
    def __init__(self, blocking=True, cont=False):
        global pyaudio, wave
        import pyaudio, wave
        self.W = None
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.blocking = blocking
        self.cont = cont
        self.isStop = None

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def stop(self):
        self.isStop = True

    def close(self):
        self.stop()
        time.sleep(.1)

        if self.W != None:
            if type(self.W) is list:
                for w in self.W:
                    w.close()
            else:
                self.W.close()

        if self.stream != None:
            self.stream.stop_stream()
            self.stream.close()
        
        self.p.terminate()

def audio_play(file):
    global wave
    global pyaudio
    import wave
    import pyaudio
    w = wave.open(file, 'rb')
    data = w.readframes(w.getnframes())
    w.close()

    p = pyaudio.PyAudio()
    s = p.open(format=p.get_format_from_width(w.getsampwidth()), channels=w.getnchannels(), 
                      rate=w.getframerate(), output=True)
    s.write(data)
    s.stop_stream()
    s.close()
    p.terminate()

##################################################################
# AudioPlay classes

class AudioPlay(Audio):
    def __init__(self, file, blocking=True, cont=False):
        super().__init__(blocking, cont)

        self.W = wave.open(file, "rb")
        self.stream = self.p.open(format=self.p.get_format_from_width(self.W.getsampwidth()),
            channels=self.W.getnchannels(), rate=self.W.getframerate(), output=True, 
            stream_callback=None if blocking else self._callback)

        if blocking:
            self.data = self.W.readframes(self.W.getnframes())

    def __del__(self):
        super().__del__()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _callback(self, in_data, frame_count, time_info, status):
        data = self.W.readframes(frame_count)
        if self.cont:
            mod = frame_count - len(data) // self.W.getsampwidth()
            if mod != 0:
                self.W.rewind()
                data += self.W.readframes(mod)

        return (data, pyaudio.paContinue if not self.isStop else pyaudio.paAbort)   

    def run(self):
        self.isStop = False
        if self.blocking:
            self.stream.write(self.data)
        else:
            self.stream.start_stream()

    def isPlay(self):
        return self.stream.is_active()

##################################################################
# AudioPlayList classes

class AudioPlayList(Audio):
    def __init__(self, files, blocking=True, cont=False):
        super().__init__(blocking, cont)

        self.W = []
        for file in files:
            self.W.append(wave.open(file, "rb"))

        self.stream = self.p.open(format=self.p.get_format_from_width(self.W[0].getsampwidth()),
            channels=self.W[0].getnchannels(), rate=self.W[0].getframerate(), output=True, 
            stream_callback=None if blocking else self._callback)

        self.data = []
        if blocking:
            for w in self.W:
                self.data.append(w.readframes(w.getnframes()))

    def _callback(self, in_data, frame_count, time_info, status):
        data = self.W[self.pos].readframes(frame_count)
        if self.cont:
            mod = frame_count - len(data) // self.W[self.pos].getsampwidth()
            if mod != 0:
                self.pos += 1
                if self.pos >= len(self.W):
                    self.pos = 0

                self.W[self.pos].rewind()
                data += self.W[self.pos].readframes(mod)

        return (data, pyaudio.paContinue if not self.isStop else pyaudio.paAbort)   

    def run(self, pos=0):
        self.isStop = False
        self.pos = pos

        if self.blocking:
            self.stream.write(self.data[pos])            
        else:
            self.stream.start_stream()
    
    def isPlay(self):
        return self.stream.is_active()

##################################################################
# Audio classes

class AudioRecord(Audio):
    def __init__(self, file, sFormat=8, sChannel=1, sRate=48000, sFramePerBuffer=1024):
        super().__init__(False)

        self.w = wave.open(file, "wb")
        self.w.setsampwidth(self.p.get_sample_size(sFormat))
        self.w.setnchannels(sChannel)
        self.w.setframerate(sRate)

        self.stream = self.p.open(format=sFormat, channels=sChannel, rate=sRate, input=True, 
            frames_per_buffer=sFramePerBuffer, stream_callback=self._callback)

    def __del__(self):
        super().__del__()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _callback(self, in_data, frame_count, time_info, status):
        self.w.writeframes(in_data)
        data = chr(0) * len(in_data)

        return (data, pyaudio.paContinue if not self.isStop else pyaudio.paAbort)   

    def run(self):
        self.stream.start_stream()

class Tone:
    def __init__(self, tempo=100, volume=.5, rate=48000, channels=1): 
        global pyaudio 
        import pyaudio
        self.tempo = tempo
        self.volume = volume
        self.rate = rate
        self.channels = channels
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=self.channels, rate=self.rate, output=True)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.stream.stop_stream()
        self.stream.close() 
        self.p.terminate()

    def setTempo(self, tempo):
        self.tempo = tempo

    def rest(self, duration):
        self.play(0, "REST", 1/4)

    def play(self, octave, pitch, duration):
        global np 
        import numpy as np
        """
        octave = 1 ~ 8
        note = DO, RE, MI, FA, SOL, RA, SI
        dulation = 1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, ...
        """
        string_to_pitch = {"REST":0, "DO":1, "DO#":2, "RE":3, "RE#":4, "MI":5, "FA":6, "FA#":7, "SOL":8, "SOL#":9, "RA":10, "RA#":11, "SI":12}

        p = string_to_pitch[pitch]
        f = 2**(octave) * 55 * 2**((p - 10) / 12)
        
        if p == 0:
            time.sleep((60.0 / self.tempo) * (duration * 4))
        else:
            sample = (np.sin(2 * np.pi * np.arange(self.rate * (60.0 / self.tempo * 4) * (duration*4)) * f / self.rate)).astype(np.float32)
            self.stream.write(self.volume * sample)

            time.sleep(0.02)

##################################################################
# SoundMeter classes

class SoundMeter:
    global pyaudio 
    import pyaudio 
    def __init__(self, sampleFormat=pyaudio.paInt16, channelNums=1, framesPerBuffer=1024, sampleRate=48000):
        self.func = None
        self.args = None
        self.isStop = False

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=sampleFormat, channels=channelNums, rate=sampleRate, input=True, 
                                  frames_per_buffer=framesPerBuffer, stream_callback=self._callback)
    
    def __del__(self):
        self.stop()

    def setCallback(self, func, *args):
        self.func = func
        self.args = args
        self.stream.start_stream()

    def stop(self):
        self.isStop = True
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def _callback(self, inData, frameCount, timeInfo, status):
        import audioop
        rms = audioop.rms(inData, 2)
        self.func(rms, inData, *self.args)

        data = chr(0) * len(inData)
        return (data, pyaudio.paContinue if not self.isStop else pyaudio.paAbort)
