# Here in this file, we will define a function to synchronize the latest workout metrics from the video processor to the Streamlit session state. This ensures that the UI reflects the most up-to-date information about reps, sets, and exercise form feedback during a workout session.

import streamlit as st
import time

from services.config.workout_config import METRICS_FIELDS
from services.persistence.exercise_repository import add_exercise


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

    # Here we check if the number of sets completed has increased since the last time we saved it. If so, we calculate how many new sets have been completed, the time taken for those sets, and log this information to the database using the add_exercise function. We also update the timestamp for when the current set cycle started and the last saved sets completed in the session state. This ensures that we persist progress data accurately and can track user performance over time.
    last_saved_sets = st.session_state.get("last_saved_sets_completed", 0)

    # If the user has completed new sets since the last save, we log the exercise data to the database. We calculate how many new sets have been completed, the time taken for those sets, and call the add_exercise function to persist this information. We also update the timestamp for when the current set cycle started and the last saved sets completed in the session state. This ensures that we accurately track user progress and can provide meaningful feedback on their workout performance.
    if target_sets > 0 and reps_per_set > 0 and sets_completed > last_saved_sets:
        newly_completed = sets_completed - last_saved_sets
        now_ts = time.time()    # Get the current timestamp to calculate the time taken for the newly completed sets. This timestamp will be used to determine how long it took the user to complete the new sets since the last save.  
        started_at = st.session_state.get("set_cycle_started_at", now_ts)
        time_taken = now_ts - started_at
        user_id = st.session_state.get("user_id", 0)

        # Log the newly completed sets to the database for persistence. We call the add_exercise function with the user ID, exercise type, total reps for the newly completed sets, number of newly completed sets, and the time taken to complete those sets. This allows us to track user performance over time and provide insights into their workout progress.
        add_exercise(user_id, exercise, newly_completed * reps_per_set, newly_completed, time_taken)


        # Here we check if the voice coaching pipeline is available in the session state. If it is, we call the process_event method of the voice pipeline to generate spoken feedback based on the current exercise and metrics. If feedback is generated, we store the audio bytes and text feedback in the session state for playback and display in the UI. This allows us to provide real-time auditory coaching to the user based on their performance and form during the workout.
        if st.session_state.get("voice_pipeline"):
            result = st.session_state.voice_pipeline.process_event(
                event="set_completed",    # Here we are passing the event as "set_completed" to indicate that a set has just been completed. This allows the voice pipeline to generate feedback specific to the completion of a set, such as congratulating the user or providing form corrections based on the latest metrics.
                exercise=exercise,
                metrics=latest_metrics,
            )

            if result:
                st.session_state.audio_to_play, st.session_state.coach_feedback = result


        # Now we update the session state to reflect the new timestamp for when the current set cycle started and the last saved sets completed. This ensures that we accurately track progress and can calculate time taken for future sets correctly.
        st.session_state.set_cycle_started_at = now_ts
        st.session_state.last_saved_sets_completed = sets_completed

    
    # Here we check if the workout has been completed and if we have not already notified the user about the workout completion. If the workout is complete and the user has not been notified, we set a flag in the session state to indicate that the notification has been sent. We then call the process_event method of the voice pipeline to generate spoken feedback for the workout completion event. If feedback is generated, we store the audio bytes and text feedback in the session state for playback and display in the UI. This allows us to provide real-time auditory coaching to the user upon completing their workout.
    if workout_completed and not st.session_state.get("last_notified_workout_complete", False):
        st.session_state.last_notified_workout_complete = True

        if st.session_state.get("voice_pipeline"):
            result = st.session_state.voice_pipeline.process_event(
                event="workout_completed",
                exercise=exercise,
                metrics=latest_metrics,
            )

            if result:
                st.session_state.audio_to_play, st.session_state.coach_feedback = result
                
    # Here we check if the pose is detected in the latest metrics. If no pose is detected and the voice pipeline is available, we call the process_event method of the voice pipeline to generate spoken feedback indicating that no pose was detected and prompting the user to step into the camera frame. If feedback is generated, we store the audio bytes and text feedback in the session state for playback and display in the UI. This allows us to provide real-time auditory coaching to the user when their pose is not detected during a workout session.
    pose_detected = latest_metrics.get("pose_detected", True)
    
    if not pose_detected and st.session_state.get("voice_pipeline"):
        result = st.session_state.voice_pipeline.process_event(
            event="no_pose_detected",
            exercise=exercise,
            metrics={"issue": "No pose detected! Please step into the camera frame."},
        )
    
        if result:
            st.session_state.audio_to_play, st.session_state.coach_feedback = result

    # Here we check if the voice pipeline is available in the session state. If it is, we call the process_event method of the voice pipeline to generate spoken feedback for ongoing form checks during the workout. This allows us to provide real-time auditory coaching to the user based on their performance and form during the workout session.
    if st.session_state.get("voice_pipeline"):
        result = st.session_state.voice_pipeline.process_event(
            event="ongoing_form_check",
            exercise=exercise,
            metrics=latest_metrics,
        )
        
        if result:
            st.session_state.audio_to_play, st.session_state.coach_feedback = result


