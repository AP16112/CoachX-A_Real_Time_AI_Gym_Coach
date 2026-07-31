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

from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loader import load_css, inject_local_font
from services.persistence.exercise_repository import init_db




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
            st.selectbox("Exercise", options=EXERCISE_OPTIONS, key="plan_exercise")

            # Numeric input for number of sets (0–50 allowed)
            st.number_input("Sets", min_value=0, max_value=50, key="plan_sets", step=1)

            # Numeric input for reps per set (0–50 allowed)
            st.number_input("Reps per Set", min_value=0, max_value=50, key="plan_reps", step=1)

            # Blank space for layout spacing
            st.markdown("")

            start_session_button = st.button("Start Session", width="stretch", key="start_session_button")

            if start_session_button:
                st.session_state["workout_started"] = True
                # Force app rerun so UI updates to workout mode
                st.rerun()
        else:
            # Retrieve the workout plan details from session_state
            exercise = st.session_state.get("plan_exercise")   # The exercise chosen by the user
            sets = st.session_state.get("plan_sets")           # Number of sets planned
            reps = st.session_state.get("plan_reps")           # Number of reps per set planned

            # Display the current workout plan in an info box
            st.info(f"**{exercise}** -- {sets} Sets x {reps} Reps")

            end_session_button = st.button("End Session", key="end_session_button", width="stretch")

            if end_session_button:
                st.session_state["workout_started"] = False
                st.rerun()    # Force the app to rerun so the UI switches back to workout setup mode



        if workout_started:
            st.divider()

           # Retrieve workout details from session_state
            exercise = st.session_state.get("plan_exercise")       # Current exercise selected
            total_reps = st.session_state.get("reps")              # Total reps completed across all sets
            current_set_reps = st.session_state.get("current_set_reps")  # Reps done in the ongoing set
            reps_per_set = st.session_state.get("plan_reps")       # Planned reps per set
            sets_completed = st.session_state.get("sets_completed")# Number of sets completed so far
            target_sets = st.session_state.get("plan_sets")        # Planned total sets

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
# To run any streamlit application , we use this :-
# streamlit run your_script.py
# Here we will use this :- streamlit run main.py


