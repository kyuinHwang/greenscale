# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 10:40:31 2020

@author: kyuin hwang
"""

## Version 3.3

import numpy as np
import tkinter as tk
from tkinter import Tk, Button, Canvas, Frame, Label, Entry, Image, Checkbutton, Scale, Text
from tkinter import filedialog, PhotoImage, Toplevel, IntVar
from tkinter import LEFT, RIGHT, BOTTOM, TOP, YES, NW
from tkinter import messagebox as mbox
import PIL
from packaging import version
from PIL import ImageTk, Image
import math
import os, sys, glob
from os import system
from platform import system as platform
import datetime
#if platform() == 'Darwin':  system("""/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python" to true' """)

# def getMass(): ## Temporal
#     global selectedTarget, selectedCoin, img, canvas    
#     ## 1. determine selected area surrounded by clicked points (i.e. selectedTarget, selectedCoin)
#     ##    ==> if can't since the few/incomplete selection
#     ##    ====> presenting error massage dialog
#     ##    ==> connect neigborhood points to determine area
#     ## 2. run calculation source of KKM
#     ##    ==> select pixels within color range
#     ##    ==> change color of selected pixels to ?
#     ##    ==> counting pixels and estimating mass
#     ##    ==> calibrate using value from coin    
#     return len(selectedTarget)    


