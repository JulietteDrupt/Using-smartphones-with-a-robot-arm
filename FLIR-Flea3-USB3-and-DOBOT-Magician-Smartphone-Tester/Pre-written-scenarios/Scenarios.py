import cv2
import numpy as np
import math
import Dobotfunctions as Dfonct
import screen

#--------------------------------------------IMAGE-COMPARISON----------------------------------------

# Brute-Force Matching with ORB Descriptors

def compareToIm(img1,img2) :
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    ratio = 0
    # Initiate SIFT detector
    orb = cv2.ORB_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = orb.detectAndCompute(img1,None)
    kp2, des2 = orb.detectAndCompute(img2,None)
    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)
    # Match descriptors
    matches = bf.match(des1,des2)
    # Sort them in the order of their distance
    matches = sorted(matches, key = lambda x:x.distance)
    
    if matches is not None and des1 is not None and des2 is not None :
        dist = np.array([match.distance for match in matches])
        ratio = len(matches)/(min(len(des1),len(des2)) * np.mean(dist))
        print("Matching features ratio : {}".format(ratio))

    return ratio


# Compares screen to app screenshots and finds what app is the most likely
def compareToAll(img2) :
    # Load start screen images
    s1 = cv2.imread('./Scenarios/Images/s1.jpg')
    s2 = cv2.imread('./Scenarios/Images/s2.jpg')
    s3 = cv2.imread('./Scenarios/Images/s3.jpg')
    s4 = cv2.imread('./Scenarios/Images/s4.jpg')
    s5 = cv2.imread('./Scenarios/Images/s5.jpg')
    s6 = cv2.imread('./Scenarios/Images/s6.jpg')
    images = [s1,s2,s3,s4,s5,s6]
    ratios = []
    # Compare to each of them
    for i in range(len(images)) :
        print("Comparing to image {} :".format(i+1))
        ratios.append(compareToIm(images[i],img2))
    # Identify what image is the most similar to current screen
    maxi = max(ratios)
    i = ratios.index(maxi)
    print("App identified : {}".format(i+1))
    return i+1



# Returns scenario file name with its ID
def getFileName(i) :
    filename = "./Scenarios/Scenarios/s" + str(i) + ".txt"
    return filename


