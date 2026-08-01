# Here in this file, we will write the logic and code for shoulder press exercise detection and counting the number of reps done by the user.


# We will use the BaseExercise class to create a ShoulderPressDetector class that will handle the shoulder press detection logic.
from core.base_exercise import BaseExercise


# The ShoulderPressDetector class extends the BaseExercise class and implements the logic to detect shoulder presses based on the angles of the elbows and back. It counts repetitions and provides feedback on press depth.
class ShoulderPressDetector(BaseExercise):
    # Thresholds for detecting stages of the shoulder press
    UP_THRESHOLD = 160    # Arm angle ≥ 160° → "up" stage (arms extended overhead)
    DOWN_THRESHOLD = 90   # Arm angle ≤ 90° → "down" stage (arms lowered)
    
    # Minimum visibility confidence required for pose landmarks
    MIN_VISIBILITY = 0.7  # Ensures only reliable landmarks are used

    # Landmark indices (from Mediapipe Pose model)
    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26

    
    def __init__(self):
        # Call BaseExercise constructor to initialize reps and stage
        super().__init__()


    def reset(self) -> None:
        # Reset repetition count and stage to initial state
        self.reps = 0
        self.stage = None


    def process(self, landmarks) -> dict:
        # 1. Get visibility scores for left and right elbows
        left_vis = landmarks[self.LEFT_ELBOW].visibility
        right_vis = landmarks[self.RIGHT_ELBOW].visibility


        # 2. Choose the side (left or right) with higher visibility --> ensures we use the more reliable arm for detection
        if left_vis >= right_vis:
            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST
            hip_idx = self.LEFT_HIP
            knee_idx = self.LEFT_KNEE
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST
            hip_idx = self.RIGHT_HIP
            knee_idx = self.RIGHT_KNEE


        # 3. Calculate elbow angle (shoulder–elbow–wrist) --> used to determine arm position during shoulder press
        # Here we need to pass shoulder, elbow and wrist idx in this order because we are calculating the angle at the elbow joint, which is formed by the line segments shoulder–elbow and elbow–wrist. The angle at the elbow indicates whether the arm is extended or flexed during the press.
        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx),
        )

        # 4. Check if key landmarks (shoulder, elbow, wrist) are visible enough --> ensures we have sufficient data to make accurate assessments
        key_landmarks_visible = landmarks[shoulder_idx].visibility > self.MIN_VISIBILITY and landmarks[elbow_idx].visibility > self.MIN_VISIBILITY and landmarks[wrist_idx].visibility > self.MIN_VISIBILITY


        # 5. Stage detection and rep counting
        if key_landmarks_visible:
            # If elbow angle > UP_THRESHOLD → arms extended overhead
            if elbow_angle > self.UP_THRESHOLD:
                self.stage = "up"

            # If elbow angle < DOWN_THRESHOLD and previous stage was "up" -->  one full rep completed
            if elbow_angle < self.DOWN_THRESHOLD and self.stage == "up":
                self.stage = "down"
                self.reps += 1


        # 6. Extension status feedback based on elbow angle
        if elbow_angle >= self.UP_THRESHOLD:
            extension_status = "FULL EXTENSION"
        elif elbow_angle >= 130:
            extension_status = "NEARLY EXTENDED"
        elif elbow_angle >= self.DOWN_THRESHOLD:
            extension_status = "PRESSING"
        else:
            extension_status = "START POSITION"


        # 7. Calculate back angle (shoulder–hip–knee) to check posture
        back_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
        )

        # 8. Back arch status feedback based on back angle
        if back_angle >= 160:
            back_arch_status = "Neutral"
        elif back_angle >= 140:
            back_arch_status = "Slight Arch"
        else:
            back_arch_status = "Excessive Arch"

        # 9. Return shoulder press analysis results in the form of a dictionary containing reps, elbow angle, extension status, and back arch status. This can be used for UI display or further processing.
        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "extension_status": extension_status,
            "back_arch_status": back_arch_status,
        }
    
