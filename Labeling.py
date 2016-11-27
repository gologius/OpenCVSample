# -*- coding: utf-8 -*-

import cv2
import numpy as np


img = np.zeros((500,500,3),dtype=np.uint8)
for i in xrange(1,5):
    img = cv2.circle(img, (i*80,i*80), 5, (255,255,255), -1)     
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

labelnum, labelimg, contours, GoCs = cv2.connectedComponentsWithStats(gray)

for label in xrange(1,labelnum):
    x,y = GoCs[label]
    img = cv2.circle(img, (int(x),int(y)), 1, (0,0,255), -1)    
    
    x,y,w,h,size = contours[label]
    img = cv2.rectangle(img, (x,y), (x+w,y+h), (255,255,0), 1)    
    
    
print "label num ", labelnum 
print "contours ", contours
print "Gravity of Centers ", GoCs
cv2.imshow("img", img)
cv2.waitKey(-1)
cv2.imwrite("labeling.png",img)