class MossImage():
    def __init__(self, root, frame, noRow):
        ## Values for main window
        entryFilePath = Entry(frame, width=25)
        entryFilePath.insert(0,"PathPath")
        entryMassP = Entry(frame, width=10)
        entryMassP.insert(0,"TargetPixel")
        entryCoinP = Entry(frame, width=10)
        entryCoinP.insert(0,"CoinRadius")
        entryMassM = Entry(frame, width=10)
        entryMassM.insert(0,"PixelsPerUnit")
        entryMassFW = Entry(frame, width=10)
        entryMassFW.insert(0,"FreshMass")
        entryMassDW = Entry(frame, width=10)
        entryMassDW.insert(0,"DryMass")

        
        buttonFileLoad = Button(frame, text="Load file", command=lambda :self._fileLoad())
        
        entryFilePath.grid(row=noRow, column=0)
        buttonFileLoad.grid(row=noRow, column=1)
        entryMassP.grid(row=noRow, column=2)
        entryCoinP.grid(row=noRow, column=3)
        entryMassM.grid(row=noRow, column=4)
        entryMassFW .grid(row=noRow, column=5)
        entryMassDW .grid(row=noRow, column=6)
        
        self.root = None
        self.filePathImg = None
        self.entryFilePath = entryFilePath
        self.buttonFileLoad = buttonFileLoad
        self.entryMassP = entryMassP
        self.entryCoinP = entryCoinP
        self.entryMassM = entryMassM
        self.entryMassFW = entryMassFW
        self.entryMassDW = entryMassDW
        self.frame = frame        
        self.noRow = noRow ## No of row in main window
        
        ## Values for cropping window
        self.img = None
        self.photoResize = None
        self.canvasCrop = None        
        self.windowCrop = None
        self.targetAnchorX1, self.targetAnchorY1 = None, None
        self.coinAnchorX1, self.coinAnchorY1 = None, None
        self.targetAnchorX2, self.targetAnchorY2 = None, None
        self.coinAnchorX2, self.coinAnchorY2 = None, None
        
        
        ## Values for denoising window
        self.imgCrop = None
        self.photoCropFilter = None                
        self.penWidth = 3
        self.windowDenoise = None
        self.canvasDenoise = None
        self.noisePx = set()
        
        ## Result
        self.coinRadius = None
        self.mossPixel = None
        self.mossPixelN = None
        self.mossMassFW = None
        self.mossMassDW = None
        self.resizeRatio = None


    
    def _fileLoad(self,):
        ## can force selection on here  (*.png,....)
        if self.filePathImg == None:
            self.filePathImg = filedialog.askopenfilename(initialdir="./", title="Select image file") 
        
        self.entryFilePath.delete(0,200)
        self.entryFilePath.insert(0,os.path.basename(self.filePathImg))
        
        acceptableExtensions = ("png","gif")
        for acceptableExtension in acceptableExtensions:
            if self.filePathImg.lower().endswith(acceptableExtension):
                self.img = Image.open(self.filePathImg)
                break
        else:
            try:
                im1 = Image.open(self.filePathImg)
                global TEMPPATH
                tempFN = TEMPPATH + os.sep + os.path.basename(self.filePathImg)
                tempFN = tempFN[:tempFN.rfind('.')] + '.png'
                im1.save(tempFN)
                #self.filePathImg = tempFN
                self.img = Image.open(tempFN)
            except:
                mbox.showerror("Error","Unexpected file type detected!")
                return 0
            
        self._openCropwindow()
        #global cropCanvas, img
        #if cropCanvas != None:
        #    mbox.showerror("Error", "Please load new image after closing current image")
        #    return 0
        ## Need size down and size up before calculation?
        
    def _imageResize(self,):
        width, height = self.img.size
        if width > MAXWIDTH or height > MAXHEIGHT:
            self.resizeRatio = min(MAXWIDTH/width, MAXHEIGHT/height)
            newWidth, newHeight = int(self.resizeRatio*width), int(self.resizeRatio*height)
            if version.parse(PIL.__version__) >= version.parse("10.0.0"):
                self.imgResize = self.img.resize((newWidth,newHeight), Image.Resampling.LANCZOS)
            else:
                self.imgResize = self.img.resize((newWidth,newHeight), Image.ANTIALIAS)
        else:
            self.resizeRatio, self.imgResize = 1, self.img
            
    def _openCropwindow(self,):
        #if self.windowCrop != None and self.windowCrop.state() == 'normal':
        #    self.windowCrop.destroy()
        
        self.windowCrop = Toplevel(self.root)
        self.windowCrop.title("Cropping window")
        self._imageResize()
        self.photoResize = ImageTk.PhotoImage(self.imgResize)
        ## Resized image changed as PhotoImage class to present on canvas 
        #self.imgPhoto = PhotoImage(file=self.filePathImg)        
        #self.imgPIL = Image.open(self.filePathImg).convert("RGBA")
        self.windowCropFrameTop = Frame(self.windowCrop)
        self.windowCropFrameTop.pack(side=TOP)
        
        self.buttonCropSelectTarget = Button(self.windowCropFrameTop, text="SelectTarget", command=self._penTargetMode)
        self.buttonCropSelectCoin = Button(self.windowCropFrameTop, text="SelectCoin", command=self._penCoinMode)
        self.buttonCropClear = Button(self.windowCropFrameTop, text="Reload", command=self._clearCrop)

        self.buttonCropSelectTarget.grid(row=0, column=2)
        self.buttonCropSelectCoin.grid(row=0, column=1)
        self.buttonCropClear.grid(row=0, column=3)
        
        self.windowCropFrameBottom = Frame(self.windowCrop)
        self.windowCropFrameBottom.pack(side=BOTTOM)
        
        self.canvasCrop = Canvas(self.windowCropFrameBottom, width=self.photoResize.width(), \
                                 height=self.photoResize.height(), bg="white")
        self._clearCrop()
        #self.canvasCrop.create_image(0,0,anchor=NW,image=self.photoResize)
        self.canvasCrop.grid(row=1, column=0) 
        self.canvasCrop.bind("<Button-1>", self._selectCoin)
        
                   
    def _penTargetMode(self,):        
        self.canvasCrop.bind("<Button-1>", self._selectTarget)
    
    def _penCoinMode(self,):
        self.canvasCrop.bind("<Button-1>", self._selectCoin)
        
        
    def _clearCrop(self,):
        self.targetAnchorX1, self.targetAnchorY1 = None, None
        self.targetAnchorX2, self.targetAnchorY2 = None, None
        self.coinAnchorX1, self.coinAnchorY1 = None, None
        self.coinAnchorX2, self.coinAnchorY2 = None, None
        #self.canvasCrop.clear()
        self.canvasCrop.create_image(0,0,anchor=NW,image=self.photoResize)
        self._penCoinMode()
        
    def _selectTarget(self, event):
        ## Draw cross
        if self.targetAnchorX1 == None: ## 1st click
            self.canvasCrop.create_line(event.x-20,event.y,event.x+20,event.y, fill='red')
            self.canvasCrop.create_line(event.x,event.y-20,event.x,event.y+20, fill='red')
            self.canvasCrop.create_oval(event.x-5,event.y-5,event.x+5,event.y+5, fill='red')        
            self.targetAnchorX1, self.targetAnchorY1 = event.x, event.y
                        
        elif self.targetAnchorX2 == None: ## 2nd click
            self.canvasCrop.create_line(event.x-20,event.y,event.x+20,event.y, fill='red')
            self.canvasCrop.create_line(event.x,event.y-20,event.x,event.y+20, fill='red')
            self.canvasCrop.create_oval(event.x-5,event.y-5,event.x+5,event.y+5, fill='red')
            self.targetAnchorX2, self.targetAnchorY2 = event.x, event.y
            self._openDenoisewindow()
            
            
    def _selectCoin(self, event):
        ## Draw cross        
        if self.coinAnchorX1 == None: ## 1st click
            self.canvasCrop.create_line(event.x-20,event.y,event.x+20,event.y, fill='blue')
            self.canvasCrop.create_line(event.x,event.y-20,event.x,event.y+20, fill='blue')
            self.canvasCrop.create_oval(event.x-5,event.y-5,event.x+5,event.y+5, fill='blue')
            
            self.coinAnchorX1, self.coinAnchorY1 = event.x, event.y
        elif self.coinAnchorX2 == None: ## 2nd click
            self.canvasCrop.create_line(event.x-20,event.y,event.x+20,event.y, fill='blue')
            self.canvasCrop.create_line(event.x,event.y-20,event.x,event.y+20, fill='blue')
            self.canvasCrop.create_oval(event.x-5,event.y-5,event.x+5,event.y+5, fill='blue')
            
            self.coinAnchorX2, self.coinAnchorY2 = event.x, event.y
            ## Get radius
            self.coinRadius = math.sqrt(abs(event.x - self.coinAnchorX1)**2 \
                                        + abs(event.y - self.coinAnchorY1) ** 2)/2
            self.entryCoinP.delete(0,100)
            self.entryCoinP.insert(0,"%.2f"%self.coinRadius)
            self._penTargetMode()
        
    def _openDenoisewindow(self):
        #if self.windowDenoise != None and self.windowDenoise.state() == 'normal':
        #    self.windowDenoise.destroy()
        self.windowDenoise = Toplevel(self.root)
        self.windowDenoise.title("Denoising window")                        
               
        self.windowDenoiseFrameTop = Frame(self.windowDenoise)
        self.windowDenoiseFrameTop.pack(side=TOP)
        self.windowDenoiseFrameBottom = Frame(self.windowDenoise)
        self.windowDenoiseFrameBottom.pack(side=BOTTOM)
        
        
        self.buttonNoiseClear = Button(self.windowDenoiseFrameTop, text="Clear", command=self._clearNoise)        
        self.buttonGetMass = Button(self.windowDenoiseFrameTop, text="GetMass", command=self._getMass)

        self.scalePenWidth = Scale(self.windowDenoiseFrameTop,label="EraserSize",from_=1,to=20,orient=tk.HORIZONTAL,showvalue=0,tickinterval=5,resolution=1,length=200)
        self.scalePenWidth.bind("<ButtonRelease-1>", self._penWidthUpdate)
        self.scalePenWidth.set(self.penWidth)


        
        #self.imgCrop = self.imgPIL.crop([x1,y1,x2,y2])
        #self.setFilter()
        #self.imgCropFilter = ImageTk.PhotoImage(self.imgCropFilter)        
        self.getCropped()
        
        
        ## imgCrop
        #print(self.imgCropFilter.shape)
        #self.canvasDenoise = Canvas(self.windowDenoise, width=self.imgCropFilter.shape[1],\
        #                            height=self.imgCropFilter.shape[2], bg='white')

        self.photoCropFilter = ImageTk.PhotoImage(Image.fromarray(self.imgCropFilterArray))


        self.canvasDenoise = Canvas(self.windowDenoiseFrameBottom, width=self.photoCropFilter.width(),\
                                    height=self.photoCropFilter.height(), bg='white')
            
        self._clearNoise()   
        #self.canvasDenoise.create_image(0,0,anchor=NW,image=self.photoCropFilter)        
        self.canvasDenoise.bind("<Button-1>", self._selectNoise)
        self.canvasDenoise.bind("<B1-Motion>", self._selectNoise)
                
        self.buttonNoiseClear.grid(row=0, column=0)
        self.buttonGetMass.grid(row=0, column=1)
        self.scalePenWidth.grid(row=0, column=2)
        self.canvasDenoise.grid(row=1, column=0)

    def _penWidthUpdate(self, event):
        self.penWidth = self.scalePenWidth.get()

    def _filterImage(self, img, cvOrder=False):
        if cvOrder: ##(B,G,R) [ 59  57  64]
            b0 = np.copy(img)
            b0[(b0[:, :, 0] > b0[:, :, 1])] = [255, 255, 255]
            b0[(b0[:, :, 0] > b0[:, :, 2])] = [255, 255, 255]
            b0[abs(b0[:, :, 1] - b0[:, :, 0])<50] = [255, 255, 255]
            b0[(b0[:, :, 1]<100)] = [255, 255, 255] 
            b0[(b0[:, :, 2]<100)] = [255, 255, 255]
            return b0
        
        else: ## (R,G,B) [ 64  57  59]
            b0 = np.copy(img)
            b0[(b0[:, :, 2] > b0[:, :, 1])] = [255, 255, 255]
            b0[(b0[:, :, 2] > b0[:, :, 0])] = [255, 255, 255]
            b0[abs(b0[:, :, 1] - b0[:, :, 2])<50] = [255, 255, 255]
            b0[(b0[:, :, 1]<100)] = [255, 255, 255] 
            b0[(b0[:, :, 0]<100)] = [255, 255, 255]
            return b0
            
    def getCropped(self,):
        x1,x2 = sorted([self.targetAnchorX1,self.targetAnchorX2])
        y1,y2 = sorted([self.targetAnchorY1,self.targetAnchorY2])
        ## Order of RGB is reversed between cv2 and PIL
        #imgBase = cv2.imread(self.filePathImg) 
        imgBase = np.array(self.imgResize)
        imgCrop = imgBase[y1:y2, x1:x2]
        
        ### ImageFilter ###
        self.imgCropFilterArray = self._filterImage(imgCrop) # b0
        #print(self.imgCropFilter)
        #self.imgCropFilter = ImageTk.PhotoImage(self.imgCropFilter)
        
        
    def _selectNoise(self,event):                
        x1, y1 = event.x-self.penWidth, event.y-self.penWidth
        x2, y2 = event.x+self.penWidth, event.y+self.penWidth
        self.canvasDenoise.create_rectangle(x1,y1,x2,y2,fill="red", outline="red")
        leny,lenx,lenz = self.imgCropFilterArray.shape
        for y in range(y1,min(y2,leny)):
            for x in range(x1,min(x2,lenx)):
                self.noisePx.add((x,y))

    def _clearNoise(self,):
        self.noisePx = set() 
        self.canvasDenoise.create_image(0,0,anchor=NW,image=self.photoCropFilter)        
        
        
    def _getMass(self,):
        if self.coinRadius == None:
            mbox.showerror("Error","Deterfine coin radius before calculation!")
            return 0
        x1,x2 = sorted([self.targetAnchorX1,self.targetAnchorX2])
        y1,y2 = sorted([self.targetAnchorY1,self.targetAnchorY2])
        #imgPILcropped = self.imgPIL.crop([x1,y1,x2,y2])
        #print(help(imgPILcropped.getpixel))
        #cntMossPixel = 0
        #for y in range(y2-y1):
        #    for x in range(x2-x1):
        #        if (x,y) in self.noisePx: continue
        #        else:
        #            r,g,b = self.imgCropFilterArray[y,x]
        #            if r == 255 and g == 255 and b == 255: continue
        #            cntMossPixel += 1
        #            #r,g,b,a = imgPILcropped.getpixel((x,y))
        #            #if g > 200: cntMossPixel += 1
    
        ## Remove Noise
        #print(self.imgCropFilterArray.shape)
        rgbArray = np.copy(self.imgCropFilterArray)
        for x,y in self.noisePx: rgbArray[y,x] = [255,255,255]
   
        cntMossPixel = len(rgbArray[rgbArray[:, :]!=[255,255, 255]])/3
                        
        self.mossPixel = cntMossPixel
        self.mossPixelN = self.mossPixel/(math.pi*(self.coinRadius**2)) #!!!
        self.mossMassFW = equationFW(self.mossPixelN) ## Magic number to estimate fresh mass
        self.mossMassDW = equationDW(self.mossPixelN) ## Magic number to estimate dry mass
        self.entryMassP.delete(0,100)
        self.entryMassP.insert(0,"%.2f"%self.mossPixel)
        self.entryMassM.delete(0,100)
        self.entryMassM.insert(0,"%.2f"%self.mossPixelN)
        self.entryMassFW.delete(0,100)
        self.entryMassFW.insert(0,"%.2f"%self.mossMassFW)
        self.entryMassDW.delete(0,100)
        self.entryMassDW.insert(0,"%.2f"%self.mossMassDW)
        
        
        self.windowDenoise.destroy()
        self.windowCrop.destroy()

