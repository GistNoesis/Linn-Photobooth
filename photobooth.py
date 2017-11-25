import numpy as np
import cv2
import evdev
from threading import Thread
import threading
import time
from queue import Queue,PriorityQueue
from datetime import datetime
from datetime import timedelta
import subprocess
import math

from collections import deque
import serial
import sys
import operator

from queue import Empty
import glob
import os
import re

import CMT
import PID
import pose
import gc
import json

ang = 0
ratio = 1.0
useDummySerial = True
serialPort = "/dev/ttyUSB0"
speedmult = 20.0

allTakenPictures = []
cttoid = {}
pictureIndex = 0
artIndex = 0
nbTakenPictures = 0
controllerPlugged = False

nbFutureFrames = 10
nbPastFrames = 10

styles = [("perle","Meisje_met_de_parel.jpg"),
          ("laitiere","vermeer-milmaid.jpg"),
          ("sketch","sketch.png"),
          ("mondrian","mondrian.jpg"),
          ("monet1","monet1.jpg"),
          ("monalisa","oneline-mona-lisa-joconde-vinci.jpg"),
          ("composition_vii","composition_vii.jpg"),
          ("starry_night","starry_night.jpg"),
          ("the_wave","wave.jpg"),
          ("candy","candy.jpg"),
          ("feathers","feathers.jpg"),
          ("la_muse","la_muse.jpg"),
          ("mosaic","mosaic.jpg"),
          ("the_scream","the_scream.jpg"),
          ("udnie","udnie.jpg"),
          ("Avatarjakeneytiri","Avatarjakeneytiri.jpg"),
          ("albrecht-durer","albrecht-durer.jpg"),
           ("lisa_simpson","lisa_simpson.jpg"),
           ("marc-chagall-wallpaper","marc-chagall-wallpaper.jpg"),
           ("low-poly-character-dinges","low-poly-character-dinges.jpg"),
           ("Peasant-039-s-Head-Renaissance-Oil-Painting-LP03957","Peasant-039-s-Head-Renaissance-Oil-Painting-LP03957.jpg"),
           ("mickey","mickey.jpg"),
           ("pieter-bruegel-les-chasseurs-dans-la-neige","pieter-bruegel-les-chasseurs-dans-la-neige.jpg")]

#2017-11-02_17_09_16.268410
datetimeformat = "%Y-%m-%d_%H_%M_%S.%f"

def pathFromTimeAndFolder(ct,folder):
    return folder + "/pic" + str(ang)+"_" + ct.strftime(datetimeformat) + ".jpg"

def filenameFromTime( ct ):
    return  "pic" + str(ang) +"_"+ ct.strftime(datetimeformat) + ".jpg"

def artnameFromTime( ct ,style):
    return "pic" + str(ang) +"_"+ ct.strftime(datetimeformat)+ "@" + style + ".jpg"

def artPath(ct,style):
    return "persistent/art/pic" + str(ang) +"_"+ ct.strftime(datetimeformat) + "@" + style + ".jpg"


def parseTimeFromString( s ):
    try:
        d = datetime.strptime(s,datetimeformat)
    except ValueError:
        d = None
    return d

epoch = datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0


def loadPreviousPictures(folder):
    global nbTakenPictures
    for name in sorted(glob.glob(folder+'/pic'+str(ang)+'*.jpg')):
        basename = os.path.basename(name)
        print(basename)
        m = re.search('pic'+str(ang)+'_(.+?).jpg', basename)
        if( m ):
            dt = m.group(1)
            print(dt)

            ct = parseTimeFromString( dt )
            print( ct )
            if( ct != None):
                allTakenPictures.append((ct, folder))
                cttoid[ct.strftime(datetimeformat)] = nbTakenPictures
                nbTakenPictures=nbTakenPictures+1

gamepadevents=Queue()
artQueue = Queue()

def initEnqueueStyles( folder):
    existingart = set( glob.glob(folder + '/pic' + str(ang) + '*.jpg') )
    for pict in allTakenPictures:
        ct = pict[0]
        print(pict)
        print(ct)
        for i in range(len(styles)):
            ap = artPath( ct,styles[i][0] )
            if( ap not in existingart):
                artQueue.put( (-unix_time_millis(ct),i, ct,folder,styles[i][0]))


loadPreviousPictures("persistent/photos")
initEnqueueStyles("persistent/art")
pictureIndex = max(len(allTakenPictures)-1,0)


class dummySerial():
    def write(self,val):
        #print("dummy Serial write ")
        return
    def __init__(self):
        self.x=0

    def inWaiting(self):
        return 0

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        return

