# Here in this file, we will set or initialize all the session state variables with some default values
# Initialization of session state :-


import streamlit as st


def initial_session_defaults():
    # Define a dictionary of default values for workout tracking
    defaults = {
        # Core workout counters
        "reps": 0,                       # Total repetitions done so far
        "target_sets": 0,                # Target number of sets planned
        "reps_per_set": 0,               # Target repetitions per set
        "sets_completed": 0,             # Number of sets completed so far
        "current_set_reps": 0,           # Reps done in the current set
        "workout_complete": False,       # Flag to mark workout completion
        "last_notified_sets_completed": 0,   # Last set count notified to user
        "last_notified_workout_complete": False, # Whether workout completion was notified
        "last_saved_sets_completed": 0,  # Last saved set count (for persistence)
        "set_cycle_started_at": 0.0,     # Timestamp when current set started
        "last_exercise_type": "Squats",  # Last exercise performed

        # Workout plan (predefined before starting)
        "workout_started": False,        # Flag to indicate workout has begun
        "plan_exercise": "Squats",       # Planned exercise type
        "plan_sets": 3,                  # Planned number of sets
        "plan_reps": 10,                 # Planned reps per set

        # Common angles tracked by pose estimation
        "knee_angle": 0,                 # Knee joint angle
        "back_angle": 0,                 # Back posture angle
        "elbow_angle": 0,                # Elbow joint angle
        "front_knee_angle": 0,           # Angle of front knee (for lunges etc.)
        "torso_angle": 0,                # Torso alignment angle

        # Status fields (qualitative feedback on form)
        "depth_status": "N/A",           # Squat depth status
        "body_alignment": "N/A",         # Overall body alignment
        "hip_status": "N/A",             # Hip position status
        "shoulder_status": "N/A",        # Shoulder alignment
        "swing_status": "N/A",           # Swinging movement status
        "extension_status": "N/A",       # Extension posture status
        "back_arch_status": "N/A",       # Back arching status
        "balance_status": "N/A",         # Balance status
    }


    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

