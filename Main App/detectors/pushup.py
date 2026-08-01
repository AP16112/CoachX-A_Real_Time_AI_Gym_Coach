# Here in this file, we will write the logic and code for push-up exercise detection and counting the number of reps done by the user.

# We will use the BaseExercise class to create a PushUpDetector class that will handle the push-up detection logic.
from core.base_exercise import BaseExercise


# The PushUpDetector class extends the BaseExercise class and implements the logic to detect push-ups based on the angles of the elbows and body alignment. It counts repetitions and provides feedback on body alignment and hip sagging.
class PushUpDetector(BaseExercise):
    # Thresholds for detecting stages of the push‑up
    DOWN_THRESHOLD = 90     # Elbow angle ≤ 90° → "down" stage (chest lowered)
    UP_THRESHOLD = 160      # Elbow angle ≥ 160° → "up" stage (arms extended)

    # Minimum visibility confidence required for pose landmarks
    MIN_VISIBILITY = 0.7    # Ensures only reliable landmarks are used

    # Tolerance for hip sag (to check if hips drop too low compared to shoulders/ankles)
    HIP_SAG_TOLERANCE = 0.08  # Normalized tolerance for hip position

    # Landmark indices (from Mediapipe Pose model)
    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28


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

        # 2. Choose the side (left or right) with higher visibility -->  ensures we use the more reliable arm for detection
        if left_vis >= right_vis:
            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST
            hip_idx = self.LEFT_HIP
            ankle_idx = self.LEFT_ANKLE
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST
            hip_idx = self.RIGHT_HIP
            ankle_idx = self.RIGHT_ANKLE


        # 3. Calculate elbow angle (shoulder–elbow–wrist)
        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx),
        )


        # 4. Calculate body angle (shoulder–hip–ankle) → checks alignment
        body_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, ankle_idx),
        )


        # 5. Calculate hip deviation (to detect sagging or piking)
        shoulder_y = landmarks[shoulder_idx].y
        ankle_y = landmarks[ankle_idx].y
        hip_y = landmarks[hip_idx].y

        expected_hip_y = (shoulder_y + ankle_y) / 2
        hip_deviation = hip_y - expected_hip_y

        # 6. Check if all key landmarks are visible
        key_landmarks_visible = landmarks[shoulder_idx].visibility > self.MIN_VISIBILITY and landmarks[elbow_idx].visibility > self.MIN_VISIBILITY and landmarks[wrist_idx].visibility > self.MIN_VISIBILITY and landmarks[hip_idx].visibility > self.MIN_VISIBILITY

        # 7. Stage detection and rep counting
        if key_landmarks_visible:
            # If elbow angle < DOWN_THRESHOLD → body lowered
            if elbow_angle < self.DOWN_THRESHOLD:
                self.stage = "down"

             # If elbow angle > UP_THRESHOLD and previous stage was "down" -->  one full rep completed
            if elbow_angle > self.UP_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.reps += 1


        # 8. Body alignment feedback
        if body_angle > 160:
            body_alignment = "Straight"
        elif body_angle > 140:
            body_alignment = "Slight Bend"
        else:
            body_alignment = "Poor Form"


        # 9. Hip status feedback
        if abs(hip_deviation) <= self.HIP_SAG_TOLERANCE:
            hip_status = "LEVEL"
        elif hip_deviation > self.HIP_SAG_TOLERANCE:
            hip_status = "SAGGING"
        else:
            hip_status = "PIKED UP"

        # 10. Return push-up analysis results in the form of a dictionary containing reps, elbow angle, body alignment, and hip status. This can be used for UI display or further processing.
        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "body_alignment": body_alignment,
            "hip_status": hip_status,
        }
    

