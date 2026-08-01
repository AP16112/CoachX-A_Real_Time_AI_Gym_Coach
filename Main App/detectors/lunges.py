# Here in this file, we will write the logic and code for lunges exercise detection and counting the number of reps done by the user.

# We will use the BaseExercise class to create a LungesDetector class that will handle the lunges detection logic.
from core.base_exercise import BaseExercise


# The LungesDetector class extends the BaseExercise class and implements the logic to detect lunges based on the angles of the knees and torso. It counts repetitions and provides feedback on balance and torso alignment.
class LungesDetector(BaseExercise):
    # Thresholds for detecting stages of the lunge
    DOWN_THRESHOLD = 100    # Knee angle ≤ 100° → "down" stage (deep lunge)
    UP_THRESHOLD = 160      # Knee angle ≥ 160° → "up" stage (standing tall)

    # Minimum visibility confidence required for pose landmarks
    MIN_VISIBILITY = 0.7    # Ensures only reliable landmarks are used

    # Tolerance for balance (checks if body weight is evenly distributed)
    BALANCE_TOLERANCE = 0.10  # Acceptable normalized difference between left/right sides

    # Landmark indices (from Mediapipe Pose model)
    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27
    RIGHT_HIP = 24
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12


    def __init__(self):
        # Call BaseExercise constructor to initialize reps and stage
        super().__init__()

    def reset(self) -> None:
        # Reset repetition count and stage to initial state
        self.reps = 0
        self.stage = None
    

    def process(self, landmarks) -> dict:
        # 1. Calculate knee angles for both legs
        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE),
            self.get_point(landmarks, self.LEFT_ANKLE),
        )

        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE),
            self.get_point(landmarks, self.RIGHT_ANKLE),
        )

        
        # 2. Determine which leg is in front (smaller knee angle = deeper bend)
        if left_knee_angle <= right_knee_angle:
            front_knee_angle = left_knee_angle
            front_hip_idx = self.LEFT_HIP
            front_knee_idx = self.LEFT_KNEE
            front_ankle_idx = self.LEFT_ANKLE
            shoulder_idx_for_torso = self.LEFT_SHOULDER
        else:
            front_knee_angle = right_knee_angle
            front_hip_idx = self.RIGHT_HIP
            front_knee_idx = self.RIGHT_KNEE
            front_ankle_idx = self.RIGHT_ANKLE
            shoulder_idx_for_torso = self.RIGHT_SHOULDER

        # 3. Check if key landmarks are visible enough
        key_landmarks_visible = landmarks[front_hip_idx].visibility > self.MIN_VISIBILITY and landmarks[front_knee_idx].visibility > self.MIN_VISIBILITY and landmarks[front_ankle_idx].visibility > self.MIN_VISIBILITY


        # 4. Stage detection and rep counting
        if key_landmarks_visible:
            # If knee angle < DOWN_THRESHOLD → deep lunge
            if front_knee_angle < self.DOWN_THRESHOLD:
                self.stage = "down"

            # If knee angle > UP_THRESHOLD and previous stage was "down" -->  one full rep completed
            if front_knee_angle > self.UP_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.reps += 1


        # 5. Torso angle calculation (shoulder–hip–knee)
        torso_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx_for_torso),
            self.get_point(landmarks, front_hip_idx),
            self.get_point(landmarks, front_knee_idx),
        )


        # 6. Balance detection (checks if shoulders and hips are aligned) i.e Balance check (compare shoulder midpoint vs hip midpoint)
        shoulder_mid_x = (landmarks[self.LEFT_SHOULDER].x + landmarks[self.RIGHT_SHOULDER].x) / 2
        hip_mid_x = (landmarks[self.LEFT_HIP].x + landmarks[self.RIGHT_HIP].x) / 2
        lateral_offset = abs(shoulder_mid_x - hip_mid_x)


        if lateral_offset <= self.BALANCE_TOLERANCE:
            balance_status = "BALANCED"
        else:
            balance_status = "OFF BALANCE"


        # 7. Return analysis results in the form of a dictionary containing reps, front knee angle, torso angle, and balance status. This can be used for UI display or further processing.
        return {
            "reps": self.reps,
            "front_knee_angle": int(front_knee_angle),
            "torso_angle": int(torso_angle),
            "balance_status": balance_status,
        }
    

    