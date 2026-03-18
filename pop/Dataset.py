from ipywidgets import widgets
from IPython.display import display, Audio
import pyaudio
import wave, time, os
import cv2, math, random, traitlets
import numpy as np
from threading import Thread
from abc import *
from shutil import copyfile
from .__init__ import IPyCamera


def Collector(name=None):
    module=None

    if name is None:
        print("Keyward 'name' is requred.\n")
        print("[List]")
        print("Audio : Collect audio datasets as wav file.")
        #print("Camera : Collect picture datasets as jpg file through the camera.")
        return
    elif name.lower() == "audio" or type(name) is _Audio_Collector:
        module = _Audio_Collector()
    else:
        print("Keyward 'name' is wrong.\n")
        print("[List]")
        print("Audio : Collect audio datasets as wav file.")
        #print("Camera : Collect picture datasets as jpg file through the camera.")
        return

    module.show()

class _Audio_Collector:
    def __init__(self, sample_rate=8000):
        self.RATE=sample_rate

        self.rec_btn=widgets.Button(
            description='REC',
            disabled=False,
            button_style='danger',
            tooltip='Record',
            icon='circle',
            layout={'width':'fit-content'}
        )

        self.rec_dur=widgets.BoundedFloatText(
            value=1.0,
            min=0,
            max=60,
            step=0.5,
            description='Duration (sec)',
            disabled=False
        )

        self.rec_prog=widgets.FloatProgress(
            value=1,
            min=0,
            max=1.0,
            step=0.1,
            description='Time',
            bar_style='warning',
            orientation='horizontal'
        )

        self.rec_lab=widgets.Label(value="Ready to record.")

        self.rec_out = widgets.Output(layout={'margin': '10px'})

        self.rec_so_btn=widgets.ToggleButton(
            value=False,
            description='',
            disabled=False,
            button_style='primary',
            tooltip='Save',
            icon='caret-down'
        )

        self.rec_save_out = widgets.Output(layout={'padding':'1em','width':'fit-content','height':'fit-content','border': 'solid 1px #AAA'})

        self.rec_save_path = widgets.Text(
            placeholder='path of datasets',
            value="./audio_dataset",
            description='Path',
            disabled=False
        )

        self.rec_save_lab = widgets.BoundedIntText(
            value=0,
            min=0,
            max=99999999,
            step=1,
            description='Label',
            disabled=False
        )

        self.rec_save_name = widgets.Text(
            placeholder='identifier',
            value="identifier",
            description='Name',
            disabled=False
        )

        self.rec_save_btn=widgets.Button(
            description='Save',
            disabled=False,
            button_style='success',
            tooltip='Save',
            icon='floppy-o',
            layout={'width':'99%'}
        )

        self.rec_save_noti=widgets.Label(value="")

        self.rec_btn.on_click(self._rec_clk)
        self.rec_so_btn.observe(self._so_clk, 'value')
        self.rec_save_btn.on_click(self._save_clk)

        with self.rec_save_out:
            display(self.rec_save_path)
            display(self.rec_save_lab)
            display(self.rec_save_name)
            display(self.rec_save_btn)
            display(self.rec_save_noti)

        with self.rec_out:
            display(Audio([1],rate=self.RATE))

    def _rec(self, duration, CHUNK):
        paud_obj = pyaudio.PyAudio()
        
        wave_obj = wave.open("./._tmp.wav", "w")
        wave_obj.setnchannels(1)
        wave_obj.setframerate(self.RATE)

        stream_obj = paud_obj.open(format=pyaudio.paInt16, channels=1, rate=self.RATE, input=True, frames_per_buffer=CHUNK)
        wave_obj.setsampwidth(paud_obj.get_sample_size(pyaudio.paInt16))

        for _ in range(round(self.RATE / CHUNK * duration)):
            wave_obj.writeframes(stream_obj.read(CHUNK))

        wave_obj.close()
        
        stream_obj.stop_stream()
        stream_obj.close()
        paud_obj.terminate()

    def _rec_clk(self, obj):
        if self.rec_dur.value>=0.1:
            self.rec_prog.bar_style="warning"
            self.rec_out.clear_output(wait=True)
            CHUNK = 128
            RATE = self.RATE
            
            obj.disabled=True
            self.rec_lab.value="Record after 1s."

            dtime=time.time()
            ptime=0
            lesstime=time.time()-dtime
            while lesstime<1.:
                if time.time()-ptime>=0.1:
                    self.rec_prog.value=1-lesstime
                    ptime=time.time()
                lesstime=time.time()-dtime

            self.rec_prog.bar_style="success"
            self.rec_prog.value=0
            self.rec_lab.value="Recording now..."
            obj.button_style='success'
            obj.description="REC..."
            obj.icon='square'

            rec_thread = Thread(target=self._rec, args=(self.rec_dur.value, CHUNK))
            rec_thread.start()
            
            dtime=time.time()
            ptime=0
            lesstime=time.time()-dtime
            while lesstime<self.rec_dur.value:
                if time.time()-ptime>=0.1:
                    self.rec_prog.value=lesstime/self.rec_dur.value
                    ptime=time.time()
                lesstime=time.time()-dtime

            if rec_thread.is_alive():
                rec_thread.join()

            self.rec_prog.value=1.0
            time.sleep(0.1)

            with self.rec_out:
                if os.path.exists("./._tmp.wav"):
                    display(Audio(filename="./._tmp.wav"))
                else:                   
                    display(Audio([1],rate=self.RATE))
                
            obj.disabled=False
            obj.button_style='danger'
            obj.description="REC"
            obj.icon='circle'
            self.rec_lab.value="Ready to record."
            self.rec_prog.value=1.0
            self.rec_prog.bar_style="warning"
        else:
            self.rec_lab.value="Set the duration at least 0.1 sec."

    def _so_clk(self, evt):
        if evt['new'] :
            evt['owner'].icon='caret-up'
            
            self.rec_save_out.clear_output()
            with self.rec_save_out:
                display(self.rec_save_lab)
                display(self.rec_save_name)
                display(self.rec_save_btn)
        else:
            evt['owner'].icon='caret-down'
            self.rec_save_out.clear_output()
            
    def _save_clk(self, obj):
        try:
            if not os.path.exists(self.rec_save_path.value):
                os.mkdir(self.rec_save_path.value)
                
            label = self.rec_save_lab.value
            name = self.rec_save_name.value
            timestamp=time.strftime('%y%m%d%H%M%S', time.localtime(time.time()))+str(int(time.time()*100%100))
            
            filestr = str(label)+"_"+str(name)+"_"+str(timestamp)+".wav"
            
            if os.path.exists("./._tmp.wav"):
                copyfile("./._tmp.wav", self.rec_save_path.value+"/"+filestr)
                self.rec_save_noti.value="Saved."
            else:
                self.rec_save_noti.value="Doesn't exist a recorded."
        except Exception as e:
            if e.errno == 2:
                self.rec_save_noti.value="No such file or directory."
            else:
                self.rec_save_noti.value="An error occured."

    def show(self):
        display(widgets.HBox([
                    widgets.VBox([
                    widgets.HBox([self.rec_prog, self.rec_lab]),
                    widgets.HBox([self.rec_dur, self.rec_btn]),
                    self.rec_out],layout={'padding':'1em','width':'fit-content','height':'fit-content','border': 'solid 1px #AAA'}),
    
                    self.rec_save_out
                    ]))

