# Here in this file, we will define a function to synchronize the latest workout metrics from the video processor to the Streamlit session state. This ensures that the UI reflects the most up-to-date information about reps, sets, and exercise form feedback during a workout session.

import streamlit as st

from services.config.workout_config import METRICS_FIELDS


# The sync_metrics_update function takes a context object (which contains the video processor and state information) and updates the Streamlit session state with the latest metrics for the current exercise. It checks if the workout is active, retrieves the latest metrics from the video processor, and updates relevant session state variables such as reps, sets completed, and form feedback fields.
def sync_metrics_update(context):
    # Validate context, If context is missing, has no 'state', or video is not playing → exit early
    # Here this 'state' refers to the state of the video processor (whether it's actively processing video frames). If the video is not playing, we don't need to update metrics.
    if not context or not hasattr(context, "state") or not context.state.playing:
        return
    
    # Get the video processor from context
    # The video processor is responsible for analyzing the video feed, detecting poses, and calculating metrics like reps and angles. If it's not available, we cannot update metrics.
    processor = getattr(context, "video_processor", None)
    # SO now this processor is an instance of the VideoProcessor class, which handles the real-time analysis of the video feed to compute exercise metrics. If it's None, we exit early since we cannot retrieve metrics without it.

    if not processor:
        return 
    
    exercise = st.session_state.get("exercise_type")

    if not exercise:
        return
    
    # Set the current exercise in the video processor so it knows which exercise's metrics to compute. Then retrieve the latest metrics for that exercise.
    processor.set_exercise(exercise)

    # Here we retrieve the latest metrics from the video processor. This includes counts of reps, angles, and qualitative feedback on form. If no metrics are available, we exit early.
    latest_metrics = processor.get_latest_metrics()

    if not latest_metrics:
        return
    
    # Update the Streamlit session state with the latest metrics. We first get the total reps completed from the latest metrics. If it's None, we default it to 0. Then we update the session state with this value.
    reps = latest_metrics.get("reps", 0)

    if reps is None:    # If the reps value is None (which can happen if the video processor hasn't detected any reps yet), we default it to 0 to avoid issues in calculations later.
        reps = 0
        
    st.session_state.reps = reps

    # Get the specific fields to update for the current exercise from the METRICS_FIELDS configuration. This allows us to only update relevant metrics for the exercise being performed.
    fields = METRICS_FIELDS.get(exercise)

    if not fields:
        return 

    # Update each relevant field in the session state with the latest value from the video processor. If a metric is missing, we use a default value (0 for numeric fields, "N/A" for qualitative feedback).
    for key, default in fields.items():
        st.session_state[key] = latest_metrics.get(key, default)

    # After updating the reps, we also calculate the number of sets completed and the number of reps in the current set based on the total reps, planned reps per set, and target sets. This ensures that the session state reflects the user's progress accurately.
    reps_per_set = st.session_state.get("reps_per_set", 0)
    target_sets = st.session_state.get("target_sets", 0)

    # If reps is not None and reps_per_set and target_sets are greater than 0, we calculate the number of sets completed and the number of reps in the current set. We also determine if the workout is complete based on whether the number of sets completed meets or exceeds the target sets. If any of these values are invalid (e.g., reps_per_set or target_sets are 0), we default to 0 for sets completed and current set reps, and mark the workout as not complete.
    if reps is not None and reps_per_set > 0 and target_sets > 0:
        # Calculate sets completed and current set reps based on total reps, planned reps per set, and target sets. This ensures that the session state reflects the user's progress accurately.
        sets_completed = reps // reps_per_set      # here we are using integer division (//) to calculate how many full sets have been completed based on the total reps and the planned reps per set. This gives us the number of complete sets.
        current_set_reps = reps % reps_per_set     # here we are using the modulo operator (%) to calculate how many reps have been completed in the current set. This gives us the remainder of reps after accounting for full sets.
        workout_completed = sets_completed >= target_sets 
    else:
        sets_completed = 0
        current_set_reps = 0
        workout_completed = False


    # Update the session state with the calculated values for sets completed, current set reps, and workout completion status. This allows the UI to display accurate progress information to the user.
    st.session_state.sets_completed = sets_completed
    st.session_state.current_set_reps = current_set_reps
    st.session_state.workout_completed = workout_completed

    

  