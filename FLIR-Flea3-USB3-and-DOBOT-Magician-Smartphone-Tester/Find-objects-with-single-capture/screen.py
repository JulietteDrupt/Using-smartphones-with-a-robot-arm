# -*- coding: utf-8 -*-
import Dobotfunctions as Dfonct
import DobotDllType as dType
import math

class screen:
    """ Contient les paramètres de l'écran utiliser """
    
    def __init__(self,api,screen_width,screen_height):
        """pour initialiser les paramètres"""
        print("début")
        input("placez le robot sur le point rouge haut-gauche de l'écran (puis ENTREZ) :\n")
        self.topleft=dType.GetPose(api)[0:2]
        input("placez le robot sur le point rouge haut-droit de l'écran (puis ENTREZ) :\n")
        self.topright=dType.GetPose(api)[0:2]
        input("placez le robot sur le point rouge bas-gauche de l'écran (puis ENTREZ) :\n")
        self.bottomleft=dType.GetPose(api)[0:2]
        self.pixelheight=screen_height
        self.pixelwidth=screen_width
        #on calcul la taille de l'ecran dans la base du robot
        self.Hori_distance=math.sqrt((self.topleft[0]-self.topright[0])**2+(self.topleft[1]-self.topright[1])**2)
        self.Vert_distance=math.sqrt((self.topleft[0]-self.bottomleft[0])**2+(self.topleft[1]-self.bottomleft[1])**2)
        
    def Calc_Coordinates(self,x_pixel,y_pixel):       
        """Calcul des coordonnées d'une position dans le telephone dans la base du robot"""
        #on calcul l'angle entre les point 1 3 2
        x1=self.topright[0]
        y1=self.topright[1]
        x2=self.topleft[0]
        y2=self.topleft[1]-1
        x3=self.topleft[0]   
        y3=self.topleft[1]
        #calcul de l'angle
        angle=math.acos(((x1-x3)*(x2-x3)+(y1-y3)*(y2-y3))/(math.sqrt((x1-x3)**2+(y1-y3)**2)*math.sqrt((x2-x3)**2+(y2-y3)**2)))
        # si l'angle est négatif, il faut ajouter le signe
        if x3>=x1:
            angle=-angle

        x2 = self.topleft[0] - 1
        y2 = self.topleft[1]
        x1 = self.bottomleft[0]
        y1 = self.bottomleft[1]

        angle2 = math.acos(((x1 - x3) * (x2 - x3) + (y1 - y3) * (y2 - y3)) / (
        math.sqrt((x1 - x3) ** 2 + (y1 - y3) ** 2) * math.sqrt((x2 - x3) ** 2 + (y2 - y3) ** 2)))

        if y3 <= y1:
            angle2 = -angle2

        angle3 = (angle + angle2) / 2.

        # on change la norme de la base 2
        x_b2=float(x_pixel)/float(self.pixelwidth)*self.Hori_distance
        y_b2=float(y_pixel)/float(self.pixelheight)*self.Vert_distance
        # on projete nos valeurs dans la base du robot
        X_final=x3+x_b2*math.sin(angle3)-y_b2*math.cos(angle3)
        Y_final=y3-x_b2*math.cos(angle3)-y_b2*math.sin(angle3)
        #on renvoie nos valeurs
        return [X_final,Y_final]
