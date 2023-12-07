# MicroPython ST7567 LCD driver, SPI interfaces
#51102 by jd3096
from micropython import const
import framebuf
import time

# register definitions
DISPON = const(0xAF)
DISPOFF = const(0xAE)
SET_START_LINE = const(0X40)  #后6位为起始行
SET_PAGE_ADDR =  const(0xB0)  #后4位是页地址

SET_SEG_DIR   =  const(0xA0)  #最后一位是方向
SET_DISP_INV  =  const(0x21)  #最后一位是反转
ALL_PIXEL_ON  =  const(0xA4)  #最后一位是设置
BIAS_SELECT   =  const(0xA2)  #最后一位是设置
SOFT_RESET    =  const(0xE2)
SET_COM_DIR   =  const(0xC0)  #第四位是设置
POWER_CONT    =  const(0x28)  #后3位是三个设置
REG_RATIO     =  const(0x20)  #后3位是设置
NOP           =  const(0xE3)
RELEASE_N_LINE=  const(0x84)
SPI_READ_STAT =  const(0xFC)
SPI_READ_DDRAM=  const(0xF4)
EXT_COMM_SET  =  const(0xFE)  #后1位是设置
#注意以下是两字节命令
SET_EV        =  const(0x81)  #后跟随的字节的6位是数据
SET_BOOTER    =  const(0xF8)  #后跟随的字节的1位是数据  
SET_COL_ADDR  =  const(0x10)  #后四位是列高位#后跟随的字节4位是列低位
  
SET_N_LINE    =  const(0x85)  #后跟随的字节的5位是数据 

SET_DISP_MODE =  const(0x70)  #第二位是设置允许，决定下面三个命令的有效
SET_DISP_DUTY =  const(0xD0)  #后3位是占空比
SET_DISP_BIAS =  const(0x90)  #后3位是偏置
SET_DISP_FRATE=  const(0x98)  #后3位是帧率


# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class ST7567(framebuf.FrameBuffer):
    
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.rate=20000000
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB, self.width)

        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs

        self.init_display()

    def init_display(self):

        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        for cmd,delay in (
            (SOFT_RESET,100),
            (POWER_CONT|0x04,5),
            (POWER_CONT|0x06,5),
            (POWER_CONT|0x07,5),
            (0x24,0), 
            (SET_EV,0),   #0x81
            (0x15,0),
            (BIAS_SELECT,1),  #0xa2
            (0xc8,1),  
            (SET_SEG_DIR,1),  #0xa0
            (SET_START_LINE,0),  #0x40
            (DISPON,0)):  #0xaf
            self.write_cmd(cmd)
            time.sleep_ms(delay)
        self.fill(0)
        self.show()
        
    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)

    def poweroff(self):
        self.write_cmd(DISPOFF | 0x00)

    def poweron(self):
        self.write_cmd(DISPON)

    def contrast(self, contrast):
        self.write_cmd(REG_RATIO|(contrast&0x07))

    def invert(self, invert):
        self.write_cmd(SET_DISP_INV | (invert >0))

    def show(self):
        start=2
        for page in range(4):
            self.write_cmd(SET_PAGE_ADDR|page)
            self.write_cmd(0x10)
            self.write_cmd(0x00)
            self.write_data(self.buffer[page*128:(page+1)*128])
