import cv2
import numpy as np
from pynput.mouse import Button ,Controller
import wx

mouse=Controller()
app=wx.App()
(sx,sy)=wx.GetDisplaySize() 
cap=cv2.VideoCapture(0) 
(camx,camy)=(320,240) 
cap.set(3,camx)
cap.set(4,camy)
DampingFactor=2
pinchFlag=0 
openx,openy,openw,openh=(0,0,0,0)
mLocOld=np.array([0,0]) #Setting initial values to zero

#range for HSV (green color)
lowerBound=np.array([33,70,30])
upperBound=np.array([102,255,255])

#Kerenel
kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))

while True:

    _,img=cap.read() 
    img=cv2.resize(img,(340,240))
    
    imgHSV=cv2.cvtColor(img,cv2.COLOR_BGR2HSV) 
    mask=cv2.inRange(imgHSV,lowerBound,upperBound) 
    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernelOpen)
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
    maskFinal=maskClose
    _,conts,_=cv2.findContours(maskFinal,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) 

    #Once 2 objects are detected the below logic is followed
    if(len(conts)==2):
        
        if(pinchFlag==1):
            pinchFlag=0
            mouse.release(Button.left)
            
        x1,y1,w1,h1=cv2.boundingRect(conts[0])
        x2,y2,w2,h2=cv2.boundingRect(conts[1])
        cv2.rectangle(img,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
        cv2.rectangle(img,(x2,y2),(x2+w2,y2+h2),(255,0,0),2)
        [cx1,cy1]=[int(x1+w1/2),int(y1+h1/2)]
        [cx2,cy2]=[int(x2+w2/2),int(y2+h2/2)]
        cv2.line(img,(cx1,cy1),(cx2,cy2),(255,0,0),2)
        [cx,cy]=[int((cx1+cx2)/2),int((cy1+cy2)/2)]
        cv2.circle(img,(cx,cy),2,(0,0,255),2)

        mouseLoc=np.array([cx,cy])/DampingFactor #To increase smoothness of mouse movement and unnecessary movement we introduced damping factor
        [x,y] = mouseLoc
        mouse.position=(sx-int((x*sx)/camx),int((y*sy)/camy))
        while mouse.position!=(sx-int((x*sx)/camx),int((y*sy)/camy)):
            pass

        #these variables were added so that we get the outer rectangle that combines both objects
        openx,openy,openw,openh=cv2.boundingRect(np.array([[[x1,y1],[x1+w1,y1+h1],[x2,y2],[x2+w2,y2+h2]]]))

    #when there's only when object detected we follow below logic  
    elif(len(conts)==1):
        x,y,w,h=cv2.boundingRect(conts[0])
        # we check first and we allow the press of left mouse button  if it's not pressed yet
        #we did that to avoid the continues pressing of left button of mouse
        if(pinchFlag==0):

            if(abs((w*h-openw*openh)*100/(w*h))<30): 
                pinchFlag=1 
                mouse.press(Button.left)
                openx,openy,openw,openh=(0,0,0,0)

        #this else was added so that if there's only one object detected it will not act as a mouse and we stop movement of mouse cursor
        else:
            x,y,w,h=cv2.boundingRect(conts[0])
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            [cx,cy]=[int(x+w/2),int(y+h/2)]
            cv2.circle(img,(cx,cy),int((w+h)/4),(0,0,255),2)
            
            mouseLoc=np.array([cx,cy])/DampingFactor #To increase smoothness of mouse movement and unnecessary movement we introduced damping factor
            [x,y] = mouseLoc
            mouse.position=(sx-int((x*sx)/camx),int((y*sy)/camy))
            while mouse.position!=(sx-int((x*sx)/camx),int((y*sy)/camy)):
                pass

    #showing the results 
    cv2.imshow("(By 19DCS103 & 19DCS106)",img)
    cv2.waitKey(5)
