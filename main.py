import cv2
import cvzone
from camera import RealSenseCamera
from ball_tracker import WhiteBallTracker
from pos_goal import Courtois
import serial
import time
from pos_goal import ConditionTimer

def main():
    # Démarrage de la caméra et du tracker
    cam = RealSenseCamera()
    tracker = WhiteBallTracker(debug_mode=False)
    
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)

    # --- AJOUT TIMER ---
    timer_hors_zone = ConditionTimer()
    dernier_angle_envoye = None
    
    while True:
        img, depth_frame = cam.get_frame()
        if img is None: 
            continue

        img_out, center, mask = tracker.find_ball(img, depth_frame)

        if center:
            cx, cy = center
            coords_3d = tracker.get_3d_coordinates(cam.intrinsics, cx, cy, depth_frame)

            if coords_3d:
                x_c, y_c, z_c = coords_3d
                x_rob, y_rob, z_sol = Courtois.conversion_plan_robot(x_c, y_c, z_c)
                
                # 1. On vérifie si la balle est dans la zone
                est_dans_zone = Courtois.zone_de_tir(z_sol)
                
                # 2. On met à jour le timer
                doit_revenir_au_centre = timer_hors_zone.update(not est_dans_zone)
                
                # Variable temporaire pour savoir si on doit envoyer un truc à l'Arduino
                angle_a_envoyer = None 
                
                # 3. Prise de décision
                if est_dans_zone:
                    angle_arduino = Courtois.calculer_angle_moteur(x_rob, y_rob)
                    angle_a_envoyer = int(angle_arduino) # On tronque ici !
                    
                    print(f"🚨 (Z: {z_sol:.2f}m) -> Cible X:{x_rob:.2f}m Y:{y_rob:.2f}m | ANGLE: {angle_a_envoyer}°")
                    cv2.putText(img_out, f"Angle Oxy: {angle_a_envoyer} deg", (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                                
                elif doit_revenir_au_centre:
                    angle_a_envoyer = 90 # Retour au centre net
                    
                    print(f"🔄 Balle loin depuis 2s ({z_sol:.2f}m) -> RETOUR CENTRE | ANGLE: {angle_a_envoyer}°")
                    cv2.putText(img_out, f"Retour Centre: {angle_a_envoyer} deg", (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 3)
                                
                else:
                    # La balle est trop loin, mais on attend encore
                    print(f"⏳ Balle en attente ({z_sol:.2f}m)... chrono en cours")

                # 4. ENVOI SÉRIE (Seulement si l'angle a changé !)
                if angle_a_envoyer is not None and arduino is not None:
                    # On compare avec le dernier angle
                    if angle_a_envoyer != dernier_angle_envoye:
                        arduino.write(f"{angle_a_envoyer}\n".encode('utf-8'))
                        dernier_angle_envoye = angle_a_envoyer  # On met en mémoire !

        # Affichage
        img_stacked = cvzone.stackImages([img_out, mask], 2, 0.5)
        cv2.imshow("Vision Gardien 3D", img_stacked)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if arduino is not None:
        arduino.close()
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()