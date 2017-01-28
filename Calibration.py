# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 22:34:31 2016

@author: gologius
"""

# -*- coding: utf-8 -*-

import numpy as np
import cv2

VIDEO_FILENAME = "input\\video.MP4"
STEP = 50 #動画からフレームを抽出する間隔
PATTERN_SHAPE = (5,3) #circle gridのCircle個数
PATTERN_SIZE = 200 #Circleの中心間隔 mm
PATTERN_FLOAT = 12.0 #板の厚み分 mm

#パターンの世界座標計算
def calcObjPoints():
    
    results = []
    for y in xrange(PATTERN_SHAPE[1]):
        for x in xrange(PATTERN_SHAPE[0]):
            results.append((x*PATTERN_SIZE,y*PATTERN_SIZE, PATTERN_FLOAT))
            
    results = np.array(results, dtype=np.float32).reshape((PATTERN_SHAPE[0]*PATTERN_SHAPE[1], 1, 3))
    return results

#ユーザーによる決定
def decideLoop(debug = True):
    if not debug:
        return True
    
    print "use this ? press key o or x"
    decision = False
    while True:
        key = cv2.waitKey(1)
        if key == ord("o"):
            decision = True
            break
        elif key == ord("x"):
            decision = False
            break
        
    return decision

#ビデオ読み込み
video = cv2.VideoCapture(VIDEO_FILENAME)
if (video.isOpened() == False):
    print "video is not opened"    
frameNum = int(video.get(cv2.CAP_PROP_FRAME_COUNT))         
fps = video.get(cv2.CAP_PROP_FPS)         
imgShape = (0,0) #後で使用
print "frame num ", frameNum , " fps ", fps 

#画像解析ループ
objPoints = []
imgPoints = []
useImgs = []
precalcPoints = calcObjPoints() #世界座標は変わらないので予め計算しておく
for i in xrange(frameNum):
    ret, img = video.read()
    if ret == False or not i % STEP ==0:
        continue
    elif i==0:
        imgShape = img.shape
    
    work = np.array(img) #コピー
    found, corners = cv2.findCirclesGrid(img, PATTERN_SHAPE, flags=cv2.CALIB_CB_SYMMETRIC_GRID +cv2.CALIB_CB_CLUSTERING)
    if found:
        #検出結果を見て採用するかを決定
        cv2.drawChessboardCorners(work, PATTERN_SHAPE, corners, found)
        cv2.imshow("img", work)
        
        print len(corners)
        print corners
        ok = decideLoop(True)
        if ok:
            print "success "
            #保存
            imgPoints.append(corners)
            objPoints.append(precalcPoints)
            useImgs.append(work)
    
    else:
        print "failed"
        cv2.imshow("img", work)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    
video.release()
cv2.destroyAllWindows()

print "start calibration"
rms, K, dist, r, t = cv2.calibrateCamera(objPoints, imgPoints, (imgShape[1],imgShape[0]), None, None, flags=cv2.CALIB_USE_INTRINSIC_GUESS) #+@で内部パラメータの初期値を設定できる
print "finish calibration"

print rms
print K 
print dist 

#debug
for (i, img) in enumerate(useImgs):
    
    w_points = np.array( [(0.0, 0.0, 0.0), (1000.0, 0.0, 0.0), (0.0, 1000.0, 0.0), (1000.0, 1000.0, 0.0)] ) #世界座標
    i_points, jac = cv2.projectPoints(w_points, r[i], t[i], K, dist) #画像座標
    i_points = i_points.reshape(len(i_points),2)    
    i_points = i_points * -1.0
    undist_img = cv2.undistort(img, K, dist)     
   
    #描画
    for p in i_points:
        x, y = p
        cv2.circle(undist_img, (int(x),int(y)), 1, (255,255,0), 4)
    cv2.line(undist_img,(int(i_points[0,0]),int(i_points[0,1])),(int(i_points[1,0]),int(i_points[1,1])), (255,0,255), 1)
    cv2.line(undist_img,(int(i_points[0,0]),int(i_points[0,1])),(int(i_points[2,0]),int(i_points[2,1])), (255,0,255), 1)
    cv2.line(undist_img,(int(i_points[0,0]),int(i_points[0,1])),(int(i_points[3,0]),int(i_points[3,1])), (255,0,255), 1)        
    print i_points[0]    
    
    cv2.imshow("debug", undist_img)                
    key = cv2.waitKey(-1)
    if key == ord("q"):
        break

cv2.destroyAllWindows()

#結果保存