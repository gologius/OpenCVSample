# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 19:55:44 2017

@author: gologius
"""

u"""
動画をトリミングするためのスクリプト
"""

import cv2
import numpy as np

readFilePath = r"movie.MP4"
saveFilePath = r"movie_trim.avi"
step = 480

#動画読み込み
video = cv2.VideoCapture(readFilePath)
frameNum = int(video.get(cv2.CAP_PROP_FRAME_COUNT))    
fps = video.get(cv2.CAP_PROP_FPS)            
print "frame num ", frameNum, " fps ", fps  

#操作ループ
lookIndex = 0
remainIndices = np.ones(frameNum) > 0 #TF行列にする
isSelectRange = False
rangeStart = 0
rangeEnd = 0
while True:
    
	#指定されたフレームに移動し，画像を一枚読み込む
    video.set(cv2.CAP_PROP_POS_FRAMES, lookIndex)    
    ret, img = video.read()
    if not ret:
        lookIndex += 1
        continue
    
	#削除対象の画像は全体的に色を変える
    workimg = np.array(img)
    if remainIndices[lookIndex] == False:
        workimg -= 100
    
    cv2.putText(workimg, str(lookIndex), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200,0,200), 2);
    if isSelectRange:    
        cv2.putText(workimg, "SELECT MODE", (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200,0,200), 2);
    
    cv2.imshow("img", workimg)
    
    key = cv2.waitKey(-1)
	#フレーム移動
    if key == ord("a"):
        lookIndex -= step
        if lookIndex < 0:
            lookIndex = 0
    elif key == ord("d"):
        lookIndex += step 
        if lookIndex > frameNum-1:
            lookIndex = frameNum-1     
	#削除範囲指定
    elif key == ord("w"):
        if not isSelectRange:            
            print "start range select"
            isSelectRange = True                
            rangeStart = lookIndex
        else:
            print "end range select"
            rangeEnd = lookIndex
            remainIndices[min([rangeStart,rangeEnd]):max([rangeStart,rangeEnd])] = False
            isSelectRange = False            
    elif key == ord("c"):
        print "reset"
        remainIndices = np.ones(frameNum) > 0 #TF行列にする
	#動画保存
    elif key == ord("s"):
        print "start save"
        #保存ループ
        record = cv2.VideoWriter(saveFilePath, cv2.VideoWriter_fourcc(*'XVID'), fps, (img.shape[1], img.shape[0]))
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)   
        
        for i in xrange(frameNum):
            if i % 1000 == 0:
                print "finish frame ", i
            ret, saveimg = video.read()
            if ret and remainIndices[i]:            
                record.write(saveimg)    
            
        record.release()
        print "end save"
    if key == ord("q"):
        break        

video.release()    
cv2.destroyAllWindows()
