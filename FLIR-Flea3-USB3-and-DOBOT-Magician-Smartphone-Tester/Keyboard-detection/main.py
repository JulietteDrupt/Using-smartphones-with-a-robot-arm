import DobotDllType as dType
import Dobotfunctions as Dfonct
import screen
import CamFunctions as Cfonct
import numpy as np
import cv2

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

#Load Dll
api = dType.load()

#Connect Dobot
state = dType.ConnectDobot(api,"",115200)[0]
print("Etat de la connexion / Connect status : {}] \n".format(CON_STR[state]))

if (state == dType.DobotConnect.DobotConnect_NoError):

    # Run camera and in case a keyboard was detected, retrieve what position to press to write 'hello world'
    result, hello_im, z_min, ecran = Cfonct.run(api)

    if hello_im is not None :

        # Write 'hello world' on the keyboard
    
        for b in hello_im :
            x = b[1]
            y = b[0]
            [xf,yf] = ecran.Calc_Coordinates(x,y)

            Dfonct.Movement(api,xf,yf,z_min + 20)
            Dfonct.Touch(api,z_min)

#Disconnect Dobot
dType.DisconnectDobot(api)