def getSerial():
    if useDummySerial is True :
        return dummySerial()
    return serial.Serial(serialPort,115200,timeout=1)

def gamepadLoop():
    global controllerPlugged
    while(True):

        try:
            ## Initializing ##
            print("Finding ps3 controller...")
            devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
            for device in devices:
                print(device.name)
                if  device.name.startswith('PLAYSTATION(R)3 Controller') :
                    ps3dev = device.fn
                    controllerPlugged = True
                    print("found")

            gamepad = evdev.InputDevice(ps3dev)
            for event in gamepad.read_loop():
                if event.type == 3:  # A stick is moved
                    if event.code == 3:  # Y axis on right stick
                        print("axis0 :" + str(event.value))
                        gamepadevents.put( ("axis0",event.value) )

                    if event.code == 0:  # Y axis on right stick
                        print( "axis3 :" + str(event.value) )
                        gamepadevents.put( ("axis3",event.value))

                elif event.code==302:
                    if( event.type==1 and event.value==1):
                        print("croix down")
                        gamepadevents.put("croix down")
                    elif (event.type == 1 and event.value == 0):
                        print("croix up")
                        gamepadevents.put("croix up")
                elif event.code==303:
                    if( event.type==1 and event.value==1):
                        print("carre down")
                        gamepadevents.put("carre down")
                    elif (event.type == 1 and event.value == 0):
                        print("carre up")
                        gamepadevents.put("carre up")
                    else :
                        print(event)
                elif event.code==301:
                    if( event.type==1 and event.value==1):
                        print("rond down")
                        gamepadevents.put("rond down")
                    elif (event.type == 1 and event.value == 0):
                        print("rond up")
                        gamepadevents.put("rond up")
                    else :
                        print(event)
                elif event.code==300:
                    if( event.type==1 and event.value==1):
                        print("triangle down")
                        gamepadevents.put("triangle down")
                    elif (event.type == 1 and event.value == 0):
                        print("triangle up")
                        gamepadevents.put("triangle up")
                    else :
                        print(event)
                elif event.code==292:
                    if( event.type==1 and event.value==1):
                        print("up down")
                        gamepadevents.put("up down")
                    elif (event.type == 1 and event.value == 0):
                        print("up up")
                        gamepadevents.put("up up")
                elif event.code==294:
                    if( event.type==1 and event.value==1):
                        print("down down")
                        gamepadevents.put("down down")
                    elif (event.type == 1 and event.value == 0):
                        print("down up")
                        gamepadevents.put("down up")
                elif event.code==296:
                    if( event.type==1 and event.value==1):
                        print("L2 down")
                        gamepadevents.put("L2 down")
                    elif (event.type == 1 and event.value == 0):
                        print("L2 up")
                        gamepadevents.put("L2 up")
                elif event.code==297:
                    if( event.type==1 and event.value==1):
                        print("R2 down")
                        gamepadevents.put("R2 down")
                    elif (event.type == 1 and event.value == 0):
                        print("R2 up")
                        gamepadevents.put("R2 up")
                elif event.code==298:
                    if( event.type==1 and event.value==1):
                        print("L1 down")
                        gamepadevents.put("L1 down")
                    elif (event.type == 1 and event.value == 0):
                        print("L1 up")
                        gamepadevents.put("L1 up")
                elif event.code==299:
                    if( event.type==1 and event.value==1):
                        print("R1 down")
                        gamepadevents.put("R1 down")
                    elif (event.type == 1 and event.value == 0):
                        print("R1 up")
                        gamepadevents.put("R1 up")
                elif event.code==291:
                    if( event.type==1 and event.value==1):
                        print("start down")
                        gamepadevents.put("start down")
                    elif (event.type == 1 and event.value == 0):
                        print("start up")
                        gamepadevents.put("start up")
                elif event.code==288:
                    if( event.type==1 and event.value==1):
                        print("select down")
                        gamepadevents.put("select down")
                    elif (event.type == 1 and event.value == 0):
                        print("select up")
                        gamepadevents.put("select up")
                elif event.code==304:
                    if( event.type==1 and event.value==1):
                        print("play down")
                        gamepadevents.put("play down")
                    elif (event.type == 1 and event.value == 0):
                        print("play up")
                        gamepadevents.put("play up")
                #print(event)
        except FileNotFoundError:
            controllerPlugged = False
        except :
            controllerPlugged = False
            print("Caught it")
            print("Unexpected error:", sys.exc_info()[0])
            time.sleep(1)







