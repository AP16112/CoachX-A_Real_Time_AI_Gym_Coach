# In this file, we will write the logic for the voice pipeline that integrates the LLM (Language Model) and TTS (Text-to-Speech) components to provide real-time feedback during workouts. The VoicePipeline class will handle events, analyze exercise metrics, and generate spoken feedback based on the user's performance.


import time
import streamlit as st


# SO this is actually the Voice processor class.
# It takes in an LLM instance and a TTS instance during initialization. The LLM is responsible for generating feedback based on workout events and detected issues, while the TTS converts that feedback into spoken audio. The class also manages timing to avoid overlapping or excessive feedback.
class VoicePipeline:
    def __init__(self, llm, tts):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0   # This variable keeps track of the last time feedback was spoken, allowing the system to enforce a cooldown period between feedback events to prevent overwhelming the user with too much information at once.


    # This private method analyzes the exercise metrics to determine if there are any form issues that need to be addressed. It checks specific metrics for each exercise type and returns a descriptive issue string if a problem is detected, or None if everything is fine. This allows the system to provide targeted feedback based on the user's performance.
    def _find_form_issue(self, exercise, metrics):
        if "issue" in metrics:   # If the metrics dictionary contains a key named "issue", it indicates that a form issue has already been identified by the video processor or another component. In this case, we can directly return the value associated with that key, which is expected to be a descriptive string explaining the detected issue. This allows us to quickly provide feedback without needing to analyze individual metrics for each exercise type.
            return metrics["issue"]

        # If no pre-identified issue is present, we analyze the metrics based on the specific exercise type to detect common form problems. Each exercise has its own set of relevant metrics that can indicate issues with form or technique.
        if exercise == "Squats":
            depth = metrics.get("depth_status", "")
            back_angle = metrics.get("back_angle", 180)
            
            if depth == "TOO HIGH":
                return "The user's squat is not deep enough — knees are not bending sufficiently."

            if isinstance(back_angle, (int, float)) and back_angle < 130:
                return "The user is leaning too far forward during the squat."

        elif exercise == "Push-ups":
            alignment = metrics.get("body_alignment", "")
            hip_status = metrics.get("hip_status", "")
            
            if alignment == "Poor Form":
                return "The user's body is not straight during the push-up."

            if hip_status == "SAGGING":
                return "The user's hips are sagging down during the push-up."

            if hip_status == "PIKED UP":
                return "The user's hips are too high — lower them to form a straight line."

        elif exercise == "Biceps Curls (Dumbbell)":
            swing = metrics.get("swing_status", "")
            shoulder = metrics.get("shoulder_status", "")
            
            if swing == "SWINGING":
                return "The user is swinging their torso during the curl — keep the body still."

            if shoulder == "ELBOW DRIFTING":
                return "The user's elbow is drifting away from their side during the curl."

        elif exercise == "Shoulder Press":
            back_arch = metrics.get("back_arch_status", "")
            extension = metrics.get("extension_status", "")
            
            if back_arch == "Excessive Arch":
                return "The user is arching their lower back excessively during the press."

            if back_arch == "Slight Arch":
                return "Slight back arch detected — encourage the user to brace their core."

        elif exercise == "Lunges":
            balance = metrics.get("balance_status", "")
            
            if balance == "OFF BALANCE":
                return "The user is losing balance during the lunge — feet should be hip-width apart."

        # If no specific form issues are detected based on the exercise metrics, we return None to indicate that the user's form appears to be acceptable. This allows the system to provide positive reinforcement or continue monitoring without unnecessary feedback.
        return None


    # This method processes workout events and generates spoken feedback based on the exercise type and detected metrics. It first checks for any form issues using the _find_form_issue method. If a major event occurs (like starting or completing a workout), it will always provide feedback. For minor issues, it enforces a cooldown period of 5 seconds to avoid overwhelming the user with too much feedback. If feedback is generated, it uses the LLM to create a text response and then converts that text into speech using the TTS component. The method returns both the audio bytes and the text feedback for further use, such as playing the audio or displaying the text in the UI.
    def process_event(self, event, exercise, metrics):
        issue = self._find_form_issue(exercise, metrics)   # This line calls the _find_form_issue method to analyze the current exercise metrics and determine if there are any form issues that need to be addressed. The result is stored in the variable issue, which will be used later to generate feedback for the user.

        now = time.time()  # This line retrieves the current time in seconds since the epoch (January 1, 1970) and stores it in the variable now. This timestamp is used to enforce a cooldown period between feedback events, ensuring that the user is not overwhelmed with too much feedback in a short amount of time.

        # We define a boolean variable is_major_issue to determine if the current event is considered a major event that warrants immediate feedback. Major events include starting a workout, completing a set, or finishing a workout. If the event is one of these, we will provide feedback regardless of any cooldown restrictions.
        is_major_issue = event in ["workout_started", "set_completed", "workout_completed"]

        if not is_major_issue:
            if not issue:
                return None
            
            # If the event is not a major issue and there is a detected form issue, we check if enough time has passed since the last feedback was spoken. We enforce a cooldown period of 5 seconds to prevent overwhelming the user with too much feedback in a short time. If less than 5 seconds have passed since the last feedback, we return None to skip generating new feedback.
            if now - self.last_spoken_at < 5:
                return None
            
        # If we reach this point, it means either a major event has occurred or a form issue has been detected and the cooldown period has passed. We proceed to generate feedback using the LLM and convert it to speech using the TTS component. The generated text feedback is stored in the variable text, and the corresponding audio bytes are stored in voice. We also update the last_spoken_at timestamp to the current time to enforce the cooldown for future feedback events.
        # Here we call the give_feedback method of the LLM instance, passing in the current
        text = self.llm.give_feedback(event, issue)
        voice = self.tts.speak(text)

        self.last_spoken_at = now

        # Finally, we return both the generated audio bytes (voice) and the text feedback (text) to the caller. This allows the application to play the audio feedback for the user while also displaying the text feedback in the UI or logging it for further analysis.
        return voice, text
    


# This function takes audio bytes as input and plays them in the Streamlit app. It first checks if the audio bytes are valid (not None or empty). If valid, it hides the default audio player using custom CSS and then uses Streamlit's st.audio function to play the audio automatically. This allows for seamless auditory feedback in the application without displaying the standard audio controls.
def autoplay_audio(audio_bytes):
    if not audio_bytes:
        return
    
    # We use Streamlit's st.markdown function to inject custom CSS that hides the default audio player. The CSS targets the data-testid attribute of the audio player and sets its display property to none, effectively removing it from the UI. This allows us to play audio feedback without showing the standard audio controls, providing a cleaner user experience.
    st.markdown("<style>[data-testid='stAudio'] {display: none;}</style>", unsafe_allow_html=True)
    
    # Finally, we use Streamlit's st.audio function to play the provided audio bytes. We specify the format as "audio/mp3" and set autoplay to True, which means the audio will start playing automatically when this function is called. This provides immediate auditory feedback to the user based on the generated speech from the TTS component.
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)