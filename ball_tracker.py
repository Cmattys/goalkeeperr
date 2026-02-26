import cv2
import cvzone
from cvzone.ColorModule import ColorFinder
import pyrealsense2 as rs

class WhiteBallTracker:
    def __init__(self, debug_mode=False):
        self.color_finder = ColorFinder(debug_mode)
        self.hsv_vals = {
            'hmin': 0, 'smin': 0, 'vmin': 200, 
            'hmax': 179, 'smax': 55, 'vmax': 255
        }

    def get_3d_coordinates(self, intrinsics, cx, cy, depth_frame):
        """ Transforme le pixel (u,v) en coordonnées (x,y,z) en mètres """
        dist = depth_frame.get_distance(cx, cy)
        if dist <= 0:
            return None
        # Calcul des coordonnées réelles
        point_3d = rs.rs2_deproject_pixel_to_point(intrinsics, [cx, cy], dist)
        return point_3d

    def find_ball(self, img, depth_frame):
        img_color, mask = self.color_finder.update(img, self.hsv_vals)
        img_contours, contours = cvzone.findContours(img, mask, minArea=50)

        closest_center = None
        min_distance = 10.0
        best_contour = None

        if contours:
            for contour in contours:
                cx, cy = contour['center']
                dist = depth_frame.get_distance(cx, cy)
                if 0.10 < dist < min_distance:
                    min_distance = dist
                    closest_center = (cx, cy)
                    best_contour = contour

        if closest_center and best_contour:
            cx, cy = closest_center
            cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
            x, y, w, h = best_contour['bbox']
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return img, closest_center, mask