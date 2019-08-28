import cv2
import numpy as np
import matplotlib.pyplot as plt
import pickle

ix,iy = -1,-1
pts = []
kb = cv2.imread("clavier.jpg")

def addMouseCoord(event,x,y,flags,param) :
    global ix,iy,pts
    if event == cv2.EVENT_LBUTTONDOWN :
        [ix,iy] = x,y
        pts.append([ix,iy])

cv2.namedWindow('Keyboard')
cv2.setMouseCallback('Keyboard',addMouseCoord)
cv2.imshow('Keyboard',kb)
k = cv2.waitKey(0) & 0xFF

cv2.destroyAllWindows()

print(pts)