def rotate_image_90(im, angle):
    if angle % 90 == 0:
        angle = angle % 360
        if angle == 0:
            return im
        elif angle == 90:
            return im.transpose((1,0, 2))[:,::-1,:]
        elif angle == 180:
            return im[::-1,::-1,:]
        elif angle == 270:
            return im.transpose((1,0, 2))[::-1,:,:]

    else:
        raise Exception('Error')


framesToSave = Queue()




def imageSavingThread():
    while( True ):
        (frame,ct,folder) = framesToSave.get()
        cv2.imwrite(pathFromTimeAndFolder(ct,folder), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 100])



def isPrioritary(pi,si):
    return abs(pi-pictureIndex)+abs(si-artIndex) <=1


def getMostPriorityArt():
    mycopy = []
    myannexcopy = []

    elem = artQueue.get()
    mycopy.append(elem)


    #currentPictureTime = allTakenPictures[pictureIndex][0]
    myannexcopy.append((not isPrioritary(cttoid[elem[2].strftime(datetimeformat)], elem[1]), abs((cttoid[elem[2].strftime(datetimeformat)] - pictureIndex)) , abs(elem[1] - artIndex)))

    while True:
        try:
            elem = artQueue.get(block=False)
        except Empty:
            break
        mycopy.append(elem)
        myannexcopy.append((not isPrioritary(cttoid[elem[2].strftime(datetimeformat)], elem[1]),
                            abs((cttoid[elem[2].strftime(datetimeformat)] - pictureIndex)), abs(elem[1] - artIndex)))

    index, value = min(enumerate(myannexcopy),key=operator.itemgetter(1) )

    for i in range(len(mycopy)):
        if( i != index ):
            artQueue.put(mycopy[i] )


    return mycopy[index]


def artProcessingThread( gpuId ):
    while(True):

        (totseconds,styleidx,ct,folder,style) = getMostPriorityArt()
        time.sleep(0.1)

        """
        imagename = pathFromTimeAndFolder(ct, folder)
        picture = cv2.imread(imagename)
        time.sleep(3)
        picstyle = picture.copy()
        cv2.putText(picstyle, style, (140, 900), cv2.FONT_HERSHEY_COMPLEX, 1,
                    (255, 255, 255), 5)

        cv2.imwrite( artPath(ct,style),picstyle,[int(cv2.IMWRITE_JPEG_QUALITY), 100] )
        """
        filename = filenameFromTime(ct)
        artname = artnameFromTime(ct,style)
        print (filename,style,artname)
        print(subprocess.call(["./remoteart.sh", filename, style, artname, str(gpuId) ]))

        if( len(allTakenPictures) > 0):
            if ct == allTakenPictures[pictureIndex][0] and styleidx == artIndex:
                gamepadevents.put("refresh art")





def enqueueStyles( ct,folder):
    for i in range(len(styles)):
        artQueue.put( (-unix_time_millis(ct),i, ct,folder,styles[i][0]))

thread = Thread(target = gamepadLoop)
thread.daemon = True
thread.start()

threaddiskwriter = Thread(target = imageSavingThread)
threaddiskwriter.daemon = True
threaddiskwriter.start()

threadartProcessing = Thread(target = artProcessingThread,args=([0]))
threadartProcessing.daemon = True
threadartProcessing.start()



threadartProcessing2 = Thread(target = artProcessingThread,args=([1]))
threadartProcessing2.daemon = True
threadartProcessing2.start()

currentExposure=250

def updateExposure():
    subprocess.call(["v4l2-ctl","-d","/dev/video0", "-c", "exposure_absolute="+str(currentExposure)])
    print("currentExposure : " + str(currentExposure))


uppressed=False
downpressed=False
timer =None


last10Pictures = deque()

def TakePicture( frame, currenttime, folder ):
    global pictureIndex
    global allTakenPictures
    global cttoid
    global nbTakenPictures
    allTakenPictures.append( (currenttime,folder) )
    cttoid[currenttime.strftime(datetimeformat)] = nbTakenPictures
    framesToSave.put( (frame,currenttime,folder))
    enqueueStyles(currenttime,folder)


def TakeExtraFrame( frame,currenttime ):
    framesToSave.put( (frame,currenttime, "persistent/extraframes") )

picture = None
smallRotPicture = None







printPhoto = 0
printArt = 0
confirmDelete = False


def getStyleImage():
    try:
        picture = cv2.imread("styles/"+ styles[artIndex][1] )

        picture = cv2.resize(picture, (fullframeSize[0],fullframeSize[1]), interpolation=cv2.INTER_AREA)
    except :
        picture = np.zeros((fullframeSize[1],fullframeSize[0],3),dtype="uint8")
    if picture is None:
        picture = np.zeros((fullframeSize[1], fullframeSize[0], 3), dtype="uint8")
    return picture


