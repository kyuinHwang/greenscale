# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 10:40:31 2020

@author: gwill
"""

## V4.1.0

import numpy as np
import tkinter as tk
from tkinter import Tk, Button, Canvas, Frame, Label, Entry, Image, Checkbutton, Scale, Text
from tkinter import filedialog, PhotoImage, Toplevel, IntVar
from tkinter import LEFT, RIGHT, BOTTOM, TOP, YES, NW
from tkinter import messagebox as mbox
from PIL import ImageTk, Image
import math
import os, sys, glob
from os import system
from platform import system as platform
import datetime
from collections import Counter

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

from random import randrange


if platform() == 'Darwin':  system("""/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python" to true' """)

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
        entryFilePath.insert(0,"Path")
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
        entryMassFW.grid(row=noRow, column=5)
        entryMassDW.grid(row=noRow, column=6)
        
        self.root = None
        self.filePathImg = None
        self.filePathTemp = None
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
        self.imgResize = None
        self.aryResize = None
        self.aryResize = None
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
        

        ## Values for threshold determining window
        self.thresholdAnchorX1,self.thresholdAnchorX2 = None, None
        self.thresholdAnchorY1,self.thresholdAnchorY2 = None, None
        
        
        
        ## Values for specific band window


        ## Value for automatic coin detection
        ## Initial cluster search
        self.coinRedMin, self.coinRedMax = 231, 255
        self.coinGreenMin, self.coinGreenMax = 209, 255
        self.coinBlueMin, self.coinBlueMax =159, 226
        self.coinStatement1 = "R > B"
        self.coinStatement2 = "G > B"
        self.coinStatement3 = ""


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
                self.filePathTemp = tempFN
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
            self.imgResize = self.img.resize((newWidth,newHeight), Image.ANTIALIAS)
        else:
            self.resizeRatio, self.imgResize = 1, self.img

    def _on_closingCropWindow(self,):
        if self.filePathTemp != None:
            print(self.filePathTemp)
            os.remove(self.filePathTemp)
        self.windowCrop.destroy()
        
    def _openCropwindow(self,):
        #if self.windowCrop != None and self.windowCrop.state() == 'normal':
        #    self.windowCrop.destroy()     
        self.windowCrop = Toplevel(self.root)
        self.windowCrop.protocol("WM_DELETE_WINDOW",self._on_closingCropWindow)
        self.windowCrop.title("Cropping window")
        self._imageResize()
        self.photoResize = ImageTk.PhotoImage(self.imgResize)
        self.aryResize = np.array(self.imgResize) ## Original RBG values array
        ## Resized image changed as PhotoImage class to present on canvas 
        #self.imgPhoto = PhotoImage(file=self.filePathImg)        
        #self.imgPIL = Image.open(self.filePathImg).convert("RGBA")
        self.windowCropFrameTop = Frame(self.windowCrop)
        self.windowCropFrameTop.pack(side=TOP)
        
        self.buttonCropSelectTarget = Button(self.windowCropFrameTop, text="SelectTarget", command=self._penTargetMode)
        self.buttonCropSelectCoin = Button(self.windowCropFrameTop, text="SelectCoin", command=self._penCoinMode)
        self.buttonCropClear = Button(self.windowCropFrameTop, text="Reload", command=self._clearCrop)
        self.buttonThresholdWindow = Button(self.windowCropFrameTop, text="ThresholdTest", command=self._openThresholdWindow)

        self.buttonCropSearchTarget = Button(self.windowCropFrameTop, text="SearchTarget", command=self._searchTarget)
        self.buttonCropSearchCoin = Button(self.windowCropFrameTop, text="SearchCoin", command=self._searchCoin)
        self.buttonCropGetStat = Button(self.windowCropFrameTop, text="GetStat", command=self._getStat)
        self.buttonCropRedBand = Button(self.windowCropFrameTop, text="OpenRedBand", command=self._openRedWindow)
        self.buttonCropGreenBand = Button(self.windowCropFrameTop, text="OpenGreenBand", command=self._openGreenWindow)
        self.buttonCropBlueBand = Button(self.windowCropFrameTop, text="OpenBlueBand", command=self._openBlueWindow)
        
        
        self.buttonCropSelectTarget.grid(row=0, column=2)
        self.buttonCropSelectCoin.grid(row=0, column=1)
        self.buttonCropClear.grid(row=0, column=3)
        self.buttonThresholdWindow.grid(row=0, column=4)

        self.buttonCropSearchCoin.grid(row=1,column=1)        
        self.buttonCropSearchTarget.grid(row=1, column=2)
        self.buttonCropGetStat.grid(row=1,column=3)
        self.buttonCropRedBand.grid(row=1,column=5)
        self.buttonCropGreenBand.grid(row=1,column=6)
        self.buttonCropBlueBand.grid(row=1,column=7)

        self.windowCropFrameBottom = Frame(self.windowCrop)
        self.windowCropFrameBottom.pack(side=BOTTOM)
        
        self.canvasCrop = Canvas(self.windowCropFrameBottom, width=self.photoResize.width(), \
                                 height=self.photoResize.height(), bg="white")
        self._clearCrop()
        #self.canvasCrop.create_image(0,0,anchor=NW,image=self.photoResize)
        self.canvasCrop.grid(row=1, column=0) 
        self.canvasCrop.bind("<Button-1>", self._selectCoin)


    def _getStat(self,):
        imgBase = np.array(self.imgResize)
        height, width, nBand = imgBase.shape
        colorL = []
        for y in range(height):
            for x in range(width):
                colorL.append(imgBase)
        self.windowStat = Toplevel(self.root)
        self.windowStat.title("Screen Image")                        
               
        self.windowStatFrameTop = Frame(self.windowStat)
        self.windowStatFrameTop.pack(side=TOP)
        self.windowStatFrameBottom = Frame(self.windowStat)
        self.windowStatFrameBottom.pack(side=BOTTOM)
        
        ## Plot four figures using matplotlib
        ## ref : https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
        ## top left(x = red, y = green). top right(x = blue, y = green)
        ## bottom left(x = red, y = blue). bottom right = histogram for three bands
        ## Density plot or Scatter plot without quantitative measure
        
        # fig = Figure(figsize=(5,5), dpi=300)
        # plot1 = fig.add_subplot(2,1,1)
        # y = [i**2 for i in range(50)]
        # plot1.plot(y)
        
        # plot2 = fig.add_subplot(2,1,2)
        # y2 = [i for i in range(50)]
        # plot2.plot(y2)
        
        # canvas = FigureCanvasTkAgg(fig, master=self.windowStatFrameTop)
        # canvas.draw()
        # canvas.get_tk_widget().pack()
        # toolbar = NavigationToolbar2Tk(canvas, self.windowStatFrameTop)
        # toolbar.update()
        # canvas.get_tk_widget().pack()
        
        #plot1 = fig.add_subplot(111, projection="3d")
        #plot1.scatter(x,y,z)
        
        ## Futhermore, present fixels of figure which have selected range of rgb values
        ## like as _filterImage
        
    
    
    def _openRedWindow(self,): self._openSpecificBandWindow("Red")
    def _openGreenWindow(self,): self._openSpecificBandWindow("Green")
    def _openBlueWindow(self,): self._openSpecificBandWindow("Blue")
        
    def _bandAdaptCutoffRefresh(self):
        cutoffEntries = [self.entryRedMin, self.entryRedMax, self.entryGreenMin, self.entryGreenMax, self.entryBlueMin, self.entryBlueMax]
        cutoffs = [cutoffEntry.get() for cutoffEntry in cutoffEntries]
        cutoffsInt = []
        for idx, value in enumerate(cutoffs):
            if value.isdigit(): cutoffsInt.append(int(value))
            else: cutoffsInt.append(255*(idx%2))
        redMin, redMax, greenMin, greenMax, blueMin, blueMax = cutoffsInt
        newAryBand = np.copy(self.aryBand)
        height, width, nBand = self.aryResize.shape
        middle = lambda value,minmax:value>=minmax[0] and value<=minmax[1]
        for y in range(height):
            for x in range(width):
                if not all([middle(self.aryResize[y][x][idx],minmax) for idx, minmax in enumerate([(redMin,redMax),(greenMin,greenMax),(blueMin,blueMax)])]):
                    newAryBand[y][x] = (255,255,255) 
        self.imgBand = ImageTk.PhotoImage(Image.fromarray(newAryBand))
        self.canvasBand.create_image(0,0,anchor=NW,image=self.imgBand)
        self.canvasBand.bind("<Button-1>", self._grepRGBband)

    def _thresholdAdaptFilter(self):
        cutoffScales = [self.scaleThresholdRedMin, self.scaleThresholdRedMax, self.scaleThresholdGreenMin, self.scaleThresholdGreenMax, self.scaleThresholdBlueMin, self.scaleThresholdBlueMax]
        cutoffsInt = [cutoffScale.get() for cutoffScale in cutoffScales]
        redMin, redMax, greenMin, greenMax, blueMin, blueMax = cutoffsInt
        newAryImg = np.copy(self.aryResize)
        height, width, nBand = self.aryResize.shape
        middle = lambda value,minmax:value>=minmax[0] and value<=minmax[1]

        statementStrs = [self.entryThresholdStatement1.get(),self.entryThresholdStatement2.get(),self.entryThresholdStatement3.get()]
        statementStrs = [statementStr for statementStr in statementStrs if statementStr != ""]
        #print(statementStrs)
        cntIncluded = 0 
        for y in range(height):
            for x in range(width):
                if not all([middle(self.aryResize[y][x][idx],minmax) for idx, minmax in enumerate([(redMin,redMax),(greenMin,greenMax),(blueMin,blueMax)])]) \
                    or not all([eval(statementStr,{"R":self.aryResize[y][x][0],"G":self.aryResize[y][x][1],"B":self.aryResize[y][x][2]}) for statementStr in statementStrs]):
                    newAryImg[y][x] = (255,255,255) 
                else: cntIncluded += 1
        
        self.imgFilter = ImageTk.PhotoImage(Image.fromarray(newAryImg))
        self.canvasThreshold.create_image(0,0,anchor=NW,image=self.imgFilter)
        self.entryThresholdCountedFixel.delete(0,200)
        self.entryThresholdCountedFixel.insert(0,str(cntIncluded))


    def _openThresholdWindow(self,):
        #if self.windowCrop != None and self.windowCrop.state() == 'normal':
        #    self.windowCrop.destroy()     
        self.windowThreshold = Toplevel(self.root)
        self.windowThreshold.title("Threshold determination window")
        ## Resized image changed as PhotoImage class to present on canvas 
        #self.imgPhoto = PhotoImage(file=self.filePathImg)        
        #self.imgPIL = Image.open(self.filePathImg).convert("RGBA")
        self.windowThresholdFrameTop = Frame(self.windowThreshold)
        self.windowThresholdFrameTop.pack(side=TOP)
        
        self.entryThresholdRedCursor = Entry(self.windowThresholdFrameTop, width=10)
        self.entryThresholdGreenCursor = Entry(self.windowThresholdFrameTop, width=10)
        self.entryThresholdBlueCursor = Entry(self.windowThresholdFrameTop, width=10)
        self.entryThresholdRedCursor.grid(row=0, column=0)
        self.entryThresholdGreenCursor.grid(row=0, column=1)
        self.entryThresholdBlueCursor.grid(row=0, column=2)
        
        #self.buttonThresholdPointMode = Button(self.windowThresholdFrameTOP, text="Point", command=self._thresholdClickPoint)
        #self.buttonThresholdAreaMode = Button(self.windowThresholdFrameTOP, text="Area", command=self._thresholdClickArea)
        
 
        self.windowThresholdFrameRIGHT = Frame(self.windowThreshold,width=200,background="bisque")
        self.windowThresholdFrameRIGHT.pack(side=RIGHT)
        
        self.entryThresholdRedMin=Entry(self.windowThresholdFrameRIGHT, width=5)
        self.entryThresholdRedMax=Entry(self.windowThresholdFrameRIGHT, width=5)
        self.entryThresholdGreenMin=Entry(self.windowThresholdFrameRIGHT, width=5)
        self.entryThresholdGreenMax=Entry(self.windowThresholdFrameRIGHT, width=5)
        self.entryThresholdBlueMin=Entry(self.windowThresholdFrameRIGHT, width=5)
        self.entryThresholdBlueMax=Entry(self.windowThresholdFrameRIGHT, width=5)
        
        self.scaleThresholdRedMin=Scale(self.windowThresholdFrameRIGHT,label="RedMin",from_=0,to=255,orient=tk.HORIZONTAL,showvalue=0,tickinterval=50,resolution=1,length=200) 
        self.scaleThresholdRedMax=Scale(self.windowThresholdFrameRIGHT,label="RedMax",from_=0,to=255,orient=tk.HORIZONTAL,showvalue=0,tickinterval=50,resolution=1,length=200)
        self.scaleThresholdGreenMin=Scale(self.windowThresholdFrameRIGHT,label="GreenMin",from_=0,to=255,orient=tk.HORIZONTAL,showvalue=0,tickinterval=50,resolution=1,length=200)
        self.scaleThresholdGreenMax=Scale(self.windowThresholdFrameRIGHT,label="GreenMax",from_=0,to=255,orient=tk.HORIZONTAL,showvalue=0,tickinterval=50,resolution=1,length=200)
        self.scaleThresholdBlueMin=Scale(self.windowThresholdFrameRIGHT,label="BlueMin",from_=0,to=255,orient=tk.HORIZONTAL,showvalue=0,tickinterval=50,resolution=1,length=200)
        self.scaleThresholdBlueMax=Scale(self.windowThresholdFrameRIGHT,label="BlueMax",from_=0,to=255,orient=tk.HORIZONTAL,showvalue=0,tickinterval=50,resolution=1,length=200)
        #for scale in [self.scaleThresholdRedMax, self.scaleThresholdGreenMax, self.scaleThresholdBlueMax, \
        #              self.scaleThresholdRedMin, self.scaleThresholdGreenMin, self.scaleThresholdBlueMin]:
        #    scale.place(relx=0.1,relwidth=0.1)
        for maxScale in [self.scaleThresholdRedMax, self.scaleThresholdGreenMax, self.scaleThresholdBlueMax]: maxScale.set(255)
        self.buttonThresholdAdaptFilter = Button(self.windowThresholdFrameRIGHT, text="Filter", command=self._thresholdAdaptFilter)
        
        self.entryThresholdStatement1 = Entry(self.windowThresholdFrameRIGHT, width=20) 
        self.entryThresholdStatement2 = Entry(self.windowThresholdFrameRIGHT, width=20)        
        self.entryThresholdStatement3 = Entry(self.windowThresholdFrameRIGHT, width=20)        


        self.scaleThresholdRedMin.bind("<ButtonRelease-1>", self._entryThresholdRedMinUpdate)
        self.scaleThresholdRedMax.bind("<ButtonRelease-1>", self._entryThresholdRedMaxUpdate)
        self.scaleThresholdGreenMin.bind("<ButtonRelease-1>", self._entryThresholdGreenMinUpdate)
        self.scaleThresholdGreenMax.bind("<ButtonRelease-1>", self._entryThresholdGreenMaxUpdate)
        self.scaleThresholdBlueMin.bind("<ButtonRelease-1>", self._entryThresholdBlueMinUpdate)
        self.scaleThresholdBlueMax.bind("<ButtonRelease-1>", self._entryThresholdBlueMaxUpdate)

        self.textThresholdRGBDist = Text(self.windowThresholdFrameRIGHT, width=20, height=10, font=('Arial',12))
        self.textThresholdRGBDist.grid(row=0,column=1)        


        rowStartScale = 1
        self.entryThresholdRedMin.grid(row=0+rowStartScale, column=1)  
        self.entryThresholdRedMax.grid(row=1+rowStartScale, column=1)  
        self.entryThresholdGreenMin.grid(row=2+rowStartScale, column=1)  
        self.entryThresholdGreenMax.grid(row=3+rowStartScale, column=1)  
        self.entryThresholdBlueMin.grid(row=4+rowStartScale, column=1)  
        self.entryThresholdBlueMax.grid(row=5+rowStartScale, column=1)  


        self.scaleThresholdRedMin.grid(row=0+rowStartScale,column=2)
        self.scaleThresholdRedMax.grid(row=1+rowStartScale,column=2)
        self.scaleThresholdGreenMin.grid(row=2+rowStartScale,column=2) 
        self.scaleThresholdGreenMax.grid(row=3+rowStartScale,column=2)
        self.scaleThresholdBlueMin.grid(row=4+rowStartScale,column=2)
        self.scaleThresholdBlueMax.grid(row=5+rowStartScale,column=2)
        
        self.entryThresholdStatement1.grid(row=6+rowStartScale,column=2)
        self.entryThresholdStatement2.grid(row=7+rowStartScale,column=2)
        self.entryThresholdStatement3.grid(row=8+rowStartScale,column=2)
        self.buttonThresholdAdaptFilter.grid(row=9+rowStartScale,column=2)

        self.windowThresholdFrameLEFT = Frame(self.windowThreshold,background="blue")
        self.windowThresholdFrameLEFT.pack(side=LEFT)

        self.canvasThreshold = Canvas(self.windowThresholdFrameLEFT, width=self.photoResize.width(), \
                                 height=self.photoResize.height(), bg="white")
        self.canvasThreshold.grid(row=1, column=0) 
        self.canvasThreshold.create_image(0,0,anchor=NW,image=self.photoResize)
        self.canvasThreshold.bind("<Button-1>", self._grepRGBThreshold)
        self.canvasThreshold.bind("<Button-2>", self._grepRGBThresholdArea)

        self.windowThresholdFrameBOTTOM = Frame(self.windowThreshold)
        self.windowThresholdFrameBOTTOM.pack(side=BOTTOM)
        self.entryThresholdCountedFixel = Entry(self.windowThresholdFrameBOTTOM, width=10)
        self.entryThresholdCountedFixel.grid(row=0,column=0)

    def _cropAdaptCutoffRefresh(self):
        cutoffScales = []

    def _entryThresholdRedMinUpdate(self, event): self.entryThresholdRedMin.delete(0,100); self.entryThresholdRedMin.insert(0,str(self.scaleThresholdRedMin.get()))
    def _entryThresholdRedMaxUpdate(self, event): self.entryThresholdRedMax.delete(0,100); self.entryThresholdRedMax.insert(0,str(self.scaleThresholdRedMax.get()))
    def _entryThresholdGreenMinUpdate(self, event): self.entryThresholdGreenMin.delete(0,100); self.entryThresholdGreenMin.insert(0,str(self.scaleThresholdGreenMin.get()))
    def _entryThresholdGreenMaxUpdate(self, event): self.entryThresholdGreenMax.delete(0,100); self.entryThresholdGreenMax.insert(0,str(self.scaleThresholdGreenMax.get()))
    def _entryThresholdBlueMinUpdate(self, event): self.entryThresholdBlueMin.delete(0,100); self.entryThresholdBlueMin.insert(0,str(self.scaleThresholdBlueMin.get()))
    def _entryThresholdBlueMaxUpdate(self, event): self.entryThresholdBlueMax.delete(0,100); self.entryThresholdBlueMax.insert(0,str(self.scaleThresholdBlueMax.get()))


    def _openSpecificBandWindow(self,color):
        self.windowBand = Toplevel(self.root)
        self.windowBand.title(f"{color} Band figure")                        
               
        self.windowBandFrameTop = Frame(self.windowBand)
        self.windowBandFrameTop.pack(side=TOP)
        self.windowBandFrameBottom = Frame(self.windowBand)
        self.windowBandFrameBottom.pack(side=BOTTOM)
        
        self.entryRedCursorBand = Entry(self.windowBandFrameTop, width=10)
        self.entryGreenCursorBand = Entry(self.windowBandFrameTop, width=10)
        self.entryBlueCursorBand = Entry(self.windowBandFrameTop, width=10)

        self.entryRedMin = Entry(self.windowBandFrameTop, width=10)
        self.entryGreenMin = Entry(self.windowBandFrameTop, width=10)
        self.entryBlueMin = Entry(self.windowBandFrameTop, width=10)
        self.entryRedMax = Entry(self.windowBandFrameTop, width=10)
        self.entryGreenMax = Entry(self.windowBandFrameTop, width=10)
        self.entryBlueMax = Entry(self.windowBandFrameTop, width=10)

        self.entryRedMin.insert(0,"0"); self.entryRedMax.insert(0,"255")
        self.entryGreenMin.insert(0,"0"); self.entryGreenMax.insert(0,"255")
        self.entryBlueMin.insert(0,"0"); self.entryBlueMax.insert(0,"255")

        self.entryRedCursorBand.grid(row=1, column=1); self.entryGreenCursorBand.grid(row=1,column=2); self.entryBlueCursorBand.grid(row=1,column=3)
        self.entryRedMin.grid(row=2, column=1); self.entryRedMax.grid(row=3, column=1); 
        self.entryGreenMin.grid(row=2, column=2); self.entryGreenMax.grid(row=3, column=2)
        self.entryBlueMin.grid(row=2, column=3); self.entryBlueMax.grid(row=3, column=3);

        
        bandIdx = {"Red":0,"Green":1,"Blue":2}.get(color)
        otherIdxs = set([0,1,2]) - set((bandIdx,)) ## Indexs of Non-targeted bands

        height, width, nBand = self.aryResize.shape
        self.aryBand = np.copy(self.aryResize) ## Modified RGB values array e.g. (Red, 0, 0)
        for y in range(height):
            for x in range(width):
                for idx in otherIdxs: self.aryBand[y][x][idx] = 0
        self.imgBand = ImageTk.PhotoImage(Image.fromarray(self.aryBand))
        self.canvasBand = Canvas(self.windowBandFrameBottom, width=width,\
                                    height=height, bg='white')      
                
        self.canvasBand.grid(row=2, column=0)
        self.canvasBand.create_image(0,0,anchor=NW,image=self.imgBand)
        self.canvasBand.bind("<Button-1>", self._grepRGBband)

        self.buttonRefresh = Button(self.windowBandFrameTop, text="Adapt", command=self._bandAdaptCutoffRefresh) 
        self.buttonRefresh.grid(row=2, column=4)        

        
    def _grepRGBband(self,event):
        rgbValues = self.aryResize[event.y][event.x]
        self.entryRedCursorBand.delete(0,100)
        self.entryRedCursorBand.insert(0,"%.2f"%rgbValues[0])
        self.entryGreenCursorBand.delete(0,100)
        self.entryGreenCursorBand.insert(0,"%.2f"%rgbValues[1])
        self.entryBlueCursorBand.delete(0,100)
        self.entryBlueCursorBand.insert(0,"%.2f"%rgbValues[2])



    def _searchTarget(self,):
        aryResize = np.array(self.imgResize)
        height, width, nBand = aryResize.shape
        midX, midY = int(width/2), int(height/2)
        
    
    def _searchCoin(self,):
        aryResize = np.array(self.imgResize)
        height, width, nBand = aryResize.shape
        midX, midY = int(width/2), int(height/2)
        ## Lower right
        clusters = []
        for y in range(height):
            for x in range(width):
                R,G,B = self.aryResize[y][x]
                if self.coinRedMin <= R and self.coinRedMax >= R and \
                   self.coinGreenMin <= G and self.coinGreenMax >= G and \
                   self.coinBlueMin <= B and self.coinBlueMax >= B:
                       ## Search nearest cluster
                       for idx, cluster in enumerate(sorted(clusters,key=len,reverse=True)):
                           if any([abs(x-xcoord)+abs(y-ycoord) <= 2 for xcoord, ycoord in cluster]):
                              clusterIdx = idx
                              break
                       else: clusterIdx = None
                       
                       if clusterIdx == None: clusters.append([(x,y)])
                       else: clusters[clusterIdx].append((x,y))
        ## Upper left               
        clusters = list(filter(lambda x:len(x)>=100,clusters))
        for y in range(height-1,-1,-1):
            for x in range(width-1,-1,-1):
                R,G,B = self.aryResize[y][x]
                if self.coinRedMin <= R and self.coinRedMax >= R and \
                   self.coinGreenMin <= G and self.coinGreenMax >= G and \
                   self.coinBlueMin <= B and self.coinBlueMax >= B:
                       ## Search nearest cluster
                       for idx, cluster in enumerate(sorted(clusters,key=len,reverse=True)):
                           if any([abs(x-xcoord)+abs(y-ycoord) <= 2 for xcoord, ycoord in cluster]):
                              clusterIdx = idx
                              break
                       else: clusterIdx = None
                       
                       if clusterIdx == None: clusters.append([(x,y)])
                       else: clusters[clusterIdx].append((x,y))

        #for cluster in sorted(filter(lambda x:len(x)>=10,clusters),key=len,reverse=True):
        #    print(len(cluster),cluster)
        clusters = [set(cluster) for cluster in clusters]
        largestCluster = max(clusters,key=len)
        
        ## Cluster extention
        largestClusterExt = set(list(largestCluster)[:]) ## Extension
        maxCycle = 200 ## MAXCYCLE in modification
        rejected = set()
        for nCycle in range(maxCycle):
            searchPixels = set()
            for x,y in largestClusterExt:
                for point in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]: searchPixels.add(point)
            searchPixels = searchPixels.difference(rejected.union(largestClusterExt))
            addedPixels = set()
            for x,y in searchPixels:
                R,G,B = self.aryResize[y][x]
                ## Equation using RGB and distance from center or nearest pixel of cluster
                if self.coinRedMin <= R and self.coinRedMax >= R and \
                   self.coinGreenMin <= G and self.coinGreenMax >= G and \
                   self.coinBlueMin <= B and self.coinBlueMax >= B:
                    addedPixels.add((x,y))
                else: rejected.add((x,y))
            if len(addedPixels) == 0:
                print(nCycle,"Cycle searched for coin cluster extension")
                break
            for x,y in addedPixels: largestClusterExt.add((x,y))
        
        
        borderlinePixels = searchPixels.union(rejected) ## Boderline + 1 of cluster
        distMaxL = []
        for xQue, yQue in borderlinePixels: ## Query 
            distMax = max([abs(xQue-xSub)**2+abs(yQue-ySub)**2 for xSub, ySub in borderlinePixels]) ## Subject
            distMaxL.append(distMax)
        distMaxL = list(sorted(distMaxL,reverse=True))
        sampleSize = 10
        self.coinRadius = math.sqrt(sum(distMaxL[:sampleSize])/sampleSize)/2
        self.entryCoinP.delete(0,100)
        self.entryCoinP.insert(0,"%.2f"%self.coinRadius)
        print("Coin radius by automatic search",self.coinRadius)
        
        # Print on screen
        imgBase = np.array(self.imgResize)
        for x,y in largestClusterExt: 
            imgBase[y][x][0] = 190
            imgBase[y][x][1] = 0
            imgBase[y][x][2] = 0
        self.imgCoin = ImageTk.PhotoImage(Image.fromarray(imgBase))
        self.canvasCrop.create_image(0,0,anchor=NW,image=self.imgCoin)
         
        
                   
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
            self.coinRadius = math.sqrt(abs(event.x-self.coinAnchorX1)**2 \
                                        + abs(event.y-self.coinAnchorY1)**2)/2
            self.entryCoinP.delete(0,100)
            self.entryCoinP.insert(0,"%.2f"%self.coinRadius)
            print("Coin radius by manual selection",self.coinRadius)
        
        
            self._penTargetMode()


    def _grepRGBThreshold(self,event): # self.entryThresholdRedCursor
        rgbValues = self.aryResize[event.y][event.x]
        self.entryThresholdRedCursor.delete(0,100)
        self.entryThresholdRedCursor.insert(0,"%.2f"%rgbValues[0])
        self.entryThresholdGreenCursor.delete(0,100)
        self.entryThresholdGreenCursor.insert(0,"%.2f"%rgbValues[1])
        self.entryThresholdBlueCursor.delete(0,100)
        self.entryThresholdBlueCursor.insert(0,"%.2f"%rgbValues[2])

    def _grepRGBThresholdArea(self,event): # self.entryThresholdRedCursor
        if self.thresholdAnchorX1 == None: ## 1st click
            self.thresholdAnchorX1, self.thresholdAnchorY1 = event.x, event.y
        elif self.thresholdAnchorX2 == None: ## 2nd click
            self.thresholdAnchorX2, self.thresholdAnchorY2 = event.x, event.y
            cntRGB = Counter()
            for x in range(min(self.thresholdAnchorX1,self.thresholdAnchorX2),max(self.thresholdAnchorX1,self.thresholdAnchorX2)):
                for y in range(min(self.thresholdAnchorY1,self.thresholdAnchorY2),max(self.thresholdAnchorY1,self.thresholdAnchorY2)):
                    R,G,B = self.aryResize[y][x]
                    R,G,B = round(R/5)*5, round(G/5)*5, round(B/5)*5 ## As histogram
                    cntRGB[(R,G,B)] += 1
            strRGBdistL = []
            for rank, rgbValues in zip(range(10),sorted(cntRGB.items(),key=lambda x:x[1], reverse=True)):
                rgbV, nPixel = rgbValues
                strRGBdist = f"{rgbV[0]} {rgbV[1]} {rgbV[2]} : {nPixel}"
                strRGBdistL.append(strRGBdist)
            self.entryThresholdRGBDist.delete(0,1000)
            self.entryThresholdRGBDist.insert(0,"\n".join(strRGBdistL))
            self.thresholdAnchorX1, self.thresholdAnchorX2 = None, None
            self.thresholdAnchorY1, self.thresholdAnchorY2 = None, None



        
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
        self.mossPixelN = self.mossPixel/(self.coinRadius**2) #!!!
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
        self._on_closingCropWindow()

def equationFW(ppu):
    ## Pixel per unit to mass
    return 1.5255*ppu - 4.8468 ## Magic number to estimate fresh mass

def equationDW(ppu):
    return 0.2642*ppu - 0.8814 ## Magic number to estimate dry mass
        

        
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
    LOGFP = open(photoLogFN,'a')
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
    LOGFP = open(sampleLogFN,'a')
    if sampleName == "PutSampleName": sampleName = "Unknown"
    wList = [sampleName,str(Nsample),str(excOutlier.get())]
    for entryTarget in [entryAvgPPU, entryStdevPPU,entryAvgFW, entryAvgDW]:
        targetValue = entryTarget.get()
        if not targetValue.replace('.','').isdigit(): return 0
        wList.append(targetValue)
    wList.append(str(datetime.datetime.now()))
    LOGFP.write('\t'.join(wList)+'\n')
    print("Save sample record completed")
    LOGFP.close()        

def _on_close_root():
    global TEMPPATH, root
    if len(glob.glob("TEMPPATH" + os.sep + '*')) == 0:
        os.removedirs(TEMPPATH)
    root.destroy()
    


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

root.protocol("WM_DELETE_WINDOW",_on_close_root)
root.mainloop()
