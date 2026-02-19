import pyrealsense2 as rs
import numpy as np
import cv2

class RealSenseCamera:
    def __init__(self):
        # 1. Configuration du Pipeline (le tuyau de données)
        self.pipeline = rs.pipeline()
        config = rs.config()

        # 2. On active les deux flux : Couleur et Profondeur
        # 640x480 est une résolution standard rapide (30 images/sec)
        config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 60)
        config.enable_stream(rs.stream.color, 848, 480, rs.format.bgr8, 60)

        # 3. Démarrage
        print("⏳ Démarrage de la RealSense...")
        self.pipeline.start(config)
        
        # 4. Création de l'aligneur
        # C'est TRÈS IMPORTANT : ça aligne la profondeur sur l'image couleur.
        # Sans ça, la distance mesurée sera décalée par rapport à l'image.
        self.align = rs.align(rs.stream.color)
        print("✅ RealSense prête.")

    def get_frame(self):
        """
        Retourne :
        1. L'image couleur (pour cvzone)
        2. Le 'depth_frame' (pour mesurer la distance précise)
        """
        # Attendre la prochaine image
        frames = self.pipeline.wait_for_frames()

        # Aligner la profondeur sur la couleur
        aligned_frames = self.align.process(frames)

        # Récupérer les frames alignées
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        # Vérification si l'image est valide
        if not depth_frame or not color_frame:
            return None, None

        # Convertir l'image couleur en tableau Numpy (pour OpenCV)
        color_image = np.asanyarray(color_frame.get_data())

        # On retourne l'image (pour voir) ET la frame de profondeur (pour mesurer)
        return color_image, depth_frame

    def release(self):
        """Arrête la caméra proprement."""
        self.pipeline.stop()