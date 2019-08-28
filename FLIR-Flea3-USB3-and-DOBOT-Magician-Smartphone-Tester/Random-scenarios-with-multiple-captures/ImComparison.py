import cv2
import numpy as np

#--------------------------------------------IMAGE-COMPARISON----------------------------------------

# Brute-Force Matching with ORB Descriptors

def similarities(img1,img2) :
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



# Find differences

def changements(img1,img2) :
    # Convert input images to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Apply an adaptive threshold to both image to get their contours
    th1 = cv2.adaptiveThreshold(gray1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 93, 4)
    th2 = cv2.adaptiveThreshold(gray2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 93, 4)

    # Apply a closing to remove black noise
    kernel1 = np.ones((10,10), np.uint8)
    cl1 = cv2.morphologyEx(th1, cv2.MORPH_CLOSE, kernel1)
    cl2 = cv2.morphologyEx(th2, cv2.MORPH_CLOSE, kernel1)

    # Process the difference between both images
    dif = cl1 == cl2

    # Apply a closing to get only the thicker contours (the thinest are just mistakes)
    kernel2 = np.ones((20,20),np.uint8)
    cld = cv2.morphologyEx(np.uint8(dif), cv2.MORPH_CLOSE, kernel2)
    # Apply to steps or erosion to increase black areas and make them connect there neighbours, in order to have more closed contours
    erosion = cv2.erode(cld, kernel2, iterations = 2)

    # Add a white border to the image. This allows to detect correcly objects that would be touching the borders of the image previously.
    constant = cv2.copyMakeBorder(erosion, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value = 1)
    # Initialize difference mask
    mask = np.zeros(th1.shape, np.uint8)
    # Detect contours in the image
    contours, hierarchy = cv2.findContours(constant, cv2.RETR_TREE, 2)

    for i in range(1, len(contours)) :
        # We only want the contours having hierarchy value 0, ie being childen of the contour af the whole image.
        cnt = contours[i]
        if hierarchy[0,i,3] == 0 :
            # Draw corresponding convex hull on the mask and fill it in white.
            hull = cv2.convexHull(cnt)
            cv2.fillPoly(mask, pts = [hull], color = 255)

    return mask


# Global comparision

def compareImages(img1,img2) :
    ratio = similarities(img1,img2)
    if ratio > 0.01 : # If input images look similar, look for difference (that could be newly appeared objects)
        mask = changements(img1,img2)
        if (np.sum(mask) / (mask.shape[0] * mask.shape[1]) > 5) : # Check if the mask shows enough differences to be correct.
            return mask
    return None
