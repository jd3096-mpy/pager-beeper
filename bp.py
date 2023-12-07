import time
from machine import Pin,SPI,PWM
import neopixel
from st7567 import ST7567
from robust import MQTTClient
import _thread
import framebuf

class BP():
    def __init__(self):
        self.fb_sound=framebuf.FrameBuffer(bytearray(b'\x06\nrBBr\n\x06'),8,8,framebuf.MONO_HMSB)
        self.fb_signal=framebuf.FrameBuffer(bytearray(b'\x7fI*\x1c\x08\x08\x08\x08'),8,8,framebuf.MONO_HMSB)
        self.fb_hr=framebuf.FrameBuffer(bytearray(b'@wTT\x00\x00\x00\x00'),8,8,framebuf.MONO_HMSB)
        self.fb_24=framebuf.FrameBuffer(bytearray(b"e\x15\'Aq\x00\x00\x00"),8,8,framebuf.MONO_HMSB)
        self.SSID='dundundun'
        self.PWD='30963096'
        self.MQTT_NAME='jdesp32'
        self.SERVER="42.193.120.65"
        self.USER='jd3096'
        self.PASSWORD='jd3096'
        self.PORT=1883
        
        self.bl=PWM(Pin(10))
        self.bl.freq(500)
        self.bl.duty(1000)
        self.rgb = neopixel.NeoPixel(Pin(1), 1)
        self.rgb[0] = (6, 6, 6)
        self.rgb.write()
        spi = SPI(1, 20000000, sck=Pin(9), mosi=Pin(8),miso=Pin(21))
        self.screen = ST7567(128, 32, spi,dc=Pin(7),cs=Pin(5),res=Pin(6))
        self.screen.font_load("GB2312-16.fon")
        self.screen.font_set(0x22,0,1,0)
        self.screen_init()
        
    def screen_init(self):
        self.screen.font_load("GB2312-16.fon")
        self.screen.font_set(0x22,0,1,0)
        self.screen.fill(0)
        self.screen.text("老李MQTT BP机",12,0,1)

        self.screen.font_set(0x0,0,1,0)
        current_time = time.localtime()

        formatted_time = "{:02d}:{:02d}     {:02d}/{:02d}/{:02d}".format(
            current_time[3],  # 小时
            current_time[4],  # 分钟
            current_time[2],  # 日
            current_time[1],  # 月
            current_time[0] % 100  # 年的最后两位
        )
        self.screen.text(formatted_time,15,25,1)

        for i in range(5):
            self.screen.blit(self.fb_signal,18+i*22,17)

        self.screen.blit(self.fb_sound,1,24)
        self.screen.blit(self.fb_24,48,24)
        self.screen.blit(self.fb_hr,56,24)

        self.screen.show()
        
    def wifi(self):
        import network
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        self.screen.font_load("GB2312-16.fon")
        self.screen.font_set(0x22,0,1,0)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(self.SSID, self.PWD)
            self.screen.fill(0)
            self.screen.text("WIFI连接中...",15,0,1)
            self.screen.show()
            while not wlan.isconnected():
                for i in range(15):
                    self.screen.fill(0)
                    self.screen.text("WIFI连接中...",15,0,1)
                    self.screen.text(str(15-i),50,16,1)
                    self.screen.show()
                    time.sleep(1)
                    if wlan.isconnected():
                        break
        if wlan.isconnected():
            print('network config:', wlan.ifconfig())
            self.screen.fill(0)
            self.screen.text("WIFI已连接",26,0,1)
            self.screen.font_set(0x0,0,1,0)
            self.screen.text(wlan.ifconfig()[0],22,24,1)
            self.screen.show()
            self.rgb[0] = (0,10,0)
            self.rgb.write()
        else:
            self.screen.fill(0)
            self.screen.text("WIFI连接超时！",20,0,1)
            self.screen.show()
            self.rgb[0] = (10,0,0)
            self.rgb.write()
        time.sleep(2)
        self.screen_init()
        
    def sub_cb(self,topic, msg):
        print((topic, msg))
        if topic==b'bp':
            self.screen.font_set(0x22,0,1,0)
            self.screen.fill(0)
            self.screen.text(msg.decode(),0,0,1)
            self.screen.show()
    
    def heart_beat(self):
        while 1:
            self.c.publish(b"hb", b"I am live")
            print('live')
            time.sleep(10)
            
    def mqtt(self):
        self.c = MQTTClient(self.MQTT_NAME, server=self.SERVER,user=self.USER,password=self.PASSWORD,port=self.PORT)
        self.c.set_callback(self.sub_cb)
        self.c.connect()
        self.c.subscribe(b"bp")
        _thread.start_new_thread(self.heart_beat, ())
        print('mqtt log in')
        #c.publish(b"bp", b"jd3096 log in")
        while True:
            if True:
                self.c.wait_msg()
            else:
                self.c.check_msg()
                time.sleep(1)
        

