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

    result, filename, z_min, ecran = Cfonct.run(api)
    print(filename)

    screen_size = None
    scrolling = False
    x,y,u,v = -1,-1,-1,-1

    if result :

        with open(filename,'r') as File :
            for line in File :
                
                if line == "###BEGIN###\n" :
                    testing = True
                    input("Press enter to start test.")

                elif line == "###SCROLL###\n" :
                    scrolling = True

                elif testing == True :
                    exec(line)
                    x,y = ecran.Calc_Coordinates(x,y)
                    if scrolling == False :
                        Dfonct.Movement(api,x,y,z_min + 20)
                        Dfonct.Touch(api,z_min)
                    else :
                        u,v = ecran.Calc_Coordinates(u,v)
                        Dfonct.Scroll(api,x,y,u,v,z_min)
                        scrolling = False


#Disconnect Dobot
dType.DisconnectDobot(api)
