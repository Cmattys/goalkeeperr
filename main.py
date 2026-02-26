import cv2
import cvzone
from camera import RealSenseCamera
from ball_tracker import WhiteBallTracker
from pos_goal import Courtois

def main():
    #Démarrage de la caméra et du tracker
    cam = RealSenseCamera()
    tracker = WhiteBallTracker(debug_mode=True)
    
    while True:
        #On récupère l'image couleur et la profondeur
        img, depth_frame = cam.get_frame()
        if img is None: 
            continue

        #On cherche la balle blanche la plus proche
        img_out, center, mask = tracker.find_ball(img, depth_frame)

        if center:
            cx, cy = center
            
            #On récupère les coordonnées 3D brutes par rapport à la lentille
            coords_3d = tracker.get_3d_coordinates(cam.intrinsics, cx, cy, depth_frame)

            if coords_3d:
                # x_c = latéral caméra, y_c = vertical caméra, z_c = profondeur caméra
                x_c, y_c, z_c = coords_3d
                
                # On redresse l'image pour l'adapter au plan du gardien
                x_rob, y_rob, z_sol = Courtois.conversion_plan_robot(x_c, y_c, z_c)
                
                # On vérifie si la balle est assez proche (grâce à z_sol)
                if Courtois.zone_de_tir(z_sol):
                    
                    # On calcule l'angle de plongeon dans le plan du but (avec X et Y)
                    angle_arduino = Courtois.calculer_angle_moteur(x_rob, y_rob)
                    
                    # Affichage clair dans le terminal
                    print(f"(Z: {z_sol:.2f}m) -> Cible X:{x_rob:.2f}m Y:{y_rob:.2f}m | ANGLE: {angle_arduino}°")

                    # Affichage de l'angle en vert sur le retour vidéo
                    cv2.putText(img_out, f"Angle Oxy: {angle_arduino} deg", (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                else:
                    # Si la balle est trop loin, le gardien reste en position d'attente
                    print(f" Balle en attente ({z_sol:.2f}m)...")

        # Affichage de la vidéo (ATTENTION : SANS ACCENT DANS LE NOM)
        img_stacked = cvzone.stackImages([img_out, mask], 2, 0.5)
        cv2.imshow("Vision Gardien 3D", img_stacked)

        # Quitter proprement en appuyant sur la touche 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libération des ressources à la fin
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()