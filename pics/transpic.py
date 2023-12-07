from PIL import Image
import os

file_dir=os.getcwd()
filelist=[]
buflist=[]

#转换图像文件为pbm
for root, dirs, files in os.walk(file_dir): 
    for filename in files:
        try:
            print(filename)
            im=Image.open(filename)
            im=im.convert('1')
            im.save(filename[0:filename.find('.')]+'.pbm')
        except:
            pass

#读出位图数据
for root, dirs, files in os.walk(file_dir):
    pbmfile= [f for f in files if f.endswith(".pbm")]
    for filename in pbmfile:
        with open(filename,'rb') as f:
            f.readline()
            width,height=[int(v) for v in f.readline().split()]
            data=bytearray(f.read())
            #print(data)
            #print(width,height)
            f.close()
        logobuf=filename[:-4]+'=framebuf.FrameBuffer('+str(data)+','+str(width)+','+str(height)+',framebuf.MONO_HLSB)'
        buflist.append(logobuf)

#写入txt文件
with open("buf.txt","w") as f:
    for buf in buflist:
        f.write(buf)
        f.write('\r')
    f.close()