class joystick(object):
    server=None
    value={"x":0,"y":0}
    server_thread=None
    port=8885
    js=None
    id=format(int(random.uniform(0.5,1.5)*time.time()*(10**7)),'X')

    def handler(self, websocket, data):
        sep, x, y=data.split(",")
        self.value={"sep":sep, "x":float(x),"y":float(y)}
        
        if self.callback is not None:
            self.callback(self.value)
                
    def _serve(self):
        for _ in range(100):
            try:
                # self.js=HTML('<style>.joystick_focused{ cursor:grabbing !important;}    .joystick_background{user-select: none;        background: #fff3f3;        border: 1px solid #ffa29e;        border-radius: 50%;        height: 12em;        width: 12em;    margin:2.5em;}    .joystick_stick{cursor:grab; user-select: none;        background: #F74138;        border-radius: 50%;        box-shadow: 0.375em 0.375em 0 0 rgba(15, 28, 63, 0.125);        height: 5em;        width: 5em;        transform: translate(50%,50%);    }</style><div><div id="joystick_background_'+self.id+'" class="joystick_background">    <div id="joystick_stick_'+self.id+'" class="joystick_stick" style="position:absolute" onmousedown="start_joystick_'+self.id+'(this); joystick_focus_'+self.id+'(this);" ondrag="joystick_'+self.id+'(e)" onmouseup="reset_joystick_'+self.id+'(this); joystick_disfocus_'+self.id+'(this);"></div></div></div><script> X=0; Y=0; function joystick_focus_'+self.id+'(e){ e.classList.add("joystick_focused");} function joystick_disfocus_'+self.id+'(e){ e.classList.remove("joystick_focused");}    var port_'+self.id+'='+str(self.port)+';    var sock_'+self.id+'=new WebSocket("ws://"+window.location.hostname+":"+port_'+self.id+');    var sw_'+self.id+'=false;    var preX_'+self.id+', preY_'+self.id+', X_'+self.id+', Y_'+self.id+', nX_'+self.id+', nY_'+self.id+';    var back_'+self.id+'=document.getElementById("joystick_background_'+self.id+'");    var stick_'+self.id+'=document.getElementById("joystick_stick_'+self.id+'");    var back_width_'+self.id+'=back_'+self.id+'.offsetWidth;    var back_height_'+self.id+'=back_'+self.id+'.offsetHeight;    var stick_width_'+self.id+'=stick_'+self.id+'.offsetWidth;    var stick_height_'+self.id+'=stick_'+self.id+'.offsetHeight;  intlog_'+self.id+'=Date.now();  setInterval(()=>{try{if (parseFloat(sX_'+self.id+')==0 && parseFloat(sY_'+self.id+')==0) {if (Date.now()-intlog_'+self.id+'<500) sock_'+self.id+'.send("j," + sX_'+self.id+' + "," + sY_'+self.id+');}else{ sock_'+self.id+'.send("j," + sX_'+self.id+' + "," + sY_'+self.id+'); intlog_'+self.id+'=Date.now();}}catch{console.log("Waiting to connect...");}},50); function move_'+self.id+'(evt){        X=evt.clientX;        Y=evt.clientY;        if(sw_'+self.id+'){            nX_'+self.id+'+=X-preX_'+self.id+';            nY_'+self.id+'+=Y-preY_'+self.id+';            preX_'+self.id+'=X;            preY_'+self.id+'=Y;            if (nX_'+self.id+'>back_width_'+self.id+'-stick_width_'+self.id+'/2) nX_'+self.id+'=back_width_'+self.id+'-stick_width_'+self.id+'/2;            else if (nX_'+self.id+'<-stick_width_'+self.id+'/2) nX_'+self.id+'=-stick_width_'+self.id+'/2;            if (nY_'+self.id+'>back_height_'+self.id+'-stick_height_'+self.id+'/2) nY_'+self.id+'=back_height_'+self.id+'-stick_height_'+self.id+'/2;            else if (nY_'+self.id+'<-stick_height_'+self.id+'/2) nY_'+self.id+'=-stick_height_'+self.id+'/2;            sX_'+self.id+'=(nX_'+self.id+'+stick_width_'+self.id+'/2-back_width_'+self.id+'/2)/(back_width_'+self.id+'/2);            sY_'+self.id+'=-(nY_'+self.id+'+stick_height_'+self.id+'/2-back_height_'+self.id+'/2)/(back_height_'+self.id+'/2);                        /*sock_'+self.id+'.send("j,"+sX_'+self.id+'+","+sY_'+self.id+');*/            stick_'+self.id+'.style.transform="translate("+nX_'+self.id+'+"px,"+nY_'+self.id+'+"px)";        }    };    function up_'+self.id+'(){joystick_disfocus_'+self.id+'(stick_'+self.id+');        if(sw_'+self.id+'){            sw_'+self.id+'=false;            reset_joystick_'+self.id+'(stick_'+self.id+');        }    };    function start_joystick_'+self.id+'(e){window.onmousemove=move_'+self.id+'; window.onmouseup=up_'+self.id+';        preX_'+self.id+'=X;        preY_'+self.id+'=Y;        sw_'+self.id+'=true;    }    function joystick_'+self.id+'(e){        nX_'+self.id+'+=X-preX_'+self.id+';        nY_'+self.id+'+=Y-preY_'+self.id+';        preX_'+self.id+'=X;        preY_'+self.id+'=Y;        if (nX_'+self.id+'>back_width_'+self.id+'-stick_width_'+self.id+'/2) nX_'+self.id+'=back_width_'+self.id+'-stick_width_'+self.id+'/2;        else if (nX_'+self.id+'<-stick_width_'+self.id+'/2) nX_'+self.id+'=-stick_width_'+self.id+'/2;        if (nY_'+self.id+'>back_height_'+self.id+'-stick_height_'+self.id+'/2) nY_'+self.id+'=back_height_'+self.id+'-stick_height_'+self.id+'/2;        else if (nY_'+self.id+'<-stick_height_'+self.id+'/2) nY_'+self.id+'=-stick_height_'+self.id+'/2;                e.style.transform="translate("+nX_'+self.id+'+"px,"+nY_'+self.id+'+"px)";    }    function reset_joystick_'+self.id+'(e){        sw_'+self.id+'=false;        nX_'+self.id+' = back_width_'+self.id+'/2 - stick_width_'+self.id+'/2;        nY_'+self.id+' = back_height_'+self.id+'/2 - stick_height_'+self.id+'/2;        e.style.transform="translate("+nX_'+self.id+'+"px,"+nY_'+self.id+'+"px)"; sX_'+self.id+'="0"; sY_'+self.id+'="0"; sock_'+self.id+'.send("j,0,0");    }    reset_joystick_'+self.id+'(stick_'+self.id+'); console.log("Loaded.");</script>')
                self.js=HTML('<style>.joystick_focused{ cursor:grabbing !important;}    .joystick_background{user-select: none;        background: #fff3f3;        border: 1px solid #ffa29e;        border-radius: 50%;        height: 12em;        width: 12em;    margin:2.5em;}    .joystick_stick{cursor:grab; user-select: none;        background: #F74138;        border-radius: 50%;        box-shadow: 0.375em 0.375em 0 0 rgba(15, 28, 63, 0.125);        height: 5em;        width: 5em;        transform: translate(50%,50%);    }</style><div><div id="joystick_background_'+self.id+'" class="joystick_background">    <div id="joystick_stick_'+self.id+'" class="joystick_stick" style="position:absolute" onmousedown="start_joystick_'+self.id+'(this); joystick_focus_'+self.id+'(this);" ondrag="joystick_'+self.id+'(e);" onmouseup="reset_joystick_'+self.id+'(this); joystick_disfocus_'+self.id+'(this);" ontouchstart="onTouchStart(event);" ontouchmove="onTouchMove(event);" ontouchend="onTouchEnd(event);"></div></div></div><script> X=0; Y=0; function joystick_focus_'+self.id+'(e){ e.classList.add("joystick_focused");} function joystick_disfocus_'+self.id+'(e){ e.classList.remove("joystick_focused");}    var port_'+self.id+'='+str(self.port)+';    var sock_'+self.id+'=new WebSocket("ws://"+window.location.hostname+":"+port_'+self.id+');    var sw_'+self.id+'=false;    var preX_'+self.id+', preY_'+self.id+', X_'+self.id+', Y_'+self.id+', nX_'+self.id+', nY_'+self.id+';    var back_'+self.id+'=document.getElementById("joystick_background_'+self.id+'");    var stick_'+self.id+'=document.getElementById("joystick_stick_'+self.id+'");    var back_width_'+self.id+'=back_'+self.id+'.offsetWidth;    var back_height_'+self.id+'=back_'+self.id+'.offsetHeight;    var stick_width_'+self.id+'=stick_'+self.id+'.offsetWidth;    var stick_height_'+self.id+'=stick_'+self.id+'.offsetHeight;  intlog_'+self.id+'=Date.now(); var pressed = 0; var fpressed = 0; setInterval(()=>{try{if (parseFloat(sX_'+self.id+')==0 && parseFloat(sY_'+self.id+')==0) {if (Date.now()-intlog_'+self.id+'<500) sock_'+self.id+'.send("j," + sX_'+self.id+' + "," + sY_'+self.id+');}else{ sock_'+self.id+'.send("j," + sX_'+self.id+' + "," + sY_'+self.id+'); intlog_'+self.id+'=Date.now();}}catch{console.log("Waiting to connect...");}},50); function move_'+self.id+'(evt){ X=evt.clientX; Y=evt.clientY; if(sw_'+self.id+'){            nX_'+self.id+'+=X-preX_'+self.id+';            nY_'+self.id+'+=Y-preY_'+self.id+';            preX_'+self.id+'=X;            preY_'+self.id+'=Y;            if (nX_'+self.id+'>back_width_'+self.id+'-stick_width_'+self.id+'/2) nX_'+self.id+'=back_width_'+self.id+'-stick_width_'+self.id+'/2;            else if (nX_'+self.id+'<-stick_width_'+self.id+'/2) nX_'+self.id+'=-stick_width_'+self.id+'/2;            if (nY_'+self.id+'>back_height_'+self.id+'-stick_height_'+self.id+'/2) nY_'+self.id+'=back_height_'+self.id+'-stick_height_'+self.id+'/2;            else if (nY_'+self.id+'<-stick_height_'+self.id+'/2) nY_'+self.id+'=-stick_height_'+self.id+'/2;            sX_'+self.id+'=(nX_'+self.id+'+stick_width_'+self.id+'/2-back_width_'+self.id+'/2)/(back_width_'+self.id+'/2);            sY_'+self.id+'=-(nY_'+self.id+'+stick_height_'+self.id+'/2-back_height_'+self.id+'/2)/(back_height_'+self.id+'/2);                        /*sock_'+self.id+'.send("j,"+sX_'+self.id+'+","+sY_'+self.id+');*/            stick_'+self.id+'.style.transform="translate("+nX_'+self.id+'+"px,"+nY_'+self.id+'+"px)";        }    };    function up_'+self.id+'(){joystick_disfocus_'+self.id+'(stick_'+self.id+');        if(sw_'+self.id+'){            sw_'+self.id+'=false;            reset_joystick_'+self.id+'(stick_'+self.id+');        }    };    function start_joystick_'+self.id+'(e){window.onmousemove=move_'+self.id+'; window.onmouseup=up_'+self.id+';        preX_'+self.id+'=X;        preY_'+self.id+'=Y;        sw_'+self.id+'=true;    }    function joystick_'+self.id+'(e){        nX_'+self.id+'+=X-preX_'+self.id+';        nY_'+self.id+'+=Y-preY_'+self.id+';        preX_'+self.id+'=X;        preY_'+self.id+'=Y;        if (nX_'+self.id+'>back_width_'+self.id+'-stick_width_'+self.id+'/2) nX_'+self.id+'=back_width_'+self.id+'-stick_width_'+self.id+'/2;        else if (nX_'+self.id+'<-stick_width_'+self.id+'/2) nX_'+self.id+'=-stick_width_'+self.id+'/2;        if (nY_'+self.id+'>back_height_'+self.id+'-stick_height_'+self.id+'/2) nY_'+self.id+'=back_height_'+self.id+'-stick_height_'+self.id+'/2;        else if (nY_'+self.id+'<-stick_height_'+self.id+'/2) nY_'+self.id+'=-stick_height_'+self.id+'/2;                e.style.transform="translate("+nX_'+self.id+'+"px,"+nY_'+self.id+'+"px)";    }    function reset_joystick_'+self.id+'(e){        sw_'+self.id+'=false;        nX_'+self.id+' = back_width_'+self.id+'/2 - stick_width_'+self.id+'/2;        nY_'+self.id+' = back_height_'+self.id+'/2 - stick_height_'+self.id+'/2;        e.style.transform="translate("+nX_'+self.id+'+"px,"+nY_'+self.id+'+"px)"; sX_'+self.id+'="0"; sY_'+self.id+'="0"; sock_'+self.id+'.send("j,0,0");    } function onTouchStart(event){pressed = 1; preX_'+self.id+' = X; preY_'+self.id+' = Y; sw_'+self.id+' = true; } function onTouchMove(event){event.preventDefault(); if (pressed === 1){X = event.targetTouches[0].pageX; Y = event.targetTouches[0].pageY; if (sw_'+self.id+'){nX_'+self.id+' += X - preX_'+self.id+'; nY_'+self.id+' += Y - preY_'+self.id+'; preX_'+self.id+' = X; preY_'+self.id+' = Y; if (fpressed === 0){fpressed = 1, nX_'+self.id+' = 50; nY_'+self.id+' = 50;} else if(fpressed === 1){ if (nX_'+self.id+' > back_width_'+self.id+' - stick_width_'+self.id+' / 2) nX_'+self.id+' = back_width_'+self.id+' - stick_width_'+self.id+' / 2; else if (nX_'+self.id+' < -stick_width_'+self.id+' / 2) nX_'+self.id+' = -stick_width_'+self.id+' / 2; if (nY_'+self.id+' > back_height_'+self.id+' - stick_height_'+self.id+' / 2) nY_'+self.id+' = back_height_'+self.id+' - stick_height_'+self.id+' / 2; else if (nY_'+self.id+' < -stick_height_'+self.id+' / 2) nY_'+self.id+' = -stick_height_'+self.id+' / 2;} sX_'+self.id+' = (nX_'+self.id+' + stick_width_'+self.id+' / 2 - back_width_'+self.id+' / 2) /(back_width_'+self.id+'/2); sY_'+self.id+' = -(nY_'+self.id+' + stick_height_'+self.id+' / 2 - back_height_'+self.id+' / 2) /(back_height_'+self.id+'/2); stick_'+self.id+'.style.transform = "translate(" + nX_'+self.id+' + "px," + nY_'+self.id+' + "px)"; }}} function onTouchEnd(event){ if (pressed ===1) {pressed = 0; fpressed = 0; joystick_disfocus_'+self.id+'(stick_'+self.id+'); if (sw_'+self.id+'){ sw_'+self.id+' = false; reset_joystick_'+self.id+'(stick_'+self.id+'); }}} reset_joystick_'+self.id+'(stick_'+self.id+'); console.log("Loaded.");</script>')
                self.server = WebSocketServer("0.0.0.0", self.port, on_data_receive=self.handler)
                self.server.serve_forever()
            except Exception as e:
                if e.errno==98:
                    self.port+=1
                    continue
                else:
                    print(e)
                    del self
                    break
            else:
                break

    def __init__(self, callback=None):
        self.callback=callback

        global WebSocketServer, HTML, display, Thread
        from websock import WebSocketServer
        from IPython.display import HTML, display
        from threading import Thread

        self.server_thread=Thread(target=self._serve)
        self.server_thread.daemon=True
        self.server_thread.start()

    def __call__(self):
        return self.js

    def show(self):
        display(self.js)

