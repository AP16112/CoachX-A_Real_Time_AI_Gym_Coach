# CoachX : A Real-time AI Gym Coach

![Platform](https://img.shields.io/badge/Platform-Web-blue)
![Frontend](https://img.shields.io/badge/Frontend-Streamlit-red)
![AI](https://img.shields.io/badge/AI-MediaPipe%20%2B%20Groq-purple)
![Language](https://img.shields.io/badge/Language-Python%203.11-yellow)
![Storage](https://img.shields.io/badge/Storage-SQLite-green)
![Status](https://img.shields.io/badge/Status-Live-success)

CoachX is a real-time AI fitness coaching system that turns a webcam into an intelligent personal trainer. The app captures the user’s live pose through the browser, converts the stream into structured body landmarks using a computer vision model, analyzes the movement pattern for the selected exercise, and then gives instant verbal feedback to improve form or encourage completion. Instead of only showing static metrics, the system pushes the experience into a continuous coaching loop where pose detection, exercise logic, and AI-generated voice guidance work together in real time.

At a high level, the project combines:

- a Streamlit interface for user interaction and dashboard-style workout tracking
- WebRTC for low-latency webcam streaming between the browser and Python backend
- MediaPipe PoseLandmarker for real-time human pose detection
- exercise-specific detector logic for counting repetitions and identifying form issues
- a Groq-powered LLM to generate short coaching instructions
- Google Text-to-Speech to speak those instructions back to the user
- SQLite to persist user sessions and workout history

---

## 🚀 Live Demo

- CoachX WebApp: https://coachx-landing-page.netlify.app

---

## Overview

CoachX provides an end-to-end workout coaching workflow:

- choose an exercise from the sidebar
- define the sets and reps plan
- start a live session with webcam tracking
- detect pose landmarks in real time using MediaPipe
- analyze form and rep flow with exercise-specific detectors
- receive live spoken coaching through an LLM + TTS pipeline
- persist completed workout history in SQLite

This makes the project useful for:

- AI and computer vision portfolio work
- real-time exercise monitoring demos
- fitness-tech prototypes
- Streamlit + WebRTC experiments
- voice-assisted interactive coaching experiences

## Why This Project

Traditional gym coaching is expensive, hard to scale, and often inconsistent. Many users want instant, on-demand feedback while exercising, especially when they are training alone.

CoachX addresses this by combining:

- pose estimation for body keypoints
- real-time exercise detectors for rep and form analysis
- AI-powered coaching prompts for corrective feedback
- voice playback for immediate audio guidance

This creates a practical demo of how AI can support training quality and motivation in real time.

## Problem Statement

People training solo often struggle with:

- bad posture during workouts
- incorrect rep pacing
- lack of immediate corrective feedback
- no structured workout progress tracking

CoachX solves this by creating a browser-based coaching assistant that monitors the user’s movement, gives real-time corrections, and keeps their workout logs.

## What The Project Does

The application supports:

- username-based workout session login
- exercise plan setup for sets and reps
- live webcam pose analysis
- rep counting and form metric extraction
- exercise-specific coaching for:
  - Squats
  - Push-ups
  - Biceps Curls (Dumbbell)
  - Shoulder Press
  - Lunges
- LLM-generated corrective voice feedback
- workout history tracking and aggregation per user
- a separate marketing-style landing page for product presentation

### What WebRTC Is and How It Works in This Project

WebRTC stands for Web Real-Time Communication. It is a browser-based protocol and API stack used for transmitting audio, video, and data in real time with very low latency. In this project, WebRTC is used to connect the user’s webcam to the Streamlit frontend and then pass the video frames into the Python backend for computer vision analysis.

In practice, the flow looks like this:

1. The browser captures the webcam stream.
2. `streamlit-webrtc` creates a peer-to-peer connection using WebRTC.
3. The live frames are forwarded into the `VideoProcessorClass` Python object.
4. The model processes each frame, extracts pose landmarks, and calculates exercise metrics.
5. The processed output is sent back to the Streamlit UI for live visualization.

This matters because the app needs frame-by-frame analysis rather than a delayed or upload-based workflow. WebRTC gives the system the fast path required for real-time inference.

### Machine Learning Model Used

The main ML model in this project is the MediaPipe `PoseLandmarker` model from the `pose_landmarker_full.task` asset in [MainApp/ml_models/pose_landmarker_full.task](MainApp/ml_models/pose_landmarker_full.task).

This model is used for:

- detecting whether a person is present in the frame
- extracting 33 body landmarks such as shoulders, elbows, wrists, hips, knees, and ankles
- estimating body pose across video frames with temporal stability
- providing the keypoint coordinates used by the exercise detectors

The model works in `VIDEO` mode, which is ideal for a live camera workflow. In the code, the model is initialized with confidence thresholds and a `PoseLandmarkerOptions` configuration. Each incoming frame is converted into a MediaPipe-compatible image object and passed into `detect_for_video()`, which returns landmark predictions for the current frame.

The key idea is that the model does not directly tell the app whether the exercise is correct. Instead, it provides the geometry of the pose. That geometry is then interpreted by custom detector logic for each exercise.

### How the ML Model Is Used Here

Once the landmark coordinates are available, the project performs a second layer of logic:

- the selected exercise detector receives the pose landmarks
- it computes metrics such as knee angle, elbow angle, body alignment, depth, balance, and rep state
- the detector returns a metric dictionary containing values like `depth_status`, `hip_status`, `swing_status`, and `reps`
- those metrics are fed into the voice coaching pipeline for real-time guidance

So the pipeline is:

`webcam → WebRTC stream → MediaPipe PoseLandmarker → exercise-specific detectors → metrics → LLM + TTS feedback`

This is why the app is not just a camera feed; it is a real-time inference and coaching system.


## Key Features

- Streamlit-based interactive interface
- Browser webcam access through WebRTC
- MediaPipe pose landmark detection
- Real-time exercise-specific metrics and pose overlays
- AI voice coaching using Groq LLM + Google TTS
- Workout history persistence in SQLite
- User session handling for personalized workout progress
- Responsive product landing page in HTML/CSS

## Demo

### Home / Product Landing Page



### Main App Experience

The main app offers:

- side-panel workout planning
- live pose detection view
- real-time metrics such as reps, sets, and posture status
- AI coach feedback shown in the UI and spoken aloud
- per-user history table for past sessions

## Tech Stack

- Python
- Streamlit
- Streamlit WebRTC
- MediaPipe
- OpenCV
- NumPy
- Pandas
- SQLite
- Groq API
- gTTS
- Python-dotenv
- HTML/CSS

## Project Structure

```text
CoachX/
|-- README.md
|-- packages.txt
|-- LandingPage/
|   |-- index.html
|   |-- style.css
|-- MainApp/
|   |-- main.py
|   |-- requirements.txt
|   |-- .env
|   |-- data.db
|   |-- ml_models/
|   |   |-- pose_landmarker_full.task
|   |-- core/
|   |-- detectors/
|   |-- services/
|   |   |-- auth/
|   |   |-- coaching/
|   |   |-- config/
|   |   |-- persistence/
|   |   |-- state/
|   |   |-- tracking/
|   |   |-- vision/
```

## Important Files

| File / Folder | Purpose |
|---|---|
| [MainApp/main.py](MainApp/main.py) | Main Streamlit entry point and app orchestration |
| [MainApp/services/vision/exercise_video_processor.py](MainApp/services/vision/exercise_video_processor.py) | Real-time video frame processing, pose detection, and overlay drawing |
| [MainApp/services/coaching/voice_pipeline.py](MainApp/services/coaching/voice_pipeline.py) | AI coaching logic that turns metrics into spoken feedback |
| [MainApp/services/coaching/llm.py](MainApp/services/coaching/llm.py) | Groq-based LLM response generation for workout cues |
| [MainApp/services/coaching/tts.py](MainApp/services/coaching/tts.py) | Google Text-to-Speech audio generation |
| [MainApp/services/persistence/exercise_repository.py](MainApp/services/persistence/exercise_repository.py) | SQLite persistence for user sessions and exercise history |
| [MainApp/services/config/workout_config.py](MainApp/services/config/workout_config.py) | Exercise list, metrics schema, and prompt configuration |
| [MainApp/ml_models/pose_landmarker_full.task](MainApp/ml_models/pose_landmarker_full.task) | MediaPipe pose landmark model asset |
| [LandingPage/index.html](LandingPage/index.html) | Landing page markup and call-to-action content |
| [LandingPage/style.css](LandingPage/style.css) | Landing page styling |
| [MainApp/requirements.txt](MainApp/requirements.txt) | Python dependency list for the app |
| [packages.txt](packages.txt) | OS-level deployment packages for OpenCV-related runtime support |

## How It Works

1. A user enters a unique username and starts a session.
2. The user selects an exercise, sets, and reps from the sidebar.
3. The Streamlit app opens a webcam feed through WebRTC.
4. The browser webcam stream is sent into the `VideoProcessorClass` using `streamlit-webrtc`.
5. Each frame is converted into a format compatible with MediaPipe and processed by the pose landmark model.
6. The corresponding detector analyzes alignment, angles, pose depth, and repetition count from the landmark coordinates.
7. The latest metrics are synced into Streamlit session state so the UI can display real-time progress.
8. The voice pipeline checks for important workout events such as `workout_started`, `set_completed`, `workout_completed`, and `no_pose_detected`.
9. The LLM generates short coaching text and the text-to-speech layer speaks it back to the user.
10. Workout progress is persisted in SQLite and shown in the history table for the logged-in user.

### How the Database Is Used Here

The database layer is implemented through SQLite and is centered in [MainApp/services/persistence/exercise_repository.py](MainApp/services/persistence/exercise_repository.py).

It is used for three main purposes:

- storing users in a `users` table with a unique username
- storing workout activity in an `exercises` table with fields such as `user_id`, `exercise_name`, `reps`, `sets`, and `time`
- grouping and retrieving workout history so the user can review past sessions in the Streamlit dashboard

The runtime flow is simple:

1. `init_db()` creates the required tables if they do not already exist.
2. `get_or_create_user()` registers or retrieves the current user.
3. `add_exercise()` stores each completed workout segment, automatically updating the same-day record if it already exists.
4. `get_users_exercises()` reads the stored history and formats it into a table in the app.

So the database is not the core ML component; it is the persistence layer that keeps the coaching experience personal and trackable across sessions.

## Exercise Detection Pipeline

The live analysis uses a per-exercise detector architecture:

- Squat detector checks depth, knee angle, and back alignment
- Push-up detector checks body alignment and hip position
- Biceps curl detector checks swing and shoulder drift
- Shoulder press detector checks extension and back arch
- Lunge detector checks front knee angle, torso angle, and balance

These detectors feed real-time metrics into the coaching layer that decides whether the user needs a motivational or corrective cue.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/CoachX.git
cd CoachX
```

### 2. Create a Virtual Environment

On Windows:

```bash
py -3.11 -m venv venv
venv\Scripts\activate
```

On Linux or macOS:

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

From the `MainApp` folder:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in `MainApp/` with your Groq and TURN credentials:

```env
GROQ_API_KEY=your_groq_api_key
TURN_URLS=your_turn_urls
TURN_USERNAME=your_turn_username
TURN_CREDENTIAL=your_turn_credential
```

For Streamlit deployment, you may also store sensitive values in `.streamlit/secrets.toml` instead of a raw `.env` file.

### 5. Run the App

```bash
cd MainApp
streamlit run main.py
```

### 6. Run the Landing Page

Open the HTML landing page directly in a browser, or serve it from a lightweight static server if needed.

## Deployment Notes

- The main app is designed for Streamlit deployment.
- The landing page is a static HTML/CSS experience.
- `packages.txt` contains required OS packages such as OpenCV runtime libraries for deployment environments.
- A local `.env` file is used for development credentials and is intentionally excluded from version control via `.gitignore`.

## Strengths

- Real-time pose analysis using MediaPipe
- Strong product-demo workflow with both app and landing page
- Voice coaching adds a unique AI training layer
- Workout progress is preserved in a lightweight local database
- Modular service structure makes it easy to extend

## Limitations

- Real-world accuracy depends on camera quality, lighting, and user framing
- Voice feedback depends on external API availability
- The project is better suited for demos and prototypes than large-scale production use
- Exercise detection is calibrated around the selected supported movement set

## Future Improvements

- add more exercise detectors and advanced pose scoring
- improve workout analytics and charts
- support stronger user authentication and profiles
- add rest timers and exercise plan templates
- improve audio feedback UX and cooldown management
- add automated tests and CI for app reliability
- package the landing page and main app into a more unified deployment flow

## Learning Outcomes

This project demonstrates:

- building a real-time computer vision fitness assistant
- integrating OpenCV and MediaPipe in a browser-based app
- using Streamlit for interactive AI dashboards
- connecting voice coaching with LLM-generated prompts
- persisting workout data through SQLite
- designing a polished product landing experience alongside the main app
