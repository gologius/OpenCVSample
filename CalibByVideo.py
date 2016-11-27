# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 22:34:31 2016

@author: Koji
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
    for x in xrange(PATTERN_SHAPE[0]):
        for y in xrange(PATTERN_SHAPE[1]):
            results.append((x*PATTERN_SIZE,y*PATTERN_SIZE, 12.0))
            
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
    useImgs.append(work)
    found, corners = cv2.findCirclesGrid(img, PATTERN_SHAPE, flags=cv2.CALIB_CB_SYMMETRIC_GRID +cv2.CALIB_CB_CLUSTERING)
    if found:
        #検出結果を見て採用するかを決定
        cv2.drawChessboardCorners(work, PATTERN_SHAPE, corners, found)
        cv2.imshow("img", work)
        ok = decideLoop(False)
        if ok:
            print "success"
            #保存
            imgPoints.append(corners)
            objPoints.append(precalcPoints)
    else:
        print "failed"
        cv2.imshow("img", work)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    
video.release()
cv2.destroyAllWindows()

rms, K, dist, r, t = cv2.calibrateCamera(objPoints, imgPoints, (imgShape[1],imgShape[0]), None, None, flags=cv2.CALIB_USE_INTRINSIC_GUESS) #+@で内部パラメータの初期値を設定できる

print rms
print K 
print dist 

for (i, img) in enumerate(useImgs):
    
    #描画
    
    origin = cv2.projectPoints((0.,0.,0.), r[i], t[i], K, dist)

    cv2.circle(img, origin, 4)

    cv2.imshow("debug", img)                
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

cv2.destroyAllWindows()

#結果保存