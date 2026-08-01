# Here in this file, we will defines the different options which we can use anywhere in this project.
# THis file is acting as a central configuration module for our AI gym coach project.  


# A list of supported exercises in our app. Used for dropdowns, workout plans, or validation so users can only pick recognized exercises. Keeps exercise names consistent across the app.
EXERCISE_OPTIONS=[
    "Squats",
    "Push-ups",
    "Biceps Curls (Dumbbell)",
    "Shoulder Press",
    "Lunges"
]


# A list of keypoint connections for pose estimation. Each tuple represents a pair of landmark indices that should be connected with a line to visualize the skeleton. These indices correspond to the landmarks detected by MediaPipe’s PoseLandmarker model.
# So here each tuple in the list represents a connection between two body landmarks. For example, (11, 12) connects the left shoulder (index 11) to the right shoulder (index 12). This is used to draw the skeleton overlay on the video feed.
POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),       # Shoulders & Arms
    (11, 23), (12, 24), (23, 24),                           # Torso / Hips
    (23, 25), (24, 26), (25, 27), (26, 28), (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)  # Legs
]