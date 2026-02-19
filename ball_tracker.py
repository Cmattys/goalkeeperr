import cv2
import cvzone
from cvzone.ColorModule import ColorFinder
import math

class WhiteBallTracker:
    def __init__(self, debug_mode=False):
        self.color_finder = ColorFinder(debug_mode)
        
        # Tes réglages HSV
        self.hsv_vals = {
            'hmin': 0, 'smin': 0, 'vmin': 200, 
            'hmax': 179, 'smax': 55, 'vmax': 255
        }

    def find_ball(self, img, depth_frame):
        """
        Cherche l'objet blanc LE PLUS PROCHE.
        Nécessite: img (couleur) et depth_frame (profondeur RealSense).
        """
        # 1. Masque et Contours
        img_color, mask = self.color_finder.update(img, self.hsv_vals)
        img_contours, contours = cvzone.findContours(img, mask, minArea=50)

        closest_center = None
        min_distance = 10.0  # On initialise avec une grande distance (10 mètres)
        best_contour = None

        # 2. On boucle sur TOUS les objets blancs trouvés
        if contours:
            for contour in contours:
                cx, cy = contour['center']
                
                # On lit la distance de cet objet spécifique
                # (Attention : RealSense renvoie 0.0 si c'est trop près ou illisible)
                dist = depth_frame.get_distance(cx, cy)

                # 3. La comparaison : Est-ce le plus proche ?
                # On ignore 0.0 (erreur) et on cherche une distance inférieure au record actuel
                if 0.10 < dist < min_distance:
                    min_distance = dist
                    closest_center = (cx, cy)
                    best_contour = contour

        # 4. Si on a trouvé un "gagnant" (le plus proche)
        if closest_center and best_contour:
            cx, cy = closest_center
            
            # On dessine dessus
            cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED) # Point Rouge
            
            # On affiche la distance à côté
            cv2.putText(img, f"{min_distance:.2f} m", (cx + 10, cy), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Carré vert
            x, y, w, h = best_contour['bbox']
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # On renvoie l'image, le point du plus proche, et le masque
        return img, closest_center, mask