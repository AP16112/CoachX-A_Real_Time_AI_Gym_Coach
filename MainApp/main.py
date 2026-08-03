# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Project :- CoachX : "A Real-time AI Gym Coach"

## This project is a real-time AI Gym Trainer that tracks your form, counts reps, and delivers intelligent voice coaching for smarter workouts.
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Here we will use this main.py file to write out streamlit code here
# Actually Streamlit wants some entry point and this main.py is actually acting as the entry point for this project

# Streamlit is an open‑source Python framework designed to make it easy to build and share data apps, dashboards, and interactive machine learning demos with just a few lines of code.

# What Streamlit does :-
# - Lets you turn a Python script into a web app instantly.
# - Focuses on simplicity — you don’t need HTML, CSS, or JavaScript.
# - Perfect for data scientists, ML engineers, and analysts who want to showcase models or visualizations interactively.

# Key Features :-
# - Widgets: Sliders, buttons, text inputs, file uploaders.
# - Charts: Native support for Matplotlib, Plotly, Altair, and more.
# - Live updates: Apps auto‑refresh when you change code.
# - Deployment: Easy to share via Streamlit Cloud or run locally.

# Imports Python’s built-in OS module. Used here to check if the CSS file exists on disk (os.path.exists(file_path)).
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

import time    # here we are importing time module to use sleep function actually, as we are using time.sleep() function in this file

from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loader import load_css, inject_local_font, inject_webrtc_styles
from services.persistence.exercise_repository import init_db
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_video_processor import VideoProcessorClass
from services.tracking.metrics import sync_metrics_update
from services.persistence.exercise_repository import get_users_exercises, add_exercise
from groq import Groq # Here This is a Python client library for interacting with the Groq API, which is a service that provides advanced AI and machine learning capabilities. In this project, we use it to generate intelligent voice feedback based on the user's exercise performance and form.

from services.coaching.llm import LLMCoach
from services.coaching.tts import TextToSpeech
from services.coaching.voice_pipeline import VoicePipeline, autoplay_audio  


# Here we are loading environment variables from a .env file located in the same directory as this main.py file. The load_dotenv function reads the .env file and sets the environment variables so they can be accessed using os.environ.get(). This is useful for storing sensitive information like API keys, database credentials, or configuration settings without hardcoding them into the source code.
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


# Here we are defining a helper function get_config_value(name) that retrieves configuration values from either environment variables or Streamlit's secrets management. It first checks if the value exists in the environment variables using os.environ.get(name). If found, it returns that value. If not, it attempts to fetch the value from Streamlit's secrets (st.secrets.get(name)). If neither source provides the value, it returns None. This function allows for flexible configuration management, enabling sensitive information to be securely stored and accessed without hardcoding it into the application.
def get_config_value(name):
    value = os.environ.get(name)
    if value:
        return value

    try:
        # Here we are checking if the Streamlit secrets management is available (hasattr(st, "secrets")). If it is, we attempt to retrieve the configuration value using st.secrets.get(name). This allows us to securely access sensitive information like API keys or credentials that are stored in Streamlit's secrets management system. If the value is found, it is returned; otherwise, None is returned.
        return st.secrets.get(name, None)
    except Exception:
        return None



# What is streamlit_webrtc? :-
# It’s a Streamlit component that lets you use WebRTC inside Streamlit apps.
# WebRTC enables real‑time audio, video, and data streaming directly in the browser.
# This package bridges Streamlit (Python) with WebRTC (browser APIs) so you can build apps like video chat, live audio processing, or computer vision demos.

# webrtc_streamer :-
# It Creates a WebRTC connection between the browser and your Streamlit backend.
# Usage: You call webrtc_streamer() inside your Streamlit app to start capturing video/audio from the user’s device.
# Features:
# Access webcam and microphone streams.
# Process frames in Python (e.g., apply OpenCV, face detection, ML models).
# Send processed video/audio back to the browser.
# Can also handle data channels for custom peer‑to‑peer messaging.

