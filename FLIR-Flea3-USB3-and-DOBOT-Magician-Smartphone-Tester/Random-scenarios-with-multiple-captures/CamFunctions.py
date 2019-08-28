# -*- coding: utf-8 -*-

import cv2
import time
import numpy as np
import os
import PySpin
import math
import Dobotfunctions as Dfonct
import screen
import random
import ImComparison as imcp

#-----------------------------------------COORDONNEES-POINTS---------------------------------------

# Prend en entrée 3 points (1, 2 et 3) et les range dans l'ordre top-left, top-right et bottom-left.
def order(pts):
    pts_ord = np.zeros(pts.shape)
    d1 = abs(pts[0,0]-pts[1,0])
    d2 = abs(pts[0,0]-pts[2,0])
    d3 = abs(pts[2,0]-pts[1,0])
    d = min(d1,d2,d3)
    dist1 = max(d1,d2,d3)
    if d == d1:
        align1 = (0,1)
    elif d == d2:
        align1 = (0,2)
    else :
        align1 = (1,2)
    D1 = abs(pts[0,1]-pts[1,1])
    D2 = abs(pts[0,1]-pts[2,1])
    D3 = abs(pts[2,1]-pts[1,1])
    D = min(D1,D2,D3)
    dist2 = max(D1,D2,D3)
    if D == D1:
        align2 = (0,1)
    elif D == D2:
        align2 = (0,2)
    else :
        align2 = (1,2)
    for i in range(3):
        if i in align1 and i in align2 :
            pts_ord[0,0] = pts[i,0]
            pts_ord[0,1] = pts[i,1]
        elif i in align1 and dist1 > dist2 :
            pts_ord[1,0] = pts[i,0]
            pts_ord[1,1] = pts[i,1]
        else :
            pts_ord[2,0] = pts[i,0]
            pts_ord[2,1] = pts[i,1]
    return pts_ord


# Détermine les coordonnées des points rouges tl, tr et bl dans l'image passée en entrée.
def CamCalibrate(im):
    dst = cv2.fastNlMeansDenoisingColored(im,None,10,10,7,21)
    hsv = cv2.cvtColor(dst,cv2.COLOR_BGR2HSV)
    lower_red = np.array([0,100,100])
    upper_red = np.array([10,255,255])
    mask_r = cv2.inRange(hsv,lower_red,upper_red)
    res = cv2.bitwise_and(dst,dst,mask = mask_r)
    ret,th = cv2.threshold(res[:,:,2],5,255,cv2.THRESH_BINARY)
    contours,hierarchy = cv2.findContours(th,1,1)
    print("{} contours detected".format(len(contours)))
    if len(contours) != 3 :
        print("Unexpected number of contours. Please try again (you may change brightness).")
        return(None)
    centroids = []
    for cnt in contours :
        M = cv2.moments(cnt)
        cx = M["m10"]/M["m00"]
        cy = M["m01"]/M["m00"]
        centroids.append([cx,cy])
    centroids = np.array(centroids)
    centroids = order(centroids)
    print("Centroids: {}".format(centroids))
    return centroids



def dist(pt1,pt2):
    return math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

def Coord(target,centroids):
    v1 = centroids[0] - centroids[2]
    v2 = centroids[0] - centroids[1]
    v = centroids[0] - np.array(target)
    c1 = (v1[0] * v[0] + v1[1] * v[1]) / dist(centroids[0],centroids[2])
    c2 = (v2[0] * v[0] + v2[1] * v[1]) / dist(centroids[0],centroids[1])
    return [c1,c2]

def TouchCoordinates(centroidsTouches,centroids):
    bl = centroids[2]
    n,m = centroidsTouches.shape
    for i in range(n) :
        centroidsTouches[i,0] += bl[0]
        centroidsTouches[i,1] += bl[1]
        centroidsTouches[i] = Coord(centroidsTouches[i],centroids)
    return(centroidsTouches)

def size(centroids):
    d1 = dist(centroids[0],centroids[1])
    d2 = dist(centroids[0],centroids[2])
    largeur = min(d1,d2)
    longueur = max(d1,d2)
    return [largeur,longueur]

#--------------------------------------------SEGMENTATION-TOUCHES-------------------------------------

# Redimensionne l'écran en ne gardant que la zone encadrée par les points rouges
def resizeScreen(im,centroids):
    miny = int(centroids[2,1])
    maxy = int(centroids[1,1])
    minx = int(centroids[2,0])
    maxx = int(centroids[1,0])
    return im[miny:maxy,minx:maxx,:]

