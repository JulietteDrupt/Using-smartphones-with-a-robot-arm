# -*- coding: utf-8 -*-
"""
Created on Fri Jun 09 11:43:53 2017

@author: Administrateur
"""

import DobotDllType as dType

#--------------------------------------------MOVEMENTS----------------------------------------


def Init(api):
    """ to keep a good accuracy, we calibrate our arm.
    This function must be called before all arm use"""
    #Clean Command Queued
    dType.SetQueuedCmdClear(api)
    #Async Motion Params Setting
    dType.SetHOMEParams(api, 200, 200, 200, 200, isQueued = 1)
    dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued = 1)
    dType.SetPTPCommonParams(api, 100, 100, isQueued = 1)
    #Async Home
    dType.SetHOMECmd(api, temp = 0, isQueued = 1)
    #Useless movement which permit to wait the init end.
    tempo=tempo=dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 210, 0, 135, 0, isQueued = 1)[0]
    #Start to Execute Command Queued
    dType.SetQueuedCmdStartExec(api)
    #Wait for Executing Last Command 
    while tempo > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100) 
    #Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)
    
    
def Calc_Z_Min(api):
    """ SECURITE : le bras robotic va attendre que vous
    le placiez à sa valeur la plus basse de z
    SECURITY : the robot will wait that you put
    the robotic arm at is lowest z value"""
    input("""[CALIBRAGE / CALIBRATION]
[placez le robot en position d'appuie / lean the robot on a button]
[puis appuyer sur ENTRER / then press ENTER]""")
    a=dType.GetPose(api)
    print ("[Z's value / Valeur de z : {}]\n".format(int(a[2])))
    return a[2]
    
def Position(api):
    """ pour recuperer la position du bras / to get the current arm's position"""
    input("""placez le robot en position (puis ENTREZ) / put the robot at the desired position (then ENTER) : \n""")
    pos=dType.GetPose(api)
    return pos
    
def Movement(api,x,y,z):
    """ deplace le bras vers la position (x,y,z)
    move the arm to (x,y,z)"""
    dType.SetQueuedCmdClear(api)
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x, y, z, 0, isQueued = 1)[0]
    tempo=dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x, y, z, 0, isQueued = 1)[0]
    dType.SetQueuedCmdStartExec(api)    
    while tempo > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)
    dType.SetQueuedCmdStopExec(api)
    

def Touch(api,z_min):
    """move the arm to touch a button and back to its initial position"""
    a=dType.GetPose(api)    
    dType.SetQueuedCmdClear(api)
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,a[0],a[1],z_min, 0, isQueued = 1)[0]
    tempo=dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,a[0],a[1],z_min+30, 0, isQueued = 1)[0]
    dType.SetQueuedCmdStartExec(api)    
    while tempo > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)
    dType.SetQueuedCmdStopExec(api)

def Scroll(api,x_begin,y_begin,x_end,y_end,z_min):
    """permit to the robot to scroll with a movement from x_begin,y_begin to x_end,y_end"""
    Movement(api,x_begin,y_begin,z_min+30)
    Movement(api,x_begin,y_begin,z_min)
    Movement(api,x_end,y_end,z_min)
    Movement(api,x_end,y_end,z_min+30)

#----------------------------------------CALIBRATION---------------------------------------------


def coordinates(api,letter):
    input("mettre le bras robotic sur (puis ENTRER) / put the robot arm on (THEN ENTER) : {}".format(letter))
    a=dType.GetPose(api)
    print("OK")
    return a[0:2]
    
def Keyboard_Calibration(api,firstline,secondline,thirdline):
    """ give the position (x,y) of each letter on the keyboard. return a table"""
    
    ff=coordinates(api,firstline[0])
    fl=coordinates(api,firstline[-1])
    sf=coordinates(api,secondline[0])
    sl=coordinates(api,secondline[-1])
    tf=coordinates(api,thirdline[0])
    tl=coordinates(api,thirdline[-1])
    space=coordinates(api," ")
    
    calculs=[(fl[0]-ff[0])/(len(firstline)-1),(sl[0]-sf[0])/(len(secondline)-1),(tl[0]-tf[0])/(len(thirdline)-1),(fl[1]-ff[1])/(len(firstline)-1),(sl[1]-sf[1])/(len(secondline)-1),(tl[1]-tf[1])/(len(thirdline)-1)]
    
    Coordinates=[]
    for i in range (0,len(firstline)):
        Coordinates.append([firstline[i],ff[0]+i*calculs[0],ff[1]+i*calculs[3]])
    for i in range (0,len(secondline)):
        Coordinates.append([secondline[i],sf[0]+i*calculs[1],sf[1]+i*calculs[4]])
    for i in range (0,len(thirdline)):
        Coordinates.append([thirdline[i],tf[0]+i*calculs[2],tf[1]+i*calculs[5]])
    Coordinates.append([" ",space[0],space[1]])
    
    return Coordinates
    
def index_number_keyboard(searched, coordinates):
    "return the index number where you can find the character"
    for i in range(0,len(coordinates)):
        if coordinates[i][0]==searched:
            return i;

def screen_Calibration(api):
    tlc = coordinates(api, "top left corner")
    trc = coordinates(api, "top right corner")
    blc = coordinates(api, "bottom left corner")
    print("top left corner : {}".format(tlc))
    print("top right corner : {}".format(trc))
    print("bottom left corner : {}".format(blc))