# WebRtcMode :-
# This enum defines the connection mode:
# SENDONLY → Browser → Streamlit (one‑way stream).
# Example: User uploads webcam feed for ML processing, but doesn’t receive video back.
# RECVONLY → Streamlit → Browser (one‑way stream).
# Example: Server streams a video feed to the user (like a broadcast).
# SENDRECV → Two‑way (peer‑to‑peer style).
# Example: Video chat app — both sides send and receive audio/video.
# DATA → Data channel only (no audio/video).
# Example: Real‑time messaging or sending sensor data.




# Here this fn get_rtc_configuration() is responsible for configuring the ICE servers used in WebRTC connections. It first sets up a default STUN server (stun:stun.l.google.com:19302) to help peers discover their public IP addresses. Then, it checks for TURN server credentials (TURN_URLS, TURN_USERNAME, TURN_CREDENTIAL) from environment variables or Streamlit secrets. If TURN credentials are provided, it adds them to the ICE servers list. Finally, it returns a dictionary containing the configured ICE servers, which is used by the webrtc_streamer component to establish reliable peer-to-peer connections for video streaming.
def get_rtc_configuration():
    ice_servers = [{"urls": ["stun:stun.l.google.com:19302"]}]

    turn_urls = get_config_value("TURN_URLS")
    turn_username = get_config_value("TURN_USERNAME")
    turn_credential = get_config_value("TURN_CREDENTIAL")

    if turn_urls and turn_username and turn_credential:
        if isinstance(turn_urls, str):
            turn_urls = [url.strip() for url in turn_urls.split(",") if url.strip()]

        ice_servers.append(
            {
                "urls": turn_urls,
                "username": turn_username,
                "credential": turn_credential,
            }
        )

    # Here we are returning a dictionary with the key "iceServers" and its value set to the list of ICE servers we configured. This dictionary is used by the WebRTC connection to establish peer-to-peer communication between the browser and the Streamlit backend. The ICE servers help in NAT traversal, allowing the peers to discover their public IP addresses and relay media streams if direct connections fail.
    return {"iceServers": ice_servers}

# What TURN :-
# WebRTC tries to connect your browser camera to the Streamlit server using ICE servers.
# STUN = tries to find a direct connection
# TURN = relays the video if direct connection fails
# We already have STUN. TURN is only needed when networks/firewalls block the direct WebRTC route.




def save_unsaved_workout_progress():
    user_id = st.session_state.get("user_id", 0)
    exercise = st.session_state.get("exercise_type")
    reps = int(st.session_state.get("reps", 0) or 0)
    reps_per_set = int(st.session_state.get("reps_per_set", 0) or 0)
    last_saved_sets = int(st.session_state.get("last_saved_sets_completed", 0) or 0)

    if not isinstance(user_id, int) or not exercise or reps <= 0:
        return

    saved_reps = last_saved_sets * reps_per_set if reps_per_set > 0 else 0
    unsaved_reps = max(reps - saved_reps, 0)

    if unsaved_reps <= 0:
        return

    unsaved_sets = unsaved_reps // reps_per_set if reps_per_set > 0 else 0
    now_ts = time.time()
    started_at = st.session_state.get("set_cycle_started_at", now_ts)
    time_taken = int(now_ts - started_at)

    add_exercise(user_id, exercise, unsaved_reps, unsaved_sets, time_taken)
    st.session_state.last_saved_sets_completed = last_saved_sets + unsaved_sets





