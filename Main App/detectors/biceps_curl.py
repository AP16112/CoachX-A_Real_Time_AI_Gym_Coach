# Here in this file, we will write the logic and code for biceps curl exercise detection and counting the number of reps done by the user.


import math   # importing the math module to perform mathematical operations like calculating angles and trigonometric functions.

# We will use the BaseExercise class to create a BicepsCurlDetector class that will handle the biceps curl detection logic.
from core.base_exercise import BaseExercise


# The BicepsCurlDetector class extends the BaseExercise class and implements the logic to detect biceps curls based on the angles of the elbows and shoulders. It counts repetitions and provides feedback on elbow drift and swinging movement.
class BicepsCurlDetector(BaseExercise):
    # Thresholds for detecting stages of the biceps curl
    UP_THRESHOLD = 50      # Elbow angle ≤ 50° → "up" stage (arm fully curled)
    DOWN_THRESHOLD = 160   # Elbow angle ≥ 160° → "down" stage (arm fully extended)

    # Minimum visibility confidence required for pose landmarks
    MIN_VISIBILITY = 0.7   # Ensures only reliable landmarks are used

    # Tolerance for elbow drift (to check if elbow stays fixed near torso)
    ELBOW_DRIFT_TOLERANCE = 0.06  # Acceptable normalized drift of elbow position
    # Ensures the elbow stays close to the torso. If the elbow moves too far away, it indicates incorrect form. Normalized tolerance accounts for different body sizes.

    # Threshold for detecting arm swing (to prevent cheating by moving shoulder too much)
    SWING_THRESHOLD = 15   # If shoulder angle changes more than 15°, it’s considered swinging
    # If the shoulder angle changes more than 15°, it’s considered “swinging” the arm instead of isolating the biceps.

    # Landmark indices (from Mediapipe Pose model)
    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24


    def __init__(self):
        # Call the parent class (BaseExercise) constructor. This initializes common attributes like reps and stage
        super().__init__()

        # Baseline x‑coordinate of the shoulder (used to detect elbow drift). Will be set during the first valid detection
        self._shoulder_x_baseline = None


    def reset(self) -> None:
        self.reps = 0
        self.stage = None
        self._shoulder_x_baseline = None     # Reset shoulder baseline so drift can be recalculated fresh


    def process(self, landmarks) -> dict:
        # 1. Get visibility scores for left and right elbows
        left_vis = landmarks[self.LEFT_ELBOW].visibility
        right_vis = landmarks[self.RIGHT_ELBOW].visibility

        # 2. Choose the side (left or right) with higher visibility --> ensures we use the more reliable arm for detection
        if left_vis >= right_vis:
            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST

        # 3. Calculate elbow angle (shoulder–elbow–wrist)
        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx),
        )

        # 4. Check if key landmarks (shoulder, elbow, wrist) are visible enough --> ensures we have sufficient data to make accurate assessments
        key_landmarks_visible = landmarks[shoulder_idx].visibility > self.MIN_VISIBILITY and landmarks[elbow_idx].visibility > self.MIN_VISIBILITY and landmarks[wrist_idx].visibility > self.MIN_VISIBILITY


        # 5. Stage detection and rep counting
        if key_landmarks_visible:
            # If elbow angle < UP_THRESHOLD → arm fully curled
            if elbow_angle < self.UP_THRESHOLD:
                self.stage = "up"

            # If elbow angle > DOWN_THRESHOLD and previous stage was "up" --> one full rep completed
            if elbow_angle > self.DOWN_THRESHOLD and self.stage == "up":
                self.stage = "down"
                self.reps += 1


        # 6. Elbow drift detection (checks if elbow stays close to shoulder)
        shoulder_x = landmarks[shoulder_idx].x
        elbow_x = landmarks[elbow_idx].x
        elbow_drift = abs(elbow_x - shoulder_x)

        if elbow_drift <= self.ELBOW_DRIFT_TOLERANCE:
            shoulder_status = "STABLE"
        else:
            shoulder_status = "ELBOW DRIFTING"


        # 7. Swing detection (checks if torso is swinging) -->  uses midpoint of shoulders and hips to measure torso tilt
        shoulder_mid_x = (landmarks[self.LEFT_SHOULDER].x + landmarks[self.RIGHT_SHOULDER].x) / 2
        shoulder_mid_y = (landmarks[self.LEFT_SHOULDER].y + landmarks[self.RIGHT_SHOULDER].y) / 2

        hip_mid_x = (landmarks[self.LEFT_HIP].x + landmarks[self.RIGHT_HIP].x) / 2
        hip_mid_y = (landmarks[self.LEFT_HIP].y + landmarks[self.RIGHT_HIP].y) / 2

        dx = shoulder_mid_x - hip_mid_x
        dy = shoulder_mid_y - hip_mid_y


        # Calculate torso angle relative to vertical axis
        torso_angle_from_vertical = self._safe_angle(dx, dy)

        if torso_angle_from_vertical <= self.SWING_THRESHOLD:
            swing_status = "NO SWING"
        else:
            swing_status = "SWINGING"


        # 8. Return analysis results
        return {
            "reps": self.reps,                  # total reps counted
            "elbow_angle": int(elbow_angle),    # current elbow angle
            "shoulder_status": shoulder_status, # elbow stability feedback
            "swing_status": swing_status        # torso swing feedback
        }



    # here we define a helper function to calculate the angle of the torso relative to the vertical axis. This is used to detect swinging movements during biceps curls.
    # Here _safe_angle is a private method (indicated by the underscore) that calculates the angle in degrees between the torso vector (dx, dy) and the vertical axis. It uses the arctangent function to compute the angle and handles cases where dy is zero to avoid division by zero errors.
    # Here atan2 is a mathematical function that computes the angle (in radians) between the positive x-axis and the point (x, y). It takes into account the signs of both arguments to determine the correct quadrant of the angle. The result is then converted to degrees using math.degrees().
    def _safe_angle(self, dx, dy):
        # Calculate angle in degrees between the torso vector (dx, dy) and vertical axis
        # Uses atan2 to handle both positive and negative values safely
        # Here 2 in atan2 means we will pass two arguments to the function: dx (horizontal displacement) and dy (vertical displacement). The function will return the angle in radians between the positive x-axis and the point (dx, dy). This is useful for calculating angles in 2D space, especially when determining the orientation of the torso relative to vertical. 
        # abs(dx) → horizontal displacement, abs(dy) → vertical displacement
        # If dy == 0 (to avoid division by zero), return 0.0 as a safe fallback
        return math.degrees(math.atan2(abs(dx), abs(dy))) if dy != 0 else 0.0
    
    