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

    result,target,screen_size = Cfonct.run()

    Dfonct.Init(api)
    z_min = Dfonct.Calc_Z_Min(api)
    Dfonct.Touch(api,z_min) #comme le robot est en fait déjà dans la bonne position, il ne fait que reculer de qqs centimètres

    ecran = screen.screen(api,screen_size[0],screen_size[1])
    # Largeur
    x = target[1]
    # Longueur
    y = target[0]
    [xf,yf] = ecran.Calc_Coordinates(x,y)
    print ('xf : {}'.format(xf))
    print ('yf : {}'.format(yf))

    Dfonct.Movement(api,xf,yf,z_min + 20)
    Dfonct.Touch(api,z_min)


#Disconnect Dobot
dType.DisconnectDobot(api)
