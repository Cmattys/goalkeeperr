
class Courtois :
    def direction (mémoire_x):
        #si le x augmgnete on vas a droite 
        max=len(mémoire_x)-1
        delta=mémoire_x[0]-mémoire_x[max]
        if (delta>10):
            return "Gauche"
        elif (delta<-10):
            return "Droite"
        else :
            return "fixe"
        
    def Hauteur (mémoire_y):
        #si le x augmgnete on vas a droite 
        max=len(mémoire_y)-1
        delta=mémoire_y[0]-mémoire_y[max]
        if (delta>10):
            return "Haut"
        elif (delta<-10):
            return "Bas"
        else :
            return "fixe"
    
    def stab_direction(mémo):
        max=len(mémo)
        for i in range(max):
            if mémo[0]!=mémo[i]:
                return "Pas stable"
            else :
                return mémo[0]
            

    def is_stable(mémoire_z, tolerance=0.02):
    
    # 1. Sécurité : Si la mémoire est vide ou presque vide, on ne sait pas
        if len(mémoire_z) < 2:
            return False

    # 2. On cherche les extrêmes dans toute la mémoire
        mini = min(mémoire_z)
        maxi = max(mémoire_z)

    # 3. On calcule l'écart max
        ecart = maxi - mini

    # 4. Vérification
    # Si l'écart est plus petit ou égal à ta tolérance (ex: 2), c'est stable !
        if ecart <= tolerance:
            return True
        else:
            return False
        
    def prise_decision(horizontale,vertical):
        angle=90
        direction = 1
        if horizontale == "Gauche" :
            direction = -1
        elif horizontale == "Droite" :
            direction = 1
        #si le robot ne doit pas bouger mais je commente pour l'instant 
        #esle :
            #return 90
        if vertical == "Haut" :
            delta = direction * 45
        else :
            delta = direction * 90
        
        angle = angle + delta 
        return angle
    
    def zone_de_tir(distance):
        limite = 2
        if distance<limite :
            return True
        else :
            return False

