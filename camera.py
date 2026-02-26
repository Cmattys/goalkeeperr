import pyrealsense2 as rs
import numpy as np

class RealSenseCamera:
    def __init__(self):
        self.pipeline = rs.pipeline()
        config = rs.config()

        # Configuration des flux
        config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 60)
        config.enable_stream(rs.stream.color, 848, 480, rs.format.bgr8, 60)

        print("⏳ Démarrage de la RealSense...")
        self.profile = self.pipeline.start(config) # On garde le profil
        
        # RÉCUPÉRATION DES INTRINSÈQUES (pour le calcul 3D)
        depth_stream = self.profile.get_stream(rs.stream.depth)
        self.intrinsics = depth_stream.as_video_stream_profile().get_intrinsics()
        
        self.align = rs.align(rs.stream.color)
        print("✅ RealSense prête avec Intrinsèques chargées.")

    def get_frame(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            return None, None

        color_image = np.asanyarray(color_frame.get_data())
        return color_image, depth_frame

    def release(self):
        self.pipeline.stop()