# Segmente l'image de l'écran
def segmentation(im, mask = None):

    if mask is not None :
        im = cv2.bitwise_and(im,im,mask = mask)

    img = im[:,:,0]
    imb = im[:,:,1]
    imr = im[:,:,2]
    clahe = cv2.createCLAHE(clipLimit = 2.0,tileGridSize=(8,8))
    imr = clahe.apply(imr)
    img = clahe.apply(img)
    imb = clahe.apply(imb)
    dstr = cv2.fastNlMeansDenoising(imr,None,13)
    dstg = cv2.fastNlMeansDenoising(img,None,13)
    dstb = cv2.fastNlMeansDenoising(imb,None,13)
    thr = cv2.adaptiveThreshold(dstr,255, \
                            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                            cv2.THRESH_BINARY_INV,93,4)
    thg = cv2.adaptiveThreshold(dstg,255, \
                            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                            cv2.THRESH_BINARY_INV,93,4)
    thb = cv2.adaptiveThreshold(dstb,255, \
                            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                            cv2.THRESH_BINARY_INV,93,4)

    th = cv2.add(thr,thg)
    th = cv2.add(th,thb)
    th = 255 - th
    kernel = np.ones((5,5),np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel)
    cross = cv2.getStructuringElement(cv2.MORPH_CROSS,(10,10))
    dilation = cv2.dilate(th,kernel,iterations = 1)

    cross = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    th = cv2.erode(th,cross,iterations = 3)
    kernel = np.ones((3,3),np.uint8)

    dist_transform = cv2.distanceTransform(th,cv2.DIST_L2,5)
    ret,sure_fg = cv2.threshold(dist_transform, \
                            0.01*dist_transform.max(),255,0)
    sure_fg = np.uint8(sure_fg)

    unknown = 255 - th
    ret,markers,stats,centroids = cv2.connectedComponentsWithStats(sure_fg)

    markers = markers+1
    markers[unknown == 255] = 0

    markers = markers.astype(np.uint8)
    markers = cv2.applyColorMap(markers,cv2.COLORMAP_JET)
    print("{} objects detected".format(ret))
    return (markers,stats,centroids)

def getOnlyTouches(stats,centroidsTouches):
    areas = stats[:,4]
    #print(areas)
    quart1 = np.quantile(areas,0.25)
    quart3 = np.quantile(areas,0.75)
    med = np.median(areas)
    print("quart1 : {}".format(quart1))
    print("med : {}".format(med))
    print("quart3 : {}".format(quart3))
    valid = np.array([area > 0.5 * med and area < 50 * quart3 for area in areas])
    for i in range(centroidsTouches.shape[0]) :
        if not valid[i] :
            centroidsTouches[i] = 0
    centroidsTouches = centroidsTouches[~np.all(centroidsTouches == 0,axis = 1)]
    print("{} touches detected".format(centroidsTouches.shape[0]))
    #print(centroidsTouches)
    return centroidsTouches

def showObjects(im,centroidsTouches):
    for t in centroidsTouches :
        cv2.circle(im,(int(t[0]),int(t[1])),10,(0,255,255),-1)

#--------------------------------------------CAMERA----------------------------------------

