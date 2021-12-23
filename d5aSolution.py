#-*- coding: utf-8 -*

import os
from tkinter.messagebox import showinfo
from PIL import Image
import tkinter
import tkinter.ttk
import windnd
import uuid
import zipfile
import shutil
import sys
import re
import struct

def floatToBytes(f):#浮点转字符
    return struct.pack("f",f) 

def bytesToFloat(bs):#字符转浮点
    return struct.unpack("f",bs)[0]

def pad_image(image, target_size):
 
    """
    :param image: input image
    :param target_size: a tuple (num,num)
    :return: new image
    """
 
    iw, ih = image.size  # 原始图像的尺寸
    w, h = target_size  # 目标图像的尺寸
 
    # print("原始大小: ",(iw,ih))
    # print("输出大小: ", (w, h))
 
    scale = min((w-170.67) / iw, (h-170.67) / ih)  # 转换的最小比例,可根据需要留白
 
    # 保证长或宽，至少一个符合目标图像的尺寸 0.5保证四舍五入
    nw = int(iw * scale+0.5)
    nh = int(ih * scale+0.5)
    image = image.resize((nw, nh), Image.BICUBIC)  # 更改图像尺寸，双立法插值效果很好
    #image.show()
    new_image = Image.new('RGBA', target_size)  # 
    # // 为整数除法，计算图像的位置
    new_image.paste(image, ((w - nw) // 2, (h - nh) // 2))  # 将图像填充为中间图像
    return new_image
 
def  generateUUID():#生成UUID
    return ''.join([each for each in str(uuid.uuid1()).split('-')])

def createIcon(f):#创建图标
    image = Image.open(f.decode('gbk'))
    size = (1024, 1024)
    newImage=pad_image(image, size)
    newPath = str(f.decode('gbk'))
    #print(newPath)
    result = os.path.split(newPath)
    finalPath = result[0] + "\icon.png"
    newImage.save(finalPath)

def getFileRootAndName(f):#获取文件路径，名称
    newPath = str(f.decode('gbk'))
    root,name = os.path.split(newPath)
    fname = name.split('.')[0]
    return root,fname


def createSummary(f,fileName):#根据文件名创建summary.txt
    root,fname = getFileRootAndName(f)
    file = open(root+'\summary.txt','w')
    file.write(fileName)
    file.close()
    
def createInfo(f,imageUUID,materiaUUID):#创建info.json
    currentPath = os.path.abspath(sys.argv[0])
    currentRoot,currentName = os.path.split(currentPath)
    root,name = getFileRootAndName(f)
    
    productId = generateUUID()#生成productId
    preProductId = '8CFA5CAE4F900B6166E4DA96F573E2A8'
    
    materialGroup = generateUUID()#生成materialGroup
    preMaterialGroup = '4C06A1644797F7D8D4CCB0863B9863D7'
    
    materiaId = materiaUUID#生成materiaId
    preMateriaId = '697494A74F94C219D79A598B10966F25'
    
    pngId = imageUUID#生成pngId
    prePngId = '86BA2C7241F88FE295ACD8A9C151A7AE'
    
    styleId = generateUUID()#生成styleId
    preStyleId= 'E32FC8464E3D36CFA77396A5BA177B41'
    
    listId = [productId,materialGroup,materiaId,pngId,styleId]
    preListId = [preProductId,preMaterialGroup,preMateriaId,prePngId,preStyleId]
    
    f1 = open(currentRoot+"\\info.json",'r+')
    f2 = open(root+'\\info.json','w+')      
    for line in f1.readlines():
        sentence=line
        for i in range(len(listId)):
            sentence=re.sub(preListId[i],listId[i],sentence)#替换原info.json文件中productId,materialGroup,materiaId,pngId,styleId
        f2.write(sentence)
    f1.close()
    f2.close()

def createTextures(f,imageUUID,materiaUUID):#创建textures
    root,fname = getFileRootAndName(f)
    newRoot=root+"\\textures\\um\\"+materiaUUID#创建文件夹
    os.makedirs(newRoot)
    img = Image.open(f.decode('gbk'))
    img.save(newRoot+"\\"+imageUUID+".png")#创建图片


def createD5mesh(f,height):#创建d5mesh
    currentPath = os.path.abspath(sys.argv[0])
    currentRoot,currentName = os.path.split(currentPath)#获得当前目录下地址，文件名
    os.chdir(currentRoot)#转到当前目录
    
    root,fname = getFileRootAndName(f)#获取拖入文件地址，名称
    image = Image.open(f.decode('gbk'))
    iw, ih = image.size
    rate = iw/ih#获取图片宽/高比值
    
    w=rate*height#获取mesh中宽
    with open ("1.d5mesh","rb+") as f:
        s= f.read()
        sa = bytearray(s)
        for i in range(4):
            #sa[60+32*i:64+32*i]=floatToBytes(0.0)
            if i ==0:#mesh第一个点位置
                sa[56+32*i:60+32*i] = floatToBytes(-w/2)
                sa[60+32*i:64+32*i]=floatToBytes(0.0)
                sa[64+32*i:68+32*i]=floatToBytes(height)
                
            if i ==1:#mesh第二个点位置
                sa[56+32*i:60+32*i] = floatToBytes(-w/2)
                sa[60+32*i:64+32*i]=floatToBytes(0.0)
                sa[64+32*i:68+32*i]=floatToBytes(0.0)
                
            if i ==2:#mesh第三个点位置
                sa[56+32*i:60+32*i] = floatToBytes(w/2)
                sa[60+32*i:64+32*i]=floatToBytes(0.0)
                sa[64+32*i:68+32*i]=floatToBytes(height)
                
            if i ==3:#mesh第四个点位置
                sa[56+32*i:60+32*i] = floatToBytes(w/2)
                sa[60+32*i:64+32*i]=floatToBytes(0.0)
                sa[64+32*i:68+32*i]=floatToBytes(0.0)
        #检查输出是否正确
        for i in range(4):
            x=sa[56+32*i:60+32*i]
            y=sa[60+32*i:64+32*i]
            z=sa[64+32*i:68+32*i]
            x1=bytesToFloat(x)
            y1=bytesToFloat(y)
            z1=bytesToFloat(z)
            print(x.hex(),y.hex(),z.hex())
            print(" %(x)s, %(y)s, %(z)s" %{'x':x1, 'y':y1,'z':z1})
        s = bytes(sa)
        os.chdir(root)
        with open("1.d5mesh","wb+") as f2:#输出新的1.d5mesh
            f2.write(s)
            

def compactToD5a(f,imageUUID,materiaUUID,fileName):
    root,fname = getFileRootAndName(f)
    
    os.chdir(root)
    icon = "icon.png"
    summary = "summary.txt"
    textures = "textures\\um\\"+materiaUUID+"\\"+imageUUID+".png"
    info = "info.json"
    d5mesh = "1.d5mesh"
    
    files = [icon, summary, textures, info, d5mesh]
    out_name=root+"\\"+fileName+".d5a"
    result = zipfile.ZipFile(out_name, 'w', zipfile.ZIP_DEFLATED,'utf-8')
    for file in files:
        result.write(file)
    result.close()
    for item in result.namelist():
        item.encode('utf-8')
    for file in files:
        os.remove(file)
    shutil.rmtree("textures")
    
    #输入高度
def setInput(files):
    def inputParameter(inputHeight=172.0,sequence=0):#默认172
        inputHeight = inputHeight
        tk.destroy()
        drag_files(files,inputHeight,sequence)#执行生成d5a操作
    #获取高度
    tk = tkinter.Tk()
    tk.title("ZscTool")
    lable_Height = tkinter.Label(tk, text="自动将png转化为d5a格式,请输入所需高度（注意:只能输入数字）:")
    lable_Height.grid(row=1, column=1)
    data_Height = tkinter.Text(tk, width=20, height=1)  #原始数据录入框
    data_Height.grid(row=2, column=1)
    #获取序号
    lable_sequence = tkinter.Label(tk, text="请输入开始序号（注意:只能输入数字）:")
    lable_sequence.grid(row=3, column=1)
    data_sequence = tkinter.Text(tk, width=20, height=1)  #原始数据录入框
    data_sequence.grid(row=4, column=1)
    button = tkinter.Button(tk, text="确定", bg="lightblue", width=10,command=lambda:inputParameter(inputHeight=float(data_Height.get("0.0","end")),sequence=int(data_sequence.get("0.0","end"))))  # 调用内部方法  加()为直接调用
    button.grid(row=5, column=1)
    tk.mainloop()
    
def drag_files(files,inputHeight,sequence):
    root = tkinter.Tk()
    root.title("转换进度")
    root.geometry('300x120')
    progressbarOne = tkinter.ttk.Progressbar(root)
    progressbarOne.pack(pady=20)
    # 进度值最大值
    progressbarOne['maximum'] = len(files)
    progressbarOne['value']=0
    # 进度值初始值
    for f in files:
        # 每次更新加1
        progressbarOne['value'] += 1
        # 更新画面
        root.update()
        str_sequence=str(sequence)
        fileName = "人物_2D人物_2D人物"+str_sequence+"_Cut out people"+str_sequence+"_20211220"
        imageUUID = generateUUID()#获取imageUUID
        materiaUUID=generateUUID()#获取materiaUUID
        createSummary(f,fileName)#创建summary.txt
        createIcon(f)#创建icon.png
        createInfo(f,imageUUID,materiaUUID)#根据info.json替换相应参数，创建新的info.json
        createTextures(f,imageUUID,materiaUUID)#创建textures，传入imageUUID，materiaUUID
        createD5mesh(f,inputHeight)#根据1.d5mesh替换相应参数，创建新的1.d5mesh
        compactToD5a(f,imageUUID,materiaUUID,fileName)#打包成d5a，并删去文件
        sequence+=1
    root.destroy()
    showinfo("完成","已完成转换")#完成转换提示
 
#"自动填充alpha通道并使图片变为1024*1024"
def main():
    tk = tkinter.Tk()
    tk.title("ZscTool")
    words = tkinter.Label(tk, width=50, height = 25, text="自动将png转化为d5a格式,请拖入png文件")
    words.pack()
    windnd.hook_dropfiles(tk,func=setInput)
    tk.mainloop()

if __name__ == '__main__':
    main()