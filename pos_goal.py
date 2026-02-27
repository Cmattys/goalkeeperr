import math

class Courtois:
    #À quelle hauteur (en mètres) est placée l'objectif de ta caméra par rapport au sol ?
    HAUTEUR_CAMERA = 0.60  
    
    # De combien de degrés la caméra penche-t-elle vers le sol ?
    ANGLE_TILT_DEG = 25    

    @staticmethod
    def conversion_plan_robot(x_cam, y_cam, z_cam):
        # Conversion de l'angle en radians
        theta = math.radians(Courtois.ANGLE_TILT_DEG)

        # On calcule la distance qui descend VRAIMENT tout droit vers le sol
        y_descendant = y_cam * math.cos(theta) + z_cam * math.sin(theta)
        
        # On calcule la vraie profondeur au sol (Z_sol)
        z_sol = z_cam * math.cos(theta) - y_cam * math.sin(theta)
        
        #TRANSLATION : On place le (0,0) à la base du robot
        x_robot = x_cam  # L'axe gauche/droite ne change pas
        y_robot = Courtois.HAUTEUR_CAMERA - y_descendant # Hauteur de la balle par rapport au sol
        
        # On renvoie les coordonnées prêtes pour le gardien
        return x_robot, y_robot, z_sol

    @staticmethod
    def calculer_angle_moteur(x_robot, y_robot):
        """
        Calcule l'angle de l'aiguille dans le plan Oxy (le but).
        - 0° = Balle au sol à gauche (le robot se couche à gauche)
        - 90° = Balle en l'air au centre (le robot est debout)
        - 180° = Balle au sol à droite (le robot se couche à droite)
        """
        # ASTUCE ICI : On met un signe MOINS devant x_robot pour inverser la gauche et la droite !
        angle_rad = math.atan2(y_robot, -x_robot) 
        angle_deg = math.degrees(angle_rad)
        
        # Sécurité : Si la balle est "sous" le sol (erreur de capteur ou rebond bizarre)
        if angle_deg < 0:
            angle_deg = 0 if (-x_robot) > 0 else 180
            
        return max(0, min(180, int(angle_deg)))

    @staticmethod
    def zone_de_tir(z_sol):
        """ Le robot s'active si la balle est à moins de 2.5m """
        return z_sol < 2.5
    

import time

class ConditionTimer:
    def __init__(self):
        self.start_time = None # On ne commence pas à compter tout de suite

    def update(self, condition_is_false):
        """
        condition_is_false: On lui passe le résultat de ta fonction (True ou False)
        """
        if condition_is_false:
            # Si c'est la première fois qu'on détecte le False, on démarre le chrono
            if self.start_time is None:
                self.start_time = time.time()
            
            # On vérifie si 2 secondes sont passées
            if time.time() - self.start_time >= 2:
                return True
        else:
            # Si la condition n'est plus False, on reset le chrono à zéro
            self.start_time = None
            
        return False