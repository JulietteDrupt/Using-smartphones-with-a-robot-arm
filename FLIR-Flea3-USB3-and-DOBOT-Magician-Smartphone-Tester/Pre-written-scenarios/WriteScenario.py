import numpy as np
import cv2
import math


ix,iy = -1,-1
centroids = None
scroll = False
scrollBeginOk = False
filename = ""


#-----------------------------------------------CALIBRATION-------------------------------------------

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



# Redimensionne l'écran en ne gardant que la zone encadrée par les points rouges
def resizeScreen(im,centroids):
    miny = int(centroids[2,1])
    maxy = int(centroids[1,1])
    minx = int(centroids[2,0])
    maxx = int(centroids[1,0])
    return im[miny:maxy,minx:maxx,:]


#--------------------------------------GET-COORDINATES------------------------------------------------


def dist(pt1,pt2):
    return math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)


def convertCoord(target,centroids):
    v1 = centroids[0] - centroids[2]
    v2 = centroids[0] - centroids[1]
    v = centroids[0] - np.array(target)
    c1 = int((v1[0] * v[0] + v1[1] * v[1]) / dist(centroids[0],centroids[2]))
    c2 = int((v2[0] * v[0] + v2[1] * v[1]) / dist(centroids[0],centroids[1]))
    return [c1,c2]


def TouchCoordinates(centroidsTouches,centroids):
    bl = centroids[2]
    n,m = centroidsTouches.shape
    for i in range(n) :
        centroidsTouches[i,0] += bl[0]
        centroidsTouches[i,1] += bl[1]
        centroidsTouches[i] = Coord(centroidsTouches[i],centroids)
    return(centroidsTouches)


#---------------------------------WRITE-SCENARIO-FILE-------------------------------------------------


def getMouseCoord(event,x,y,flags,param):
    global ix,iy,centroids
    global filename
    global scroll, scrollBeginOk, scrollEndOk
    if event == cv2.EVENT_LBUTTONDOWN and centroids is not None :
        [ix,iy] = convertCoord([x,y],centroids)
        print("x,y = {},{}\n".format(iy,ix))
        
        with open(filename,'a') as File :
            if scroll == True :
                if scrollBeginOk == False :
                    File.write("###SCROLL###\nx,y = {},{} ; ".format(iy,ix))
                    scrollBeginOk = True
                else :
                    File.write("u,v = {},{}\n".format(iy,ix))
                    scroll = False
                    scrollBeginOk = False
            
            else :
                File.write("x,y = {},{}\n".format(iy,ix))


def writeSize(centroids):
    d1 = dist(centroids[0],centroids[1])
    d2 = dist(centroids[0],centroids[2])
    largeur = min(d1,d2)
    longueur = max(d1,d2)
    with open(filename,'a') as File :
            File.write("###SCREENSIZE###\nscreen_size = [{},{}]\n###BEGIN###\n".format(int(largeur),int(longueur)))
    #return [largeur,longueur]


#--------------------------------------------CAMERA---------------------------------------------------


import os
import PySpin

def acquire_images(cam, nodemap, nodemap_tldevice):
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
        screen_size = [0,0]
        global centroids
        global scroll
        global filename
        
        filename = input("Scenario filename : ")

        # Set acquisition mode to continuous
        #
        #  Retrieve enumeration node from nodemap
        
        # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

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
        cv2.setMouseCallback('im',getMouseCoord)
        while(1):
            try:
            
            #  Retrieve next received image
                image_result = cam.GetNextImage()

            #  Ensure image completion
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()

                    row_bytes = float(len(image_result.GetData()))/width
                    rawFrame = np.array(image_result.GetData(), dtype = "uint8").reshape(height,width)
                    im = cv2.cvtColor(rawFrame,cv2.COLOR_BAYER_BG2BGR)                   
                    cv2.imshow('im',im)
                    
                    k = cv2.waitKey(10) & 0xFF
                    if k == ord('q') :
                        break
                    elif k == ord('c') :
                        print("Processing... Please wait... This will take less than a minute...")
                        dst = cv2.fastNlMeansDenoisingColored(im,None,10,10,7,21)
                        centroids = CamCalibrate(dst)
                        writeSizeInFile = input("Do you want to write screen size in the file (y or n)?\n(Screen size will not be read with screen recognition algorithm.)")
                        if writeSizeInFile == 'y' :
                            writeSize(centroids)
                    elif k == ord('s') :
                        scroll = True
                        
                    #  Release image
                    image_result.Release()

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False
            
        cv2.destroyAllWindows()       
            
        #  End acquisition
        cam.EndAcquisition()
    
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


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


def run_single_camera(cam):
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

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images
        result &= acquire_images(cam, nodemap, nodemap_tldevice)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def main():
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """

    # Since this application saves images in the current folder
    # we must ensure that we have permission to write to this folder.
    # If we do not have permission, fail right away.
    try:
        test_file = open('test.txt', 'w+')
    except IOError:
        print('Unable to write to current directory. Please check permissions.')
        input('Press Enter to exit...')
        return False

    test_file.close()
    os.remove(test_file.name)

    result = True

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

        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    # Run example on each camera
    for i, cam in enumerate(cam_list):

        print('Running example for camera %d...' % i)

        result &= run_single_camera(cam)
        print('Camera %d example complete... \n' % i)

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    input('Done! Press Enter to exit...')
    return result

if __name__ == '__main__':
    main()
