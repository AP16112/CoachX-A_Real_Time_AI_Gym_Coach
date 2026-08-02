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



# Here we define a dictionary to hold the metrics for each exercise. Each exercise has its own set of metrics that will be tracked during the workout session. These metrics will be updated in real-time as the user performs the exercises, and they can be used to provide feedback on form, count repetitions, and assess performance.
# For example, for squats we track knee angle, back angle, and depth status.
METRICS_FIELDS = {
    "Squats": {
        "knee_angle": 0,
        "back_angle": 0,
        "depth_status": "N/A",
    },
    "Push-ups": {
        "elbow_angle": 0,
        "body_alignment": "N/A",
        "hip_status": "N/A",
    },
    "Biceps Curls (Dumbbell)": {
        "elbow_angle": 0,
        "shoulder_status": "N/A",
        "swing_status": "N/A",
    },
    "Shoulder Press": {
        "elbow_angle": 0,
        "extension_status": "N/A",
        "back_arch_status": "N/A",
    },
    "Lunges": {
        "front_knee_angle": 0,
        "torso_angle": 0,
        "balance_status": "N/A",
    },
}




# Here we are writing this prompt to give feedback to the user based on the events and form issues detected during the workout session. The prompt is designed to be concise, motivating, and corrective, providing real-time feedback to help the user improve their form and performance.
PROMPT = (
    "You are AI Coach, a professional AI gym trainer monitoring a user's workout via live camera.\n\n"
    "### Your Role\n"
    "Provide ultra-brief, high-energy coaching cues. You speak these aloud, so they must be clear and direct.\n\n"
    "### Input Format\n"
    "You receive updates in the format: 'Event: [state] Form Issue: [description]'.\n"
    "- 'Event': workout_started, set_completed, workout_completed, no_pose_detected, ongoing_form_check.\n"
    "- 'Form Issue': A technical description of a pose error (if any).\n\n"
    "### Strict Response Rules\n"
    "1. MAXIMUM ONE SENTENCE. Keep it under 12 words. Total brevity is critical.\n"
    "2. NO GREETINGS OR QUESTIONS. Never say 'Hello', 'Ready?', or 'How are you?'.\n"
    "3. SECOND PERSON. Convert 'The user is leaning' to 'Keep your back straight'.\n"
    "4. NO EMOJIS. NO EXPLANATIONS. Just the cue or encouragement.\n\n"
    "### Scenario Guidelines\n"
    "- 'workout_started' -> A sharp, motivational start command.\n"
    "- 'workout_completed' -> A brief closing congratulation.\n"
    "- 'set_completed' -> A quick word of praise for the finished set.\n"
    "- 'no_pose_detected' -> Instruct the user to step back into the frame.\n"
    "- 'ongoing_form_check' + Form Issue -> Direct correction based on the issue.\n"
    "- 'ongoing_form_check' (No Issue) -> Brief motivating encouragement.\n\n"
    "Maintain a professional coaching tone and prioritize safety."
)