def equationFW(ppu):
    ## Pixel per unit to mass
    return 1.1038*ppu - 4.4981 ## Magic number to estimate fresh mass

def equationDW(ppu):
    return 0.1911*ppu - 0.8180 ## Magic number to estimate dry mass
        

        
def _loadDir():
    global gImages
    fileDir = filedialog.askdirectory(initialdir="./", title="Select image file directory")
    extensions = ['png','jpg','jpeg','gif']
    iFNs = []
    for extension in extensions:
        iFNs.extend(glob.glob(f"{fileDir}/*.{extension}"))
        iFNs.extend(glob.glob(f"{fileDir}/*.{extension.upper()}"))
    iFNs = list(set(iFNs))
    for gImage, iFN in zip(gImages, sorted(iFNs)):
        print(iFN)
        gImage.filePathImg = iFN
        gImage.entryFilePath.delete(0,100)
        gImage.entryFilePath.insert(0,os.path.basename(iFN))
        
    
def _getStat():
    global gImages, excOutlier, entryAvgPPU, entryStdevPPU
    global entryAvgFW, entryAvgDW, Nsample
    ppus = []
    for gImage in gImages:
        if gImage.mossPixelN == None: continue
        ppus.append(gImage.mossPixelN)
    Nsample = len(ppus)
    if excOutlier.get() and len(ppus) > 3:
        q1, q3 = np.percentile(ppus,25),np.percentile(ppus,75)
        IQR = q3-q1
        ppus = [ppu for ppu in ppus if ppu > q1-1.5*IQR and ppu < q3+1.5*IQR]
    avgPPU, stdPPU = np.mean(ppus), np.std(ppus)
    avgFW, avgDW = equationFW(avgPPU), equationDW(avgPPU)
    for entryTarget, valueTarget in zip([entryAvgPPU, entryStdevPPU,entryAvgFW, entryAvgDW],[avgPPU, stdPPU, avgFW, avgDW]):
        entryTarget.delete(0,100)
        entryTarget.insert(0,"%.2f"%valueTarget)
        