def acquire_images(cam, nodemap, nodemap_tldevice,api):
    """
    This function shows images from a device.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** IMAGE ACQUISITION ***\n')
    try:

        result = True
        centroids = None
        centroidsTouches = None
        stats = None
        screen_size = [0,0]
        ecran = None
        z_min = None
        cum = None
        current = None
        previous = None


        # Set acquisition mode to continuous
        #
        #  Retrieve enumeration node from nodemap
        
        # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False,centroidsTouches,screen_size

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False,centroidsTouches,screen_size

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print('Acquisition mode set to continuous...')

        #  Begin acquiring images
        cam.BeginAcquisition()

        print('Acquiring images...')

        #  Retrieve device serial number
        device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)

        # Retrieve, convert, and show images
        cv2.namedWindow('im', cv2.WINDOW_NORMAL)
        print("Please ensure you have calibration screen image downloaded. Then put it in full screen to get started.")
        print("Please use keyboard :\n\t- press c to calibrate\n\t- press y to extract screen after calibration\n\t- press e to segment the screen after extracted\n\t- press q when you are done (with a correct segmentation).\nYou can extract a new screen (y) and segment it (e) as long as you are not satisfied with the result. Playing with screen brightness and camera focus may help.")
        while(1):
            try:
            
            #  Retrieve next received image
                image_result = cam.GetNextImage()

            #  Ensure image completion
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:
                    # Retrieve image width and height
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()

                    # Convert image to uint8 numpy array
                    row_bytes = float(len(image_result.GetData()))/width
                    rawFrame = np.array(image_result.GetData(), dtype = "uint8").reshape(height,width)
                    # Convert image to BGR
                    im = cv2.cvtColor(rawFrame,cv2.COLOR_BAYER_BG2BGR)
                    
                    # Display image in window 'im'
                    cv2.imshow('im',im)
                    k = cv2.waitKey(10) & 0xFF
                    if k == ord('q') : # Press 'q' to exit
                        cv2.destroyAllWindows()
                        break
                    elif k == ord('c') :
                        print("Processing... Please wait... This will take less than a minute...")
                        # Denoise image
                        dst = cv2.fastNlMeansDenoisingColored(im,None,10,10,7,21)
                        # Calibrate camera
                        centroids = CamCalibrate(dst)

                        if len(centroids == 3) : # if camera calibration went well
                            # Retrieve screen size
                            screen_size = size(centroids)
                            # Destroy all OpenCV windows
                            cv2.destroyAllWindows()

                            # Initialize robot
                            Dfonct.Init(api)
                            # Get the height of the screen's plane
                            z_min = Dfonct.Calc_Z_Min(api)
                            Dfonct.Touch(api,z_min)
                            # Launch robot calibration
                            ecran = screen.screen(api,screen_size[0],screen_size[1])
                            Dfonct.Touch(api,z_min)
                            # Move robot offscreen
                            [xf,yf] = ecran.Calc_Coordinates(-50,-10)
                            Dfonct.Movement(api,xf,yf,z_min + 20)

                        
                    elif k == ord('y') and centroids is not None :
                        # If a previous image of the screen was taken, it is copied to 'previous'
                        if current is not None :
                            previous = np.copy(current)
                        # Extract image of the screen, assign it to 'current' and display it
                        im2 = resizeScreen(im,centroids)
                        cv2.imshow('resized',im2)
                        current = np.copy(im2)

                    elif k == ord('e') and im2 is not None :

                        mask = None

                        # If a 'previous' image exists, compare it to 'current'. If new objects appeared, the resulting mask will hide everything but them. Otherwise returned mask will be None (ie if 'current' screen is unchanged or completely different).
                        if previous is not None :
                            mask = imcp.compareImages(previous, current)
                            # Display mask in case it is not None
                            if mask is not None :
                                cv2.imshow("mask",mask)

                        # Segment 'current' image with mask. If mask is None no mask is applied to 'current'.
                        markers,stats,centroidsTouches = segmentation(im2, mask)
                        # Display resulting object markers
                        cv2.imshow('segmentation',markers)
                        # Select what are most likely graphical objects beyond those detected by segmentation and display their centroids
                        centroidsTouches = getOnlyTouches(stats,centroidsTouches)
                        showObjects(im2,centroidsTouches)
                        cv2.imshow('touches',im2)
                        # Convert the object's coordinates to the red dot's basis.
                        centroidsTouches = TouchCoordinates(centroidsTouches,centroids)


                    elif k == ord('r') and centroids is not None :

                        if centroidsTouches is not None :
                            # Pick a random object beyond those detected, and touch it.
                            i = random.randint(0,len(centroidsTouches)-1)                            

                            touche = centroidsTouches[i]
                            x = touche[1]
                            y = touche[0]
                            [xf,yf] = ecran.Calc_Coordinates(x,y)
                            Dfonct.Movement(api,xf,yf,z_min + 20)
                            Dfonct.Touch(api,z_min)
                            # Move offscreen.
                            [xf,yf] = ecran.Calc_Coordinates(-50,-10)
                            Dfonct.Movement(api,xf,yf,z_min + 20)

                    #  Release image
                    image_result.Release()

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False,centroidsTouches,screen_size
                  
            
        #  End acquisition
        cam.EndAcquisition()
    
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False,centroidsTouches,screen_size

    return result,centroidsTouches,screen_size


def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** DEVICE INFORMATION ***\n')

    try:
        result = True

        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

        else:
            print('Device control information not available.')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def run_single_camera(cam,api):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True
        centroidsTouches = None
        screen_size = [0,0]

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images
        r1,centroidsTouches,screen_size = acquire_images(cam, nodemap, nodemap_tldevice,api)
        result &= r1

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result,centroidsTouches,screen_size


def run(api):
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """

    result = True
    centroidsTouches = None
    screen_size = [0,0]

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Get current library version
    version = system.GetLibraryVersion()
    print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('No camera detected. Please connect the camera or check you have the correct drivers installed.')
        input('Done! Press Enter to exit...')
        return False
    
    elif num_cameras > 1 :
        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Too many cameras connected. The present program does not support multi-camera acquisition. Please just let one connected and re-try')
        input('Done! Press Enter to exit...')
        return False,centroidsTouches,screen_size

    # If single camera, run
    cam = cam_list[0]
    print('Running...')
    r1,centroidsTouches,screen_size = run_single_camera(cam,api)
    result &= r1
    print('Completed... \n')

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    input('Done! Press Enter to exit and disconnect Dobby...')
    return result,centroidsTouches,screen_size

