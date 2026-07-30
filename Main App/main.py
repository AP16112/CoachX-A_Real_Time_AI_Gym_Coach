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

import streamlit as st

from services.auth.login_wall import render_login_wall



def main():
    st.set_page_config(
        page_title="CoachX : A Real-time AI Gym Coach",     # page_title sets the browser tab title
        page_icon="🏋️‍♀️",        # small icon visible before this page_title
        initial_sidebar_state="expanded",
        layout="centered"
    )


    if not render_login_wall():
        return

    st.write("Hello!")



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


