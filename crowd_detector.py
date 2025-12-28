import cv2
import numpy as np
from collections import deque
import time

class AdvancedCrowdDetector:
    def __init__(self, smooth_window=5):
        self.smooth_window = smooth_window
        self.count_history = deque(maxlen=smooth_window)
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=True)
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    def estimate_crowd_count(self, frame):
        """
        Estimate crowd count using background subtraction and contour analysis
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(gray)

        # Apply morphological operations to reduce noise
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel, iterations=2)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by area (potential people)
        min_area = 500  # Minimum area for a person
        max_area = 50000  # Maximum area for a person
        valid_contours = [cnt for cnt in contours if min_area < cv2.contourArea(cnt) < max_area]

        # Estimate crowd count based on contours
        contour_count = len(valid_contours)

        # Simple density estimation (normalized by frame size)
        density = contour_count / (frame.shape[0] * frame.shape[1] / 100000)  # per 100k pixels

        # Cascade count (for hierarchical detection, simplified)
        cascade_count = contour_count

        # Confidence based on contour stability
        confidence = min(1.0, contour_count / 10.0) if contour_count > 0 else 0.0

        # Smooth the count
        self.count_history.append(contour_count)
        smoothed_count = np.mean(self.count_history) if self.count_history else contour_count

        return {
            'count': smoothed_count,
            'cascade_count': cascade_count,
            'contour_count': contour_count,
            'density_count': density,
            'confidence': confidence,
            'method': 'background_subtraction'
        }

    def create_density_heatmap(self, frame, detection):
        """
        Create a density heatmap overlay
        """
        # Create a copy of the frame
        heatmap = frame.copy()

        # Get foreground mask
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fg_mask = self.bg_subtractor.apply(gray)

        # Apply Gaussian blur to create density effect
        density_map = cv2.GaussianBlur(fg_mask.astype(np.float32), (51, 51), 0)

        # Normalize to 0-255
        if density_map.max() > 0:
            density_map = (density_map / density_map.max() * 255).astype(np.uint8)

        # Apply colormap
        heatmap_overlay = cv2.applyColorMap(density_map, cv2.COLORMAP_JET)

        # Blend with original frame
        alpha = 0.6
        heatmap = cv2.addWeighted(frame, 1 - alpha, heatmap_overlay, alpha, 0)

        # Add count text
        count_text = f"Crowd Count: {int(detection['count'])}"
        cv2.putText(heatmap, count_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return heatmap