def selectDisplayedPhoto(index):
    if( len( allTakenPictures) == 0 ):
        return
    (ct,folder) = allTakenPictures[index]
    imagename = pathFromTimeAndFolder(ct,folder)
    picture = cv2.imread(imagename)
    displayPhoto( picture )


def selectArtPicture(index, indexStyle):
    if (len(allTakenPictures) == 0):
        picture=getStyleImage()
        displayArt(picture)
        return
    (ct, folder) = allTakenPictures[index]
    imagename = artPath(ct, styles[indexStyle][0])
    try:
        picture = cv2.imread(imagename)
    except :
        picture=getStyleImage()

    if picture is None:
        picture = getStyleImage()

    displayArt(picture)

fontColorBgr =(0,0,255)

def displayPhoto( img ):
    currentPic = cv2.resize(img, (0, 0), fx=ratio, fy=ratio)
    if( printPhoto == 1):
        cv2.putText(currentPic, "Press select to confirm print", (40, 200), cv2.FONT_HERSHEY_COMPLEX, 1, fontColorBgr, 5)
    elif (printPhoto == 2):
        cv2.putText(currentPic, "Added to print queue", (140, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 1,fontColorBgr, 5)
    if( confirmDelete is True):
        cv2.putText(currentPic, "Press Triangle to confirm deletion", (140, 300),
                    cv2.FONT_HERSHEY_COMPLEX, 1, fontColorBgr, 5)

    cv2.imshow("picture", currentPic)



def displayArt( img ):
    currentPic = cv2.resize(img, (0, 0), fx=ratio, fy=ratio)

    if (printArt == 1):
        cv2.putText(currentPic, "Press start to confirm print", (40, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 1,fontColorBgr, 5)
    elif (printArt == 2):
        cv2.putText(currentPic, "Added to print queue", (140, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 1, fontColorBgr, 5)

    cv2.imshow("art", currentPic)

def printPhotoJob(pictureIndex):
    print("Print photo")
    filename = pathFromTimeAndFolder( allTakenPictures[pictureIndex][0] ,"persistent/photos")
    print(subprocess.call(["lp", "-o", "media", filename]))
    with open("persistent/printedPhotos.txt", "a+") as myfile:
        myfile.write(filename + "\n")


def printArtJob(pictureIndex,artindex):
    print("Print art")
    filename = artPath(allTakenPictures[pictureIndex][0], styles[artindex][0])
    print(subprocess.call(["lp", "-o", "media", filename]))
    with open("persistent/printedPhotos.txt", "a+") as myfile:
        myfile.write(filename + "\n")


def ChangePrintArtToZero():
    global printArt
    if (printArt != 0):
        printArt = 0
        selectArtPicture(pictureIndex, artIndex)
    printArt = 0

def ChangePrintPhotoToZero():
    global printPhoto
    if (printPhoto != 0):
        printPhoto = 0
        selectDisplayedPhoto(pictureIndex)
    printPhoto=0

frameProcessed = 0
frameoflastpic = -10000
circularBuffer=deque()


def SavePastFrames(nbFramesToSave):
    co=0
    for (frame,ct) in reversed(circularBuffer):
        TakeExtraFrame(frame, ct)
        if(co > nbFramesToSave):
            break
        co=co+1


def moveCurrentPictureToDeletedFolder():
    global pictureIndex
    ct = allTakenPictures[pictureIndex][0]
    filename = filenameFromTime(ct)
    print( subprocess.call( ["mv","persistent/photos/"+filename,"persistent/deleted/"+filename]))
    del allTakenPictures[pictureIndex]
    pictureIndex = min( pictureIndex,len(allTakenPictures)-1)
    selectDisplayedPhoto(pictureIndex)
    selectArtPicture(pictureIndex, artIndex)

recording = False

def processEvents(frame ,currenttime,ser):
    global background
    global currentExposure
    global uppressed
    global downpressed
    global timer
    global pictureIndex
    global artIndex
    global printPhoto
    global printArt
    global frameProcessed
    global frameoflastpic
    global confirmDelete

    frameProcessed+=1
    circularBuffer.append( (frame,currenttime) )
    if( len( circularBuffer ) > nbPastFrames ):
        circularBuffer.popleft()


    while not gamepadevents.empty():
        ev = gamepadevents.get()
        if ev == "refresh art":
            selectArtPicture(pictureIndex, artIndex)
        elif ev == "select down":
            ChangePrintArtToZero()
            if (printPhoto == 1):
                printPhoto = 2
                printPhotoJob(pictureIndex)
            else:
                printPhoto = 1
            print("handling select tdown " + str(printArt))
            selectDisplayedPhoto(pictureIndex)
        elif ev == "start down":
            ChangePrintPhotoToZero()
            if( printArt == 1):
                printArt = 2
                printArtJob(pictureIndex,artIndex)
            else:
                printArt = 1
            print("handling start down " + str(printArt) )
            selectArtPicture( pictureIndex,artIndex)
        elif ev == "start up" or ev=="select up":
            print("startorselect up")
        elif isinstance(ev,tuple):
            pass
        else:
            print( ev )
            ChangePrintArtToZero()
            ChangePrintPhotoToZero()

        if( ev == "refresh art" ):
            pass
        elif isinstance(ev,tuple):
            pass
        elif ( ev == "triangle down" or ev == "triangle up"):
            pass
        else :
            confirmDelete = False

        if ev == "croix down":
            TakePicture(frame,currenttime,"persistent/photos")
            pictureIndex = len(allTakenPictures)-1
            displayPhoto( frame )
            selectArtPicture(pictureIndex,artIndex)
            SavePastFrames(nbPastFrames)
            frameoflastpic=frameProcessed

        elif ev == "up down":
            uppressed=True
        elif ev == "up up":
            uppressed=False
        elif ev == "down down":
            downpressed=True
        elif ev == "down up":
            downpressed=False
        elif ev == "carre down":
            timer=datetime.now()+ timedelta(seconds=5)
        elif ev == "triangle down":
            if( confirmDelete ):
                confirmDelete = False
                moveCurrentPictureToDeletedFolder()
            else:
                confirmDelete = True
                selectDisplayedPhoto(pictureIndex)
        elif ev == "L1 down":
            pictureIndex = max(0,pictureIndex-1)
            selectDisplayedPhoto(pictureIndex)
            selectArtPicture(pictureIndex, artIndex)
        elif ev == "R1 down":
            pictureIndex = min(len(allTakenPictures)-1,pictureIndex+1)
            selectDisplayedPhoto(pictureIndex)
            selectArtPicture(pictureIndex, artIndex)
        elif ev == "L2 down":
            artIndex = max(0,artIndex-1)
            selectArtPicture( pictureIndex,artIndex)
        elif ev == "R2 down":
            artIndex = min(len(styles)-1,artIndex+1)
            selectArtPicture( pictureIndex,artIndex)
        elif isinstance(ev,tuple) and ev[0] == "axis0":
            val = ev[1]
            if abs(val) > 15:
                val = (val * speedmult)
            else:
                val = 0
            # print("computed halfpulse :" +str(val))
            valw = "xs" + str(val) + '\n'
            print("axis0write :" + str(valw))
            ser.write(valw.encode('utf-8'))
        elif isinstance(ev, tuple) and ev[0] == "axis0r":
            val = ev[1]
            # print("computed halfpulse :" +str(val))
            valw = "xr" + str(int(val)) + '\n'
            print("axis0write :" + str(valw))
            ser.write(valw.encode('utf-8'))
        elif isinstance(ev, tuple) and ev[0] == "axis0a":
            val = ev[1]
            # print("computed halfpulse :" +str(val))
            valw = "xa" + str(int(val)) + '\n'
            print("axis0write :" + str(valw))
            ser.write(valw.encode('utf-8'))

        elif isinstance(ev,tuple) and ev[0] == "axis3":
            val = ev[1]
            if abs(val) > 15:
                val = ( val * speedmult)
            else:
                val = 0
            # print("computed halfpulse :" +str(val))
            valw = "ys" + str(val) + '\n'
            print("axis3write :" + str(valw))
            ser.write(valw.encode('utf-8'))
        elif isinstance(ev, tuple) and ev[0] == "axis3r":
            val = ev[1]
            # print("computed halfpulse :" +str(val))
            valw = "yr" + str(int(val)) + '\n'
            print("axis3write :" + str(valw))
            ser.write(valw.encode('utf-8'))
        elif isinstance(ev, tuple) and ev[0] == "axis3a":
            val = ev[1]
            # print("computed halfpulse :" +str(val))
            valw = "ya" + str(int(val)) + '\n'
            print("axis3write :" + str(valw))
            ser.write(valw.encode('utf-8'))


    if( uppressed ==True ):
        if (currentExposure < 2000):
            currentExposure += 5
            updateExposure()
    if (downpressed == True):
        if (currentExposure > 9):
            currentExposure -= 5
            updateExposure()

    if timer != None:
        dt = timer - datetime.now()
        if dt.total_seconds() < 0 :
            timer= None
            TakePicture(frame,currenttime,"persistent/photos")
            frameoflastpic = frameProcessed
            pictureIndex = len(allTakenPictures) - 1
            displayPhoto(frame)
            selectArtPicture(pictureIndex, artIndex)
            SavePastFrames(nbPastFrames)

    if( recording is True or (frameProcessed > frameoflastpic and frameProcessed < frameoflastpic + nbFutureFrames) )  :
        TakeExtraFrame(frame,currenttime)






cap = cv2.VideoCapture(0)

cap.set(3,1920)
cap.set(4,1080)


#cap.set( cv2.CAP_PROP_GAIN,-1.3)
#cap.set( cv2.CAP_PROP_EXPOSURE,200)


'''
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(20,20))

fgbg = cv2.createBackgroundSubtractorMOG2(500,5.0,True)
#fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
#fgbg = cv2.createBackgroundSubtractorKNN(300,0.1,False)

'''
ret, background = cap.read()


ratiovertical = 1080/1920
fullVerticalSize = (1080,1920)
verticalframeSize = (int(math.ceil(fullVerticalSize[0]*ratiovertical)),int(math.ceil(fullVerticalSize[1]*ratiovertical)))


ratiohorizontal = 0.5 #/1.14 divide by this ratio for hd ready resolution
fullHorizontalSize = (1920,1080)
horiontalframeSize = (int(math.ceil(fullHorizontalSize[0]*ratiohorizontal)),int(math.ceil(fullHorizontalSize[1]*ratiohorizontal)))



cv2.namedWindow("frame");
cv2.namedWindow("picture");
cv2.namedWindow("art");
cv2.namedWindow("doc");
cv2.namedWindow("facetrack");
#cv2.namedWindow("title");


#title = cv2.imread("title.png")
#cv2.imshow("title",title)
ps3 = cv2.imread("ps3.jpg")





if( ang == 0 or ang == 180):
    ratio = ratiohorizontal
    fullframeSize = fullHorizontalSize
    frameSize = horiontalframeSize
    cv2.moveWindow("frame", 0, 0)
    cv2.moveWindow("picture", int(math.ceil(1920 * ratio)), 0)
    cv2.moveWindow("art", 0, int(math.ceil(1080*ratio)))
    cv2.moveWindow("doc",int(math.ceil(1920 * ratio)),int(math.ceil(1080*ratio)) )
    cv2.moveWindow("facetrack", int(math.ceil(1920 * ratio)), int(math.ceil(1080 * ratio)))
    #cv2.moveWindow("title", 0, int(2*math.ceil(1080 * ratio)))
    #cv2.resizeWindow("title", 2*frameSize[0], 40)
    smallps3 = cv2.resize(ps3, (0, 0), fx=ratio, fy=ratio)
    cv2.imshow("doc", smallps3)


else:
    ratio = ratiovertical
    fullframeSize = fullVerticalSize
    frameSize = verticalframeSize
    cv2.moveWindow("frame", 0, 0)
    cv2.moveWindow("picture", int(math.ceil(1080 * ratio)), 0)
    cv2.moveWindow("art", int(math.ceil(2 * 1080 * ratio)), 0)


cv2.resizeWindow("frame",frameSize[0],frameSize[1])
cv2.resizeWindow("picture",frameSize[0],frameSize[1])
cv2.resizeWindow("art",frameSize[0],frameSize[1])
cv2.resizeWindow("doc",frameSize[0],frameSize[1])

cv2.resizeWindow("facetrack",frameSize[0],frameSize[1])

last10Pictures.append( background )
print(background.shape)

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

faceTracking = False

cmtInitialized = False

CMT = CMT.CMT()

framesToTrack = Queue()

framesToDisplay = Queue()

def queue_get_all(q,items = None):
    if items is None:
        items = []
    while 1:
        try:
            items.append(q.get_nowait())
        except :
            break
    return items

def FaceTrackinThread():

    global cmtInitialized
    global faceTracking
    global ratio
    pidx = None
    pidy = None

    isLost=False
    while( True) :

        allItems = [framesToTrack.get()]

        allItems = queue_get_all(framesToTrack,allItems)
        (rot, ct,pos) = allItems[-1]
        small = cv2.resize(rot, (0, 0), fx=ratio, fy=ratio)


        if (faceTracking):
            ftratio = 0.5
            ftinp =  cv2.resize(rot, (0, 0), fx=ftratio, fy=ftratio)

            gray = cv2.cvtColor(ftinp, cv2.COLOR_BGR2GRAY)
            if (cmtInitialized is False):
                faces = face_cascade.detectMultiScale(gray, 1.2, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(small, (int(x * ftratio/ratio), int(y * ftratio/ratio)),
                                  (int((x + w) * ftratio/ratio), int((y + h) * ftratio/ratio)), (255, 0, 0), 2)

                    try:
                        CMT.initialise(gray, (x, y), (x + w, y + h))
                        cmtInitialized = True
                        t = ct
                        pidx = PID.PIDController(t, 5.0, 0.0, 1.0)
                        pidy = PID.PIDController(t, 5.0, 0.0, 1.0)
                        isLost=False
                    except:
                        print("CMT init error Caught")
                        print("Unexpected error:", sys.exc_info()[0])
                        pass
                    break

            if (cmtInitialized is True):
                try:
                    CMT.process_frame(gray)
                    if CMT.has_result:
                        target = np.array([small.shape[0] *ratio / ftratio / 4.0, small.shape[1] *ratio / ftratio / 2.0])

                        cv2.rectangle(small, (int(CMT.tl[0] * ftratio/ratio), int(CMT.tl[1] * ftratio/ratio)),
                                      (int(CMT.br[0] * ftratio/ratio), int(CMT.br[1] * ftratio/ratio)), (255, 0, 0), 2)
                        center = [(CMT.tl[1] + CMT.br[1]) / 2, (CMT.tl[0] + CMT.br[0]) / 2]
                        diff = (center - target) * ratio
                        print(diff)
                        sf = 10.0
                        ry = - sf * diff[0]
                        rx = - sf * diff[1]

                        t = ct
                        pidy.AppendPoint(t, -diff[0])
                        pidx.AppendPoint(t, -diff[1])

                        #We use here a relative movement strategy so we don't need the position reading from the steppers
                        #Look at the deep learning case for an example of using absolute positionning
                        if (np.sqrt(rx * rx + ry * ry) > 20 * sf):
                            gamepadevents.put(("axis0r", pidy.output))
                            gamepadevents.put(("axis3r", pidx.output))
                        isLost=False
                    else:
                        isLost = True
                except :
                    print("CMT error Caught ")
                    print("Unexpected error:", sys.exc_info()[0])
        #cv2.imshow("facetrack",small)
        framesToDisplay.put(("facetrack",small.copy() ))


def FaceTrackinThreadDeepLearning():

    global faceTracking
    global ratio
    global background
    isLost=False
    t = time.time()
    pidx = PID.PIDController(t, 4.0, 0.0, 0.1)
    pidy = PID.PIDController(t, 4.0, 0.0, 0.1)

    context = pose.getContext()
    socket = pose.getSocket(context)

    while( True) :
        if( recording ):
            print("Currently recording")

        allItems = [framesToTrack.get()]

        allItems = queue_get_all(framesToTrack,allItems)
        (rot, ct,pos) = allItems[-1]
        small = cv2.resize(rot, (0, 0), fx=ratio, fy=ratio)


        if (faceTracking):
            ftratio = 1.0
            ftinp =  cv2.resize(rot, (0, 0), fx=ftratio, fy=ftratio)


            try:
                poskp = pose.getPoseFromImage(socket, ftinp)
                featureNum = 1
                if len( poskp ) > 0 and poskp[0][1]["score"] > 0.3 :
                    tl = (poskp[0][featureNum]["x"]*ratio/ftratio-10,poskp[0][featureNum]["y"]*ratio/ftratio-10)
                    br = (poskp[0][featureNum]["x"]*ratio/ftratio + 10, poskp[0][featureNum]["y"] *ratio/ftratio + 10)
                    print("topleft :")
                    print(tl)
                    print("bottomright :")
                    print(br)
                    target = np.array([small.shape[0] / 2.0, small.shape[1] / 2.0])

                    cv2.rectangle(small, (int(tl[0] ), int(tl[1] )),
                                  (int(br[0] ), int(br[1] )), (255, 0, 0), 2)


                    center = [(tl[1] + br[1]) / 2, (tl[0] + br[0]) / 2]
                    diff = (center - target)
                    print( "diff : " + str(diff))
                    #print(diff)
                    sf = 10.0
                    ry = - sf * diff[0]
                    rx = - sf * diff[1]

                    t = ct
                    pidy.AppendPoint(t, -diff[0])
                    pidx.AppendPoint(t, -diff[1])
                    if pos is None:
                        if (np.sqrt(rx * rx + ry * ry) > 20 * sf):
                            gamepadevents.put(("axis0r", pidy.output))
                            gamepadevents.put(("axis3r", pidx.output))
                    else:
                        if (np.sqrt(rx * rx + ry * ry) > 20 * sf):
                            gamepadevents.put(("axis0a",pos[0] + pidy.output ))
                            gamepadevents.put(("axis3a", pos[1] + pidx.output))

                    isLost=False
                else:
                    isLost = True
            except :
                print("FaceTrackinThreadDeepLearning error Caught ")
                print("Unexpected error:", sys.exc_info()[0])
        #cv2.imshow("facetrack",small)
        framesToDisplay.put(("facetrack",small.copy()))



threadFaceTracking = Thread(target = FaceTrackinThread)
threadFaceTracking.daemon = True
threadFaceTracking.start()



lastSrqReadIndex =0

psrq =[]



with getSerial() as ser:
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        # Our operations on the frame come here
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        #fgmask = fgbg.apply(frame)

        #if ret is False :
        #    time.sleep(0.001)
        #    continue


        srq = Queue()

        if (ser.inWaiting() > 0):  # if incoming bytes are waiting to be read from the serial input buffer
            #data_str = ser.read(ser.inWaiting()).decode('ascii')  # read the bytes and convert from binary array to ASCII
            data_str = ser.read(ser.inWaiting())
            characters = list(data_str)
            for i in characters:
                srq.put(i)
            #print(data_str, end='')
            print(srq.qsize())
        ev = []
        delim = ord('\n')
        partial = []
        while 1:
            try:
                c = srq.get_nowait()
                if( c == delim):
                    psrq.extend(partial)
                    ev.append( list(psrq) )
                    psrq.clear()
                    partial.clear()
                else:
                    partial.append(c)
            except:
                psrq.extend(partial)
                break

        currentPosition = None
        #print("len(ev) : "+ str(len(ev)))
        parsedEvts = []
        for event in ev :
            eventstr = ''.join([chr(c) for c in event])
            try:
                obj= json.loads(eventstr)
                parsedEvts.append(obj)
            except:
                print("json error Caught ")
                print("Unexpected error:", sys.exc_info()[0])

        for i in range(len(parsedEvts)-1,-1,-1):
            e = parsedEvts[i]
            #print(e)
            if "pos" in e:
                currentPosition = e["pos"]
                break


        rot = rotate_image_90(frame,ang)
        small = cv2.resize(rot, (0, 0), fx=ratio, fy=ratio)
        #print("current position : " + str(currentPosition))

        framesToTrack.put((rot.copy(),time.time(),currentPosition))



        if timer != None:
            dt = timer - datetime.now()
            if dt.total_seconds() >  0:
                cv2.putText(small, "{0:.2f}".format(dt.total_seconds()), (140, 200), cv2.FONT_HERSHEY_COMPLEX, 4, (255,255,255),5)

        if( controllerPlugged is False):
            cv2.putText(small, "Press Play Button ", (40, 200), cv2.FONT_HERSHEY_COMPLEX, 1,
                        (255, 255, 255), 5)
            cv2.putText(small, "(between select and start)", (40, 300), cv2.FONT_HERSHEY_COMPLEX, 1,
                        (255, 255, 255), 5)

            cv2.putText(small, "to turn controller on", (40, 400),
                        cv2.FONT_HERSHEY_COMPLEX, 1,
                        (255, 255, 255), 5)

        cv2.imshow('frame', small)

        frames=queue_get_all(framesToDisplay)

        #for (name,img) in frames:
        #cv2.imshow(frames[-1][0],frames[-1][1])
        renderednames = set()
        #only display most recent

        for i in range( len(frames)-1,-1,-1 ):
            (name,img) = frames[i]
            if( name not in renderednames ):
                renderednames.add(name)
                cv2.imshow(name, img)


        processEvents(rot, datetime.now(),ser)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        if key & 0xFF == ord(' '):
            gamepadevents.put("croix down")
        if key > 0:
            print(key)
        if key == 83:
            gamepadevents.put( ("axis3",40))
            gamepadevents.put(("axis0", 0))
        if key == 81:
            gamepadevents.put( ("axis3",-40))
            gamepadevents.put(("axis0", 0))
        if key == 82:
            gamepadevents.put( ("axis0",40))
            gamepadevents.put(("axis3", 0))
        if key == 84:
            gamepadevents.put( ("axis0",-40))
            gamepadevents.put(("axis3", 0))
        if key == 226:
            gamepadevents.put( ("axis0",0) )
            gamepadevents.put( ("axis3",0))

        if key & 0xFF == ord('r'):
            #recording = not recording
            print("Recording : " + str(recording))

        if key & 0xFF == ord('f'):
            faceTracking = not faceTracking
            cmtInitialized = False
            if faceTracking == False:
                gamepadevents.put(("axis0", 0.0))
                gamepadevents.put(("axis3", 0.0))







# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