## Insert datetime into the last column?
def _savePhotos():
    global photoLogFN, gImages, entrySampleName
    sampleName = entrySampleName.get()
    if os.path.exists(photoLogFN):
        LOGFP = open(photoLogFN,'a')
    else:
        LOGFP = open(photoLogFN,'a')
        LOGFP.write('\t'.join(["SampleName","ImageFilePath","ResizeRatio","#GreenishPixel","CoinRadius","Scaled#GreenishPixel","FreshWeight","DryWeight","ProcessingDate"]) + '\n')

    if sampleName == "PutSampleName": sampleName = "Unknown"
    for gImage in gImages:
        if gImage.mossPixelN == None: continue
        wList = [sampleName, gImage.filePathImg, gImage.resizeRatio, 
                 gImage.mossPixel, gImage.coinRadius, gImage.mossPixelN,
                 gImage.mossMassFW, gImage.mossMassDW, str(datetime.datetime.now())]
        LOGFP.write('\t'.join([str(value) for value in wList])+'\n')
    print("Save photo records completed")
    LOGFP.close()        

def _saveSample():
    global sampleLogFN, Nsample, excOutlier, entryAvgPPU, entryStdevPPU
    global entryAvgFW, entryAvgDW, Nsample, entrySampleName
    
    sampleName = entrySampleName.get()
    if sampleName == "PutSampleName": sampleName = "Unknown"
    if os.path.exists(sampleLogFN):
        LOGFP = open(sampleLogFN,'a')
    else:
        LOGFP = open(sampleLogFN,'a')
        LOGFP.write('\t'.join(["SampleName","#PhotographsIncludedInCalculation","IsExcludeOutlier","AverageFreshweight","AverageDryWeight"]) + '\n')
    wList = [sampleName,str(Nsample),str(excOutlier.get())]
    for entryTarget in [entryAvgPPU, entryStdevPPU,entryAvgFW, entryAvgDW]:
        targetValue = entryTarget.get()
        if not targetValue.replace('.','').isdigit(): return 0
        wList.append(targetValue)
    wList.append(str(datetime.datetime.now()))
    LOGFP.write('\t'.join(wList)+'\n')
    print("Save sample record completed")
    LOGFP.close()        