class _cam_based_class:
    _camera=None

    def __init__(self, camera=None):
        if hasattr(camera,'code') and camera.code==IPyCamera.code:
            self._camera=camera
        else:
            print('This Camera class is not available.')
            del self
    @property
    def camera(self):
        return self._camera
    
    @camera.setter
    def camera(self,camera):
        if type(camera)==Camera:
            self._camera=camera
        else:
            print('Not available class.')

def bgr8_to_jpeg(value):
    return bytes(cv2.imencode('.jpg', value)[1])

class Collision_Avoid:
    pass
class Track_Follow:
    pass

class Image_Collector(_cam_based_class):
    blocked_dir = 'collision_dataset/blocked'
    free_dir = 'collision_dataset/free'
    track_dir = 'track_dataset/'
    separator=None
    free_button=None
    blocked_button=None
    free_count=None
    blocked_count=None
    joystick=None
    image=None
    imageWidget=None
    cameraWidget=None
    toggleWidget=None
    max_speed=60
    min_speed=20
    fps=5
    last_cp=0
    is_ready=False
    jsave=False

    def __init__(self, separator, camera=None, auto_ready=True, save_per_sec=5):
        from .driving import Driving
        self.drv = Driving()
        
        if camera is not None:
            super().__init__(camera)

        self.fps=save_per_sec

        if "Collision_Avoid" in str(separator):
            self.separator="Collision_Avoid"
        elif "Track_Follow" in str(separator):
            self.separator="Track_Follow"
        else:
            print('Not available class. Please input a Collision_Avoid class or Track_Follow class in the 2nd parameter.')
            del self
            
        if auto_ready:
            self.ready()

    def __call__(self):
        self.show()

    def __del__(self):
        if self.joystick is not None:
            del self.joystick

    def _joystick_save_onclick(self, e):
        if e['new']:
            e.owner.button_style='success'
            self.jsave=True
        else:
            e.owner.button_style='danger'
            self.jsave=False

    ''' only for Collision_Avoid '''
    def save_snapshot(self,directory):
        ctime=time.strftime('%Y-%m-%d %H:%M:%S.', time.localtime(time.time()))+str(int(time.time()*100%100))
        image_path = os.path.join(directory, ctime + '.jpg')
        with open(image_path, 'wb') as f:
            f.write(self.camera.image.value)

    def save_free(self):
        self.save_snapshot(self.free_dir)
        self.free_count.value = len(os.listdir(self.free_dir))
        
    def save_blocked(self):
        self.save_snapshot(self.blocked_dir)
        self.blocked_count.value = len(os.listdir(self.blocked_dir))

    def control_as_joystick(self, value):
        if value['sep'] == "j":
            self.drv.steering=value['x']
            speed=value['y']*(self.max_speed-self.min_speed)

            if speed>0:
                self.drv.speed = speed+self.min_speed
            elif speed<0:
                self.drv.speed = -(-speed+self.min_speed)
            else:
                self.drv.stop()
    ''' only for Collision_Avoid '''

    _y_scale=1/3
    
    ''' only for Track_Follow '''
    def save_as_joystick(self, value):
        self.image=self.camera.value
        tmp_img=bgr8_to_jpeg(self.image)
        x=(value['x']+1)/2*300
        y=(value['y']+1)/2*300
        
        if value['sep'] == "j":
            y=((value['y']+1)*self._y_scale)/2*self.camera.height
            y=self.camera.height*self._y_scale*2-y
        
            self.drv.steering=value['x']
            speed=value['y']*(self.max_speed-self.min_speed)

            if speed>0:
                self.drv.speed = speed+self.min_speed
            elif speed<0:
                self.drv.speed = -(-speed+self.min_speed)
            else:
                self.drv.stop()
            
        if self.jsave or value['sep'] == "c":
            if time.time()-self.last_cp >= 1/self.fps:
                cv2.circle(self.image, (int(x), int(y)), 6, (0, 255, 0), 2)
                self.imageWidget.value=bgr8_to_jpeg(self.image)
                ctime=time.strftime('%Y-%m-%d %H:%M:%S.', time.localtime(time.time()))+str(int(time.time()*100000%100000))
                image_path = os.path.join(self.track_dir, str(int(x))+"_"+str(int(y))+"_"+ctime + '.jpg')
                image_pathorg = os.path.join(self.track_dir, str(int(x))+"org_"+str(int(y))+"_"+ctime + '.jpg')
                with open(image_path, 'wb') as f:
                    f.write(tmp_img)
                # with open(image_pathorg, 'wb') as f:
                #     f.write(tmp_org)

    ''' only for Track_Follow '''


    def ready(self):
        if self.separator=="Collision_Avoid":
            try:
                os.makedirs(self.free_dir)
                os.makedirs(self.blocked_dir)
            except FileExistsError:
                try:                    
                    os.rmdir(self.blocked_dir+'/.ipynb_checkpoints')
                except:
                    pass
                try:                    
                    os.rmdir(self.free_dir+'/.ipynb_checkpoints')
                except:
                    pass    
                
            button_layout = widgets.Layout(width='128px', height='64px')
            self.free_button = widgets.Button(description='add free', button_style='success', layout=button_layout)
            self.blocked_button = widgets.Button(description='add blocked', button_style='danger', layout=button_layout)
            self.free_count = widgets.IntText(layout=button_layout, value=len(os.listdir(self.free_dir)))
            self.blocked_count = widgets.IntText(layout=button_layout, value=len(os.listdir(self.blocked_dir)))
            self.free_button.on_click(lambda x: self.save_free())
            self.blocked_button.on_click(lambda x: self.save_blocked())
            self.joystick=joystick(callback=self.control_as_joystick)
        elif self.separator=="Track_Follow":
            try:
                os.makedirs(self.track_dir)
            except FileExistsError:
                pass

            self.imageWidget=widgets.Image(format='jpeg', width=self.camera.width, height=self.camera.height)
            self.cameraWidget=widgets.Image(format='jpeg', width=self.camera.width, height=self.camera.height)
            self.cameraWidget.add_class("clickable_image_box")
            self.camera_link = traitlets.dlink((self.camera.image, 'value'), (self.cameraWidget, 'value'))
            self.toggleWidget=widgets.ToggleButton(
                value=False,
                description='Auto Collect',
                disabled=False,
                tooltip='Automatically collects datasets during joystick control.',
                button_style='danger'
            )
            self.toggleWidget.observe(self._joystick_save_onclick,'value')
            self.joystick=joystick(callback=self.save_as_joystick)
        

        self.is_ready=True

    def show(self):
        if self.camera is None:
            print('Please set camera class.')
            return

        if not self.is_ready:
            self.ready()

        if self.separator=="Collision_Avoid":
            self.camera.show()
            display(widgets.HBox([self.free_count, self.free_button]))
            display(widgets.HBox([self.blocked_count, self.blocked_button]))
            display(self.joystick())
        elif self.separator=="Track_Follow":
            self.imageWidget.value=bgr8_to_jpeg(self.camera.value)
            display(widgets.HBox([self.cameraWidget, self.imageWidget]))
            display(self.toggleWidget)
            display(self.joystick())
            display(HTML('<script>var list=document.getElementsByClassName("clickable_image_box");for (var i=0; i<list.length; i++) {    list[i].onclick=function(e){		var x=e.offsetX/150-1;		var y=e.offsetY/150-1;		sock_'+self.joystick.id+'.send("c,"+x+","+y);	};}</script>'))
