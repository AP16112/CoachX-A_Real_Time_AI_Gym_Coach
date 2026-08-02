# Here in this file, we will write the logic and code for squat exercise detection and counting the number of reps done by the user.


# We will use the BaseExercise class to create a SquatDetector class that will handle the squat detection logic.
from core.base_exercise import BaseExercise


# The SquatDetector class extends the BaseExercise class and implements the logic to detect squats based on the angles of the knees and back. It counts repetitions and provides feedback on squat depth.
class SquatDetector(BaseExercise):
    # Thresholds for detecting squat stages based on knee angle
    DOWN_THRESHOLD = 100    # If knee angle < 100°, user is considered in "down" squat position
    UP_THRESHOLD = 160      # If knee angle > 160°, user is considered in "up" standing position
    
    # Minimum visibility confidence required for pose landmarks (from Mediapipe or similar)
    MIN_VISIBILITY = 0.7
    # Here we are taking the min visibility as 0.7 because it ensures that the landmarks we are using to calculate angles are reliable enough for accurate squat detection. If the visibility is below this threshold, we may not have enough confidence in the landmark positions, which could lead to incorrect angle calculations and rep counting.

    # Landmark indices (from Mediapipe Pose model)
    # Here we are taking these indices from mediapipe pose model because these are the indices of the landmarks that we will use to calculate the angles for squat detection. These indices correspond to specific body parts in the pose estimation model.
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


    def reset(self):
        # Reset repetition count and stage to initial state
        self.reps = 0
        self.stage = None


    def process(self, landmarks):
        # 1. Calculate left knee angle (hip–knee–ankle)
        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE),
            self.get_point(landmarks, self.LEFT_ANKLE)
        )

        # 2. Calculate right knee angle (hip–knee–ankle)
        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE),
            self.get_point(landmarks, self.RIGHT_ANKLE)
        )

        # 3. Get visibility scores for knees (confidence from pose detection)
        left_vis = landmarks[self.LEFT_KNEE].visibility
        right_vis = landmarks[self.RIGHT_KNEE].visibility

        # 4. Choose the side (left or right) with higher visibility --> ensures we use the more reliable knee angle
        if left_vis >= right_vis:
            knee_angle = left_knee_angle
            hip_idx, knee_idx, ankle_idx, shoulder_idx = self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_ANKLE, self.LEFT_SHOULDER
        else:
            knee_angle = right_knee_angle
            hip_idx, knee_idx, ankle_idx, shoulder_idx = self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_ANKLE, self.RIGHT_SHOULDER


        # 5. Calculate back angle (shoulder–hip–knee) --> used to check posture alignment during squat
        # Here we need to pass shoulder, hip and knee idx in this order because we are calculating the angle at the hip joint, which is formed by the line segments shoulder–hip and hip–knee. The angle at the hip is what indicates whether the back is upright or leaning forward during the squat.
        back_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx)
        )
    
        # 6. Check if key landmarks (hip, knee, ankle) are visible enough --> ensures we have sufficient data to make accurate assessments
        key_landmark_visible = landmarks[hip_idx].visibility >= self.MIN_VISIBILITY and landmarks[knee_idx].visibility >= self.MIN_VISIBILITY and landmarks[ankle_idx].visibility >= self.MIN_VISIBILITY

        # 7. Stage detection and rep counting
        if key_landmark_visible:
            # If knee angle < DOWN_THRESHOLD → squat down
            if knee_angle < self.DOWN_THRESHOLD:
                self.stage = "down"

            # If knee angle >= UP_THRESHOLD and previous stage was "down" --> squat completed, increment rep count
            if knee_angle >= self.UP_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.reps += 1


        # 8. Depth status feedback --> provides qualitative feedback on squat depth based on knee angle and current stage
        if self.stage == "down":
            depth_status = "GOOD DEPTH" if knee_angle <= self.DOWN_THRESHOLD else "TOO HIGH"
        elif self.stage == "up":
            depth_status = "STANDING"
        else:
            depth_status = "N/A"


        # 9. Return squat analysis results in the form of a dictionary containing reps, knee angle, back angle, and depth status. This can be used for UI display or further processing.
        return {
            "reps": self.reps,             # total reps counted
            "knee_angle": int(knee_angle), # current knee angle
            "back_angle": int(back_angle), # current back angle
            "depth_status": depth_status   # squat quality feedback
        }
    


