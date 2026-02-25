import cv2
import cvzone
from camera import RealSenseCamera
from ball_tracker import WhiteBallTracker
from pos_goal import Courtois 
from pos_goal import ConditionTimer
from collections import deque

def main():
    # 1. Démarrage Camera
    cam = RealSenseCamera()
    
    # 2. Démarrage Tracker
    tracker = WhiteBallTracker(debug_mode=True) 

    goal=Courtois
    mon_timer=ConditionTimer()
    
    

    #initialisation de la mémoire des position le tout a 0
    maxtaille=20
    mémoire_x = deque(maxlen=maxtaille)
    mémoire_y = deque(maxlen=maxtaille)
    mémoire_z = deque(maxlen=60)
    mémoire_dir= deque(maxlen=5)
    mémoire_haut= deque(maxlen=5)
    direction_final="fixe"
    Hauteur_final="fixe"


    while True:
        # A. On récupère les deux images
        img, depth_frame = cam.get_frame()
        
        if img is None:
            continue

        # B. APPEL MODIFIÉ : On donne "depth_frame" au tracker !
        # Le tracker va faire le tri et nous rendre le plus proche.
        img_out, center, mask = tracker.find_ball(img, depth_frame)

        # C. Logique
        if center:
            cx, cy = center
            # On demande : "Dans la grille de profondeur, quelle est la valeur à la case (cx, cy) ?"
            distance = depth_frame.get_distance(cx, cy)
            #on arrondie parce que renvoie trop de chiffre apres la virgule
            distance_arrondie = round(distance, 2)
            #on vas stocker dans mémoire les 20 derniere valeur de la position de la balle pour ensuite les comparer
            mémoire_x.append(cx)
            mémoire_y.append(cy)
            mémoire_z.append(distance_arrondie)
            rep=Courtois.direction(mémoire_x)
            rep2=Courtois.Hauteur(mémoire_y)
            mémoire_dir.append(rep)
            mémoire_haut.append(rep2)
            verif=Courtois.is_stable(mémoire_z)
            reset=Courtois.zone_de_tir(distance_arrondie)
            #on calcule les valeur final uniquement dans la zone de tir
            if Courtois.zone_de_tir(distance_arrondie):
                Hauteur_final=Courtois.stab_direction(mémoire_haut)
                direction_final=Courtois.stab_direction(mémoire_dir)
                print("debug")
            elif mon_timer.update(reset):
                angle=90
            
            # Plus besoin de recalculer la distance ici, le tracker a déjà choisi le bon !
            angle = Courtois.prise_decision(direction_final,Hauteur_final)
            print(f"Cible verrouillée (Plus proche) -> X:{cx} Y:{cy}")
            print(direction_final)
            print(Hauteur_final)
            print(angle)
        
        # D. Affichage
        img_stacked = cvzone.stackImages([img_out, mask], 2, 0.4)
        cv2.imshow("RealSense Robot", img_stacked)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()