## Main
photoLogFN = "./Results.photo.txt"
sampleLogFN = "./Results.sample.txt"
TEMPPATH = "./Temp"
MAXHEIGHT, MAXWIDTH = 1000, 1000
Nsample = 0
if not os.path.exists(TEMPPATH): os.mkdir(TEMPPATH)
root = Tk()
root.title("Deschampsia antarctica")
root.geometry("900x750+100+100")
root.resizable(True,True)
frameTop = Frame(root)
frameTop.pack(side=TOP)
entrySampleName = Entry(frameTop, width=20)
entrySampleName.insert(0,"PutSampleName")
entrySampleName.grid(row=0, column=0)
buttonLoadDir = Button(frameTop, text="Load Dir", command=_loadDir)
buttonLoadDir.grid(row=0, column=1)

gImages = []
for noRow in range(1,21):        
    gImages.append(MossImage(root, frameTop, noRow))
    

frameBottom = Frame(root)
frameBottom.pack(side=BOTTOM)


buttonGetStat = Button(frameBottom, text="GetAverage", command=_getStat)
excOutlier = IntVar()
checkOutlier = Checkbutton(frameBottom,text="exclude outliers",variable=excOutlier, onvalue=True, offvalue=False)
buttonSavePhoto = Button(frameBottom, text="SavePhotoData", command=_savePhotos)

buttonSaveSample = Button(frameBottom, text="SaveSampleData", command=_saveSample)
entryAvgPPU = Entry(frameBottom, width=10) ## Pixel Per Unit
entryStdevPPU = Entry(frameBottom, width=10) 
entryAvgFW = Entry(frameBottom, width=10) 
entryAvgDW = Entry(frameBottom, width=10) 


entryAvgPPU.insert(0,"AvgPPU")
entryStdevPPU.insert(0,"Stdev")
entryAvgFW.insert(0,"Freshmass")
entryAvgDW.insert(0,"DryMass")


buttonSavePhoto.grid(row=0, column=0)

buttonGetStat.grid(row=1, column=0)
checkOutlier.grid(row=1, column=1)
entryAvgPPU.grid(row=1, column=2)
entryStdevPPU.grid(row=1, column=3)
entryAvgFW.grid(row=1, column=4)
entryAvgDW.grid(row=1, column=5)
buttonSaveSample.grid(row=1, column=6)

root.mainloop()
