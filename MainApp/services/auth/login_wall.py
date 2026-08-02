# Here in this file, we will write the logic and code for login functionality UI for this app.
# Login Form UI :-

import streamlit as st
from services.persistence.exercise_repository import get_or_create_user


# The function ensures that : If a user is already logged in (user_id exists in session state), they skip the login form. If not, the app shows a registration/login form to capture a username.
def render_login_wall():
    # Here we are Checking if user is already logged in or not
    if st.session_state.get("user_id") is not None:
        return True     # as if user_id is not none, then it means that user exists, then no need to show any new registeration form or page to user now, so we will return from here only
    

    # If user doesn't exists, then we need to register this user
    st.title("🏋️‍♂️CoachX : A Real-time AI Gym Coach")
    st.markdown("### Welcome! Please enter a username to start.")    # here ### means we are using h3 tag actually


    # Here this "login_form" is the unique identifier (form key) for the form.
    # Streamlit requires a key so it can track the state of this form separately from other widgets.
    # If you had multiple forms in your app, each would need a different key (e.g., "signup_form", "feedback_form").
    # clear_on_submit=False :- This parameter controls what happens to the form fields after submission:
    # True → Clears all input fields once the form is submitted.
    # False → Keeps the entered values in the fields after submission.
    # In our case, False means the username stays visible after the user clicks "Start Session," which is helpful for login because we don’t want the field to reset immediately.
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Name (unique)", placeholder="unique name e.g. arpit16112")
        submit_button = st.form_submit_button("Start Session", width="stretch")

 
    if submit_button:
        if not username:
            st.error("Name cannot be empty.")
            return False
        
        # So if user doesn't exists, then we will either create that user or if it's exists then we will get that user
        user = get_or_create_user(username)
        
        st.session_state["username"] = user["username"]
        st.session_state["user_id"] = user["id"]

        st.rerun()


    # If login hasn’t happened yet, return False (meaning user is not authenticated).
    return False