def main():
    st.set_page_config(
        page_title="CoachX : A Real-time AI Gym Coach",     # page_title sets the browser tab title
        page_icon="🏋️‍♀️",        # small icon visible before this page_title
        initial_sidebar_state="expanded",
        layout="centered"
    )


    # os.getcwd() :- Returns the current working directory (the folder where your app is running).
    # os.path.join(os.getcwd(), "static", "style.css")  :- Joins the current directory with "static/style.css". This builds a full file path to your CSS file inside a static folder.
    # load_css(...) :- Calls our helper function load_css (which you defined earlier).
    # That function: Checks if the file exists. Reads the CSS file. Injects its contents into your Streamlit app using st.markdown("<style>...</style>").
    load_css(os.path.join(os.getcwd(), "static", "style.css"))
    
    # os.path.join(os.getcwd(), "static", "AdobeClean.otf") :- Builds the full path to the font file inside our static folder.
    # Example result: /Users/Arpit/Projects/CoachX/static/AdobeClean.otf.
    # inject_local_font(..., "AdobeClean") :- Calls our custom function inject_local_font.
    # Parameters: Font path → the actual file location of AdobeClean.otf.
    # Font name → the name we want to assign in CSS ("AdobeClean").
    # Inside the function: Reads the font file in binary. Encodes it as Base64. Injects it into your Streamlit app via a CSS @font-face rule.
    inject_local_font(os.path.join(os.getcwd(), "static", "AdobeClean.otf"), "AdobeClean")


    init_db()      # we are initializing the db i.e created the DB tables

    if not render_login_wall():
        return
    

    # Here we initializing the session state variables at first
    initial_session_defaults()

    # Here we are checking if the voice_pipeline is already initialized in the session state. If not, we create a new instance of VoicePipeline with LLMCoach and TextToSpeech components. This ensures that the voice feedback system is ready to provide real-time coaching during workouts.
    if "voice_pipeline" not in st.session_state:
        try:
            api_key = os.environ.get("GROQ_API_KEY", "")    # Here we are trying to get the Groq API key from the environment variables. If it's not set, we check if it's available in Streamlit's secrets management. This allows us to securely access the API key needed for the LLMCoach to generate intelligent feedback.

            # If the API key is not found in the environment variables, we check if it exists in Streamlit's secrets. Streamlit provides a secure way to store sensitive information like API keys. If the key is found in st.secrets, we use that value instead. This ensures that the application can access the Groq API securely without hardcoding the key in the source code.
            if not api_key and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
            
            # Create a Groq client instance using the retrieved API key. The Groq client is responsible for communicating with the Groq API, which provides advanced AI capabilities. We then create an instance of LLMCoach, passing in the Groq client. The LLMCoach uses the Groq API to generate intelligent feedback based on the user's exercise performance and form. Finally, we create an instance of TextToSpeech (TTS) to convert the generated text feedback into spoken audio. We store the VoicePipeline instance in Streamlit's session state so that it can be reused throughout the app without reinitializing it.
            groq_client = Groq(api_key=api_key)

            llm_coach = LLMCoach(groq_client)
            tts = TextToSpeech()

            st.session_state.voice_pipeline = VoicePipeline(llm_coach, tts)
        except Exception as e:
            st.session_state.voice_pipeline = None


    # Here this .get("workout_started", False) :-
    # .get() is a dictionary method that tries to fetch the value for the key "workout_started". If the key exists → returns its value.
    # If the key does not exist → returns the default value you provide (False here). This prevents errors like KeyError when the key isn’t initialized yet.
    workout_started = st.session_state.get("workout_started", False)


    # Now we are writing the logic & code for sidebar actually
    with st.sidebar:
        st.title("🏋️‍♂️CoachX : A Real-time AI Gym Coach")

        if st.session_state.username:
            st.caption(f"👤 Login as {st.session_state.username}")

        st.divider()

        st.subheader("Workout Plan")
    
        # Only show workout plan setup if workout has NOT started yet
        if not workout_started:
            # Dropdown menu to select exercise type from EXERCISE_OPTIONS list
            plan_exercise = st.selectbox("Exercise", options=EXERCISE_OPTIONS, key="plan_exercise")

            # Numeric input for number of sets (0–50 allowed)
            plan_sets = st.number_input("Sets", min_value=0, max_value=50, key="plan_sets", step=1)

            # Numeric input for reps per set (0–50 allowed)
            plan_reps = st.number_input("Reps per Set", min_value=0, max_value=50, key="plan_reps", step=1)

            # Blank space for layout spacing
            st.markdown("")

            start_session_button = st.button("Start Workout", width="stretch", key="start_session_button")

            if start_session_button:
                st.session_state.exercise_type = plan_exercise
                st.session_state.target_sets = int(plan_sets)
                st.session_state.reps_per_set = int(plan_reps)
                st.session_state.reps = 0     # Reset total reps to 0 at the start of a new workout
                st.session_state.workout_started = True
                st.session_state.set_cycle_started_at = time.time()     # Record the timestamp when the workout starts (used for timing sets)
                st.session_state.last_saved_sets_completed = 0    # Reset last saved sets completed to 0 at the start of a new workout
                
                # Since we are starting a new workout, we want to notify the user that the workout has started. If the voice_pipeline is initialized, we call its process_event method with the "workout_started" event, passing in the exercise type and an empty metrics dictionary. The result will contain audio feedback and text feedback generated by the LLMCoach and TTS components. If feedback is generated, we store the audio bytes and text feedback in session state so they can be played or displayed in the UI.
                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_started",
                        exercise=plan_exercise,
                        metrics={}
                    )
                    
                    if result:
                        # Store the generated audio and text feedback in session state for playback and display
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result
                
                st.session_state.last_notified_sets_completed = 0    # Reset last notified sets completed to 0 at the start of a new workout
                st.session_state.last_notified_workout_complete = False   # Reset last notified workout complete flag to False at the start of a new workout

                # Force app rerun so UI updates to workout mode
                st.rerun()
        else:
            # Retrieve the workout plan details from session_state
            exercise = st.session_state.get("exercise_type")   # The exercise chosen by the user
            sets = st.session_state.get("target_sets")           # Number of sets planned
            reps = st.session_state.get("reps_per_set")           # Number of reps per set planned

            # Display the current workout plan in an info box
            st.info(f"**{exercise}** -- {sets} Sets x {reps} Reps")

            end_session_button = st.button("End Workout", key="end_session_button", width="stretch")

            if end_session_button:
                save_unsaved_workout_progress()
                st.session_state.workout_started = False

                # So as session is ending, we want to notify the user that the workout has been completed. If the voice_pipeline is initialized, we call its process_event method with the "workout_completed" event, passing in the exercise type and an empty metrics dictionary. The result will contain audio feedback and text feedback generated by the LLMCoach and TTS components. If feedback is generated, we store the audio bytes and text feedback in session state so they can be played or displayed in the UI.
                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_completed",
                        exercise=exercise,
                        metrics={}
                    )

                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result

                st.rerun()    # Force the app to rerun so the UI switches back to workout setup mode



        if workout_started:
            st.divider()

           # Retrieve workout details from session_state
            exercise = st.session_state.get("exercise_type")       # Current exercise selected
            total_reps = st.session_state.get("reps")              # Total reps completed across all sets
            current_set_reps = st.session_state.get("current_set_reps")  # Reps done in the ongoing set
            reps_per_set = st.session_state.get("reps_per_set")       # Planned reps per set
            sets_completed = st.session_state.get("sets_completed")# Number of sets completed so far
            target_sets = st.session_state.get("target_sets")        # Planned total sets

            # Section heading for progress tracking
            st.subheader("Progress")

            # Display key workout metrics in a clean, dashboard-style format
            st.metric("Total Reps", f"{total_reps}")                        # Shows total reps completed
            st.metric("Current Set Reps", f"{current_set_reps} / {reps_per_set}")  # Shows reps done vs target in current set
            st.metric("Sets Completed", f"{sets_completed} / {target_sets}")       # Shows sets completed vs target sets

            st.divider()

            if exercise == "Squats":
                st.subheader("Squat Metrics")
                st.metric("Knee Angle", f"{st.session_state.knee_angle}°")
                st.metric("Back Angle", f"{st.session_state.back_angle}°")
                st.metric("Depth Status", st.session_state.depth_status)

            elif exercise == "Push-ups":
                st.subheader("Push-up Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Body Alignment", st.session_state.body_alignment)
                st.metric("Hip Position", st.session_state.hip_status)

            elif exercise == "Biceps Curls (Dumbbell)":
                st.subheader("Curl Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Shoulder Stability", st.session_state.shoulder_status)
                st.metric("Swing Detection", st.session_state.swing_status)

            elif exercise == "Shoulder Press":
                st.subheader("Shoulder Press Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Arm Extension", st.session_state.extension_status)
                st.metric("Back Arch", st.session_state.back_arch_status)

            elif exercise == "Lunges":
                st.subheader("Lunge Metrics")
                st.metric("Front Knee Angle", f"{st.session_state.front_knee_angle}°")
                st.metric("Torso Angle", f"{st.session_state.torso_angle}°")
                st.metric("Balance Status", st.session_state.balance_status)


    st.title("CoachX : A Real-time AI Gym Coach")
    st.markdown("#### Real-time pose detection with proactive AI voice coaching")


    if st.session_state.get("audio_to_play"):
        autoplay_audio(st.session_state.audio_to_play)


    if st.session_state.get("coach_feedback"):
        st.markdown("")
        st.success(f"🤖 **Coach:** {st.session_state.coach_feedback}")



    if not workout_started:
        st.markdown(
            """
            <div style="
                border: 10px dashed #444;
                border-radius: 0px;
                padding: 48px 32px;
                text-align: center;
                color: #888;
                margin-top: 32px;
                margin-bottom: 32px;
            ">
                <h2 style="color:#ccc; margin-bottom:8px;">👈 Set your workout plan</h2>
                <p style="font-size:1.05rem;">
                    Choose your exercise, sets and reps in the sidebar,<br>
                    then click <strong>Start Workout</strong> to activate the camera and AI coach.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else: 
        context = webrtc_streamer(
            key="exercise-analysis",    # A unique identifier for this WebRTC component inside Streamlit. Prevents conflicts if you have multiple webrtc_streamer instances in the same app.
            mode=WebRtcMode.SENDRECV,

            video_processor_factory=VideoProcessorClass,     # This parameter connects a custom Python class (VideoProcessorClass) that processes video frames. It allows you to run pose detection, exercise form analysis, or ML models on each frame captured from the webcam. Streamlit passes frames from the webcam → your class → processed output → back to the browser.
            rtc_configuration=get_rtc_configuration(),
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing=True
        )

        sync_metrics_update(context)  # This function synchronizes the metrics update between the video processor and the Streamlit session state. It ensures that the latest exercise metrics (like reps, angles, and status) are reflected in the UI in real-time.

        # Here we are checking if the video is playing (context.state.playing). If it is, we introduce a short delay of 0.25 seconds using time.sleep(0.25) to avoid overwhelming the UI with too many updates. After the delay, we call st.rerun() to refresh the Streamlit app, ensuring that the latest metrics are displayed in real-time.
        if context.state.playing:
            time.sleep(0.25)
            st.rerun()

        inject_webrtc_styles()

        # video_processor_factory=VideoProcessorClass :-
        # Connects a custom Python class that processes video frames.
        # Example: VideoProcessorClass could run pose detection, exercise form analysis, or ML models on each frame.
        # Streamlit passes frames from the webcam → your class → processed output → back to browser

        # rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]} :-
        # Configures ICE servers for WebRTC.
        # STUN server (stun:stun.l.google.com:19302) helps peers discover their public IP/port (NAT traversal).
        # Without this, WebRTC peers might fail to connect across different networks.

        # media_stream_constraints={"video": True, "audio": False} :-
        # Tells the browser what media streams to capture:
        # video: True → capture webcam video.
        # audio: False → disable microphone (no audio stream).
        # Useful when you only need video analysis (like exercise posture detection).

        # async_processing=True :- 
        # Enables asynchronous frame processing.
        # Prevents blocking the main Streamlit thread while heavy ML/computer vision tasks run.
        # Ensures smoother UI and real‑time responsiveness.


    st.divider()

    st.markdown("#### Workout History")

    user_id = st.session_state.get("user_id", 0)

    # Here we are checking if the user_id is an integer (which means a valid user is logged in). If it is, we retrieve the user's exercise history from the database using get_users_exercises(user_id). We then format this data into a list of dictionaries, convert it into a Pandas DataFrame, and display it as a table in the Streamlit app. If no history is found, we show an informational message to the user.
    if isinstance(user_id, int):    # Check if user_id is a valid integer (i.e., a logged-in user). If not, we skip fetching history.
        history_rows = get_users_exercises(user_id)

        # Here we are creating a list of dictionaries (df_arr) where each dictionary represents a workout entry. We extract relevant fields from each row of the user's exercise history, such as exercise name, reps, sets, time taken, and the date it was created. This structured format makes it easy to convert into a Pandas DataFrame for display in the Streamlit app.
        df_arr = [
            {
                "Exercise": row['exercise_name'],
                "Reps": row['reps'],
                "Sets": row['sets'],
                "Time (sec)": row['time'],
                "Date": row['created_at']
            }
            for row in history_rows
        ]

        # Here we are converting the list of dictionaries (df_arr) into a Pandas DataFrame (df). This allows us to easily manipulate and display the workout history data in a tabular format within the Streamlit app. If the DataFrame is not empty, we proceed to process and display the data; otherwise, we inform the user that no workout history was found.
        df = pd.DataFrame(df_arr)

        if not df.empty:
            # Here we are converting the "Date" column in the DataFrame (df) to a datetime format using pd.to_datetime(). We then extract only the date part (year-month-day) using .dt.date. This ensures that the date is displayed in a clean format without extra time information, making it easier for users to read their workout history.
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            
            # Now we are grouping the DataFrame (df) by "Exercise" and "Date" using df.groupby(). We then aggregate the grouped data to calculate the total "Reps", "Sets", and "Time (sec)" for each exercise on each date. The result is reset to a new DataFrame (agg_df) with a clean index. Finally, we increment the index by 1 for better readability and display the aggregated workout history as a table in the Streamlit app.
            # For example, if a user did 3 sets of squats on 2024-06-01 and 2 sets on 2024-06-02, this aggregation will show the total reps, sets, and time for each date separately.
            # But if the user did multiple exercises on the same date, each exercise will have its own row in the aggregated table, allowing users to see a clear breakdown of their workout history.
            agg_df = df.groupby(["Exercise", "Date"]).agg({
                "Reps": 'sum',   
                "Sets": "sum",
                "Time (sec)": "sum"
            }).reset_index()
            # Here we are using 'sum' to calculate the total number of reps for each exercise on each date. This means if a user performed multiple sets of the same exercise on the same day, all those reps will be added together to give a cumulative total for that exercise on that date.
            # Here reset_index() is used to convert the grouped DataFrame back into a regular DataFrame with a default integer index. This makes it easier to display the data in a tabular format in the Streamlit app, as we can now access the rows by their integer index rather than a multi-level index created by the groupby operation.

            # Here we are incrementing the index of the aggregated DataFrame (agg_df) by 1. This is done to make the index more user-friendly when displayed in the Streamlit app. Instead of starting from 0 (which is common in programming), the index will start from 1, making it easier for users to read and understand their workout history table.
            agg_df.index += 1

            # Here we are displaying the aggregated workout history DataFrame (agg_df) as a table in the Streamlit app using st.table(). The border="horizontal" argument adds horizontal lines between rows for better readability. This allows users to easily view their past workouts, including the total reps, sets, and time taken for each exercise on each date.
            st.table(agg_df, border="horizontal")
        else:
            st.info("No workout history found.")





# __name__ in Python :-
# Every Python file has a special built-in variable called __name__.
# If the file is being run directly (e.g., python app.py), then __name__ is automatically set to "__main__".
# If the file is being imported into another file (e.g., import app), then __name__ is set to the module’s name ("app" in this case).

# if __name__ == "__main__" :-
# This condition checks whether the file is being run directly.
# If true → execute the code inside the block.
# If false (meaning the file is imported elsewhere) → skip the block.

if __name__ == "__main__":
    main()




#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# To run any streamlit application , we use this :-
# streamlit run your_script.py
# Here we will use this :- streamlit run main.py


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Statefulness :-
# In Streamlit, statefulness refers to how the app remembers values or data across reruns.
# By default, Streamlit apps are stateless: every time a user interacts with a widget (like a button or slider), the script reruns from top to bottom, and variables reset. This makes apps simple but can be frustrating if you want to preserve information between interactions.

# How Streamlit Handles State :-
# Stateless reruns: Each interaction triggers a full rerun of the script.
# Session State: Streamlit provides st.session_state to store values that persist across reruns.
# Widget State: Widgets (like st.text_input, st.slider) automatically save their current value in st.session_state.

# Statefulness lets you build interactive apps that remember user choices, cache results, or maintain progress.


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Difference Between Module and Package :-
# Module :-	A single Python file (.py) that contains functions, classes, or variables.
# Package :- A collection of modules organized in a folder, with an __init__.py file to mark it as a package.

# So we can say that :-
# Module = one file
# Package = folder of modules

# Historically, Python required an __init__.py file inside a folder to treat it as a package.
# Without it, Python would just see the folder as a normal directory, not something importable.

# Since Python 3.3+, implicit namespace packages exist: you don’t strictly need __init__.py for a folder to be importable.
# But most projects still include it for clarity and control.

# In __init__ file :-
# In this, we write Initialization logic i.e Code that should run when the package is imported (e.g., setting up logging, loading configs).
# __init__.py file acts as the reception desk of a building (package). It decides what’s visible and accessible when someone enters.

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Differences Between WebRTC and WebSockets :-
# WebRTC is best for peer‑to‑peer audio, video, and real‑time data transfer, while WebSockets are ideal for client‑server messaging like chat, notifications, and live updates. They’re often used together — WebSockets handle signaling, and WebRTC manages the actual media/data streams.
# WebRTC uses TCP protocol & WebSockets uses UDP protocol.
# UDP is faster because it doesn't guaranted full transfer of data i.e it can drop some frames also of video & due to which it is faster
# But TCP is slower but more secure as it guaranted full transfer of data, so that's why we are using it here as we do not want video frames to droped during transmission


# When to Use Each :-
# Use WebSockets if:
# You need persistent client‑server messaging (e.g., chat, live dashboards, multiplayer game state sync).
# Your data is primarily text or binary frames.
# You want simpler setup and don’t need audio/video.

# Use WebRTC if:
# You need real‑time audio/video streaming (video conferencing, telehealth, live streaming).
# You want peer‑to‑peer data transfer (file sharing, gaming).
# You require built‑in NAT traversal and encryption.

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# What is MediaPipe? :-
# MediaPipe is a cross-platform framework developed by Google for building multimodal (video, audio, and sensor) applied machine learning pipelines. It provides pre-built models and tools for tasks like pose estimation, hand tracking, face detection, and object detection.

# Mediapipe is an open-source, cross-platform framework developed by Google that provides ready-to-use, ML-powered solutions for live, on-device computer vision and audio, such as hand tracking, face landmark detection, and gesture recognition. 
# It simplifies the process of building real-time applications that require understanding of visual and audio data.

# It works with :
# Video
# Images
# Live camera feeds

# Used for :
# Face detection
# Hand tracking
# Pose estimation

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# What is Pose Landmarker Model :-
# Pose Landmarker is a model that detects human body keypoints (landmarks) from an image or video.

# It can :
# Detect body joints
# Track movement
# Understand posture

# It works in images, video, or live stream

# It returns Output as :
# 2D coordinates of keypoints (x, y)  -->  position on screen
# 3D coordinates of keypoints (x, y, z)  --> depth information
# Optional segmentation masks for body parts

# How it works :-
# Step 1: Person Detection → Detects the person in the frame.
# First model detects "is there a human?"

# Step 2: Landmark Detection → Detects keypoints (like elbows, knees, shoulders) on the detected person.
# Second model predicts the exact positions of body joints.


# There are 33 keypoints (Body landmarks) in the Pose Landmarker model, including:
# Examples: Nose, Eyes, Ears, Shoulders, Elbows, Wrists, Hips, Knees, Ankles, etc.


# This Model hasVariants :-
# Lite --> fast, less accurate, for mobile or low-power devices
# Full --> balanced, slower, more accurate, for desktops or high-power devices
# Heavy --> most accurate, slowest, for research or high-end GPUs

# Here we will use this full variant of the model as we want more accuracy in our project

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
