import DobotDllType as dType
import Dobotfunctions as Dfonct
import screen
import CamFunctions as Cfonct

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


    # Run camera in order to retrieve the position of all graphical objects detected as well as screen size
    result,centroidsTouches,screen_size = Cfonct.run()

    print("\nDisplay calibration screen to continue.\n")

    # Initialize robot
    Dfonct.Init(api)
    # Get the heigh of the screen's plane
    z_min = Dfonct.Calc_Z_Min(api)
    Dfonct.Touch(api,z_min)

    # Launch robot calibration
    ecran = screen.screen(api,screen_size[0],screen_size[1])
    Dfonct.Touch(api,z_min)

    input("\nOpen previously segmented app.\nWarning: make sure you do not move the phone.\nThen press Enter to continue...")

    # Touch all graphical objects detected
    for touche in centroidsTouches :
        x = touche[1]
        y = touche[0]
        [xf,yf] = ecran.Calc_Coordinates(x,y)

        Dfonct.Movement(api,xf,yf,z_min + 20)
        Dfonct.Touch(api,z_min)

#Disconnect Dobot
dType.DisconnectDobot(api)


