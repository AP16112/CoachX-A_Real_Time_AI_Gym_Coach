# Here in this file, we will define the VideoProcessorClass which is responsible for processing video frames in real-time, detecting poses, and analyzing exercise performance. 
# This class integrates with MediaPipe's PoseLandmarker model to extract pose landmarks and uses specific exercise detectors to evaluate form and count repetitions.

# So we will write the actual logic for processing video frames, detecting poses, and analyzing exercise performance in real-time. The VideoProcessorClass will handle the integration with MediaPipe's PoseLandmarker model and use specific exercise detectors to evaluate form and count repetitions.


# Provides tools for building reliable file paths.
from pathlib import Path

# cv2 (OpenCV) :-
# Popular computer vision library. Used for image/video processing: reading frames, drawing landmarks, applying filters, etc.
# Example: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) converts an image to grayscale.
import cv2

# PyAV library (Python bindings for FFmpeg). Handles audio/video streams in real time.
# In streamlit-webrtc, it’s used to wrap video frames (av.VideoFrame) so they can be processed and returned.
import av

import numpy as np

# Google’s ML framework for real-time perception. Provides ready-to-use models for pose detection, face detection, hand tracking, etc.
# In our exercise detectors, mp.solutions.pose is used to get body landmarks (shoulders, elbows, knees, etc.).
import mediapipe as mp

# Python’s built-in library for multithreading. Allows running tasks in parallel (e.g., video processing + UI updates).
# Useful in real-time apps where you don’t want the main thread blocked.
import threading


# streamlit-webrtc: An extension for Streamlit that lets you work with real‑time video/audio streams directly in your web app using WebRTC (Web Real‑Time Communication).
# VideoProcessorBase: A base class provided by the library. You inherit from it to define custom video processing logic (e.g., applying filters, pose detection, exercise tracking).
from streamlit_webrtc import VideoProcessorBase
# recv(self, frame): The primary method we override to grab incoming video frames as av.VideoFrame, convert or modify them (often via OpenCV or NumPy), and return a processed av.VideoFrame.


# mediapipe.tasks → The newer MediaPipe Tasks framework, designed for higher‑level ML tasks (vision, audio, text).
# python → The Python bindings for these tasks.
# vision → A submodule under python that contains vision‑related tasks (image classification, object detection, pose detection, etc.).
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Here we are importing the specific exercise detectors that we have implemented for different exercises. Each detector contains the logic to analyze the user's form, count repetitions, and provide feedback based on the pose landmarks detected by MediaPipe.
from detectors.squat import SquatDetector
from detectors.pushup import PushUpDetector
from detectors.biceps_curl import BicepsCurlDetector
from detectors.shoulder_press import ShoulderPressDetector
from detectors.lunges import LungesDetector


from services.config.workout_config import POSE_CONNECTIONS



class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        # Here we are using _lock to ensure that when multiple threads are accessing or modifying shared data (like latest metrics or exercise type), they do so in a thread-safe manner. This prevents race conditions and ensures data integrity.
        # _latest_metrics will store the most recent analysis results (like reps, angles, form feedback) from the exercise detectors. It is updated after processing each video frame.
        # _exercise_type keeps track of the currently selected exercise (e.g., "Squats", "Push-ups"). This allows the processor to know which detector to use for analyzing the incoming video frames.
        # Here _ means that these attributes are intended for internal use within the class and should not be accessed directly from outside. It’s a naming convention in Python to indicate “private” variables.
        # Create a threading lock object. This ensures thread‑safe access when multiple threads. Might read/write shared data (like metrics) at the same time.
        self._lock = threading.Lock()    # Here we are creating a threading lock object to ensure that when multiple threads are accessing or modifying shared data (like latest metrics or exercise type), they do so in a thread-safe manner. This prevents race conditions and ensures data integrity.
        self._latest_metrics = None      # Store the latest exercise metrics (e.g., reps, angles, posture feedback). Initially set to None until the first frame is processed.
        self._exercise_type = "Squats"    # Default exercise type being tracked. Can be changed later depending on user selection (e.g., PushUps, Lunges).

        # Load the MediaPipe PoseLandmarker model for real-time pose detection.
        # Build the full path to the pose landmark model file from the MainApp directory.
        # Streamlit Cloud may start the app from the repository root, so the current
        # working directory is not reliable for locating bundled model files.
        app_dir = Path(__file__).resolve().parents[2]
        # Here we are constructing the full path to the MediaPipe pose_landmarker_full.task model file. We start from the current file's directory (__file__), resolve it to an absolute path, and then navigate up two levels (parents[2]) to reach the MainApp directory. From there, we append "ml_models/pose_landmarker_full.task" to get the complete path to the model file. This ensures that we can reliably locate the model file regardless of where the app is run from, which is important for deployment in environments like Streamlit Cloud.
        # The pose_landmarker_full.task file is a pre-trained MediaPipe model that can detect

        model_path = app_dir / "ml_models" / "pose_landmarker_full.task"
        
        # Create a BaseOptions object for MediaPipe Tasks
        # This tells MediaPipe where to find the model asset (the .task file)
        # BaseOptions is the standard way to configure model loading in the new Tasks API
        base_option = python.BaseOptions(model_asset_path=str(model_path))
        # So now this base_option object contains the path to the pose_landmarker_full.task model file, which will be used to initialize the PoseLandmarker for real-time pose detection in video frames.


        # Here we are creating a PoseLandmarkerOptions object to configure the behavior of the pose detection model. We specify that we want to run in VIDEO mode (for real-time video processing) and set minimum confidence thresholds for detection, presence, and tracking of poses. We also disable segmentation masks since we only need pose landmarks for exercise analysis.
        options = vision.PoseLandmarkerOptions(
            # Pass in the model configuration (path to .task file)
            base_options=base_option,   # It tells MediaPipe which model to load.

            # Set the running mode to VIDEO
            # Options are: IMAGE (single image), VIDEO (sequential frames), LIVE_STREAM (real-time webcam)
            # VIDEO mode uses temporal information between frames for smoother tracking
            running_mode=vision.RunningMode.VIDEO,

            # Minimum confidence threshold for detecting a pose. If detection confidence < 0.7, the pose won’t be considered valid
            min_pose_detection_confidence=0.7,

            # Minimum confidence threshold for confirming that a person is present. Helps filter out false positives when no person is detected
            min_pose_presence_confidence=0.7,  

            # Minimum confidence threshold for tracking landmarks across frames. Ensures stable tracking so landmarks don’t “jump” around
            min_tracking_confidence=0.7,

            # Whether to output segmentation masks (person vs background)
            # Disabled here since we only need pose landmarks for exercise detection
            output_segmentation_masks=False
        )
        # So now this options object contains all the configuration needed to initialize the PoseLandmarker for real-time video processing, including model path, running mode, and confidence thresholds.

        # Create the PoseLandmarker instance using the configured options
        # This loads the MediaPipe model and prepares it for video frame processing
        self._landmarker = vision.PoseLandmarker.create_from_options(options)
        # So now self._landmarker is an instance of the PoseLandmarker class, ready to process video frames and extract pose landmarks for exercise analysis.

        # Initialize a dictionary of exercise detectors. Each key is the exercise name, and the value is the corresponding detector class
        # These detectors handle rep counting and form feedback for different exercises
        self._detectors = {
            "Squats": SquatDetector(),
            "Push-ups": PushUpDetector(),
            "Biceps Curls (Dumbbell)": BicepsCurlDetector(),
            "Shoulder Press": ShoulderPressDetector(),
            "Lunges": LungesDetector(),
        }

        # Initialize frame timestamp counter. This keeps track of the current frame’s timestamp in milliseconds
        # Required by MediaPipe when running in VIDEO mode to maintain temporal consistency
        self._frame_timestamps_ms = 0


    
    def set_latest_metrics(self, metrics):
        # Acquire the threading lock before modifying shared state
        # This ensures thread‑safe access so that multiple threads (e.g., video processing + UI rendering) don’t overwrite data at the same time
        with self._lock:
            # Store a copy of the latest metrics dictionary
            # Using .copy() prevents accidental modification of the original object and ensures this class keeps its own safe snapshot of the metrics
            self._latest_metrics = metrics.copy()
    


    def get_latest_metrics(self):
        # Acquire the threading lock before reading shared state
        # This ensures thread‑safe access so that multiple threads (e.g., video processing + UI rendering) don’t read/write at the same time
        with self._lock:
            # If no metrics have been set yet, return None
            # Otherwise, return a copy of the latest metrics dictionary
            # Using .copy() ensures the caller gets a safe snapshot and cannot accidentally modify the internal state
            return None if self._latest_metrics is None else self._latest_metrics.copy()
        

    def set_exercise(self, exercise_type):
        with self._lock:
            # Update the current exercise type being tracked
            # Example: "Squats", "Push-ups", "Lunges"
            self._exercise_type = exercise_type


    def get_exercise(self):
        with self._lock:
            return self._exercise_type
        

    # THis method is called for each incoming video frame. It processes the frame, detects pose landmarks, analyzes the exercise, and returns a modified frame with overlays.
    # It means that this method is called for every video frame received from the webcam or video stream. It processes the frame, detects pose landmarks, analyzes the exercise, and returns a modified frame with overlays (like skeleton lines, rep count, and feedback).
    def _draw_skeleton(self, img, landmarks):
        # Get image dimensions (height and width)
        # Here we are extracting the height (h) and width (w) of the input image (img) using img.shape[:2]. This is important because the pose landmarks provided by MediaPipe are normalized coordinates (values between 0 and 1). To draw lines and circles on the actual image, we need to convert these normalized coordinates to pixel coordinates by multiplying them with the image width and height.
        h, w = img.shape[:2]

        # Draw skeleton connections (lines between key landmarks)
        for start_idx, end_idx in POSE_CONNECTIONS:
            p1 = landmarks[start_idx]
            p2 = landmarks[end_idx]
            # So there is a connection between two landmarks (e.g., left shoulder to left elbow). We only draw the line if both landmarks are visible enough (visibility > 0.7). This prevents drawing lines for occluded or poorly detected joints, which could clutter the overlay and give misleading feedback.

            # Only draw if both landmarks are visible enough (confidence > 0.7)
            if p1.visibility > 0.7 and p2.visibility > 0.7:
                # Here we are using cv2.line to draw a line between two landmarks (p1 and p2) on the image (img). The coordinates are converted from normalized values to pixel values by multiplying by the image width (w) and height (h). The line is drawn in green color (0, 255, 0) with a thickness of 8 pixels. This visually represents the skeleton of the detected pose on the video frame.
                cv2.line(
                    img,
                    (int(p1.x * w), int(p1.y * h)),    # here we are converting the normalized coordinates of the first landmark (p1) to pixel coordinates by multiplying its x and y values by the image width (w) and height (h), respectively. This gives us the actual pixel position of the landmark on the image.
                    (int(p2.x * w), int(p2.y * h)),
                    (0, 255, 0),
                    8
                )
        

        # Draw landmark points (circles at each joint)
        for lm in landmarks:
            if lm.visibility > 0.7:
                # here we are using cv2.circle to draw a filled circle at each visible landmark (joint) on the image (img). The coordinates are converted from normalized values to pixel values by multiplying by the image width (w) and height (h). The circle is drawn in blue color (255, 0, 0) with a radius of 8 pixels. This visually marks the key points of the detected pose on the video frame.
                cv2.circle(
                    img, 
                    (int(lm.x * w), int(lm.y * h)),
                    8,
                    (255, 0, 0),
                    -1    # The -1 thickness means the circle is filled in, rather than just an outline.
                )
            

    # Here we are defining a method called _draw_no_pose_warnings that takes an image (img) as input and overlays warning text on the image when no pose is detected. This provides feedback to the user, prompting them to face the camera so that the pose detection can work properly. The method uses OpenCV's cv2.putText function to draw two lines of text on the image: "NO POSE DETECTED" and "PLEASE FACE THE CAMERA". The text is drawn in green color with a specific font, size, and thickness for visibility.
    # The purpose of this method is to give visual feedback to the user in real-time,
    def _draw_no_pose_warnings(self, img):
        # Display a warning message when no pose landmarks are detected
        # First line: "NO POSE DETECTED"
        cv2.putText(
            img,
            "NO POSE DETECTED",          # Text to display
            (30, 50),                    # Position (x=30, y=50) in pixels
            cv2.FONT_HERSHEY_SIMPLEX,    # Font style
            1,                           # Font scale (size)
            (0, 255, 0),                 # Text color (green in BGR)
            2,                           # Thickness of the text
            cv2.LINE_AA,                 # Anti-aliased line for smoother text
        )

        # Second line: "PLEASE FACE THE CAMERA"
        cv2.putText(
            img,
            "PLEASE FACE THE CAMERA",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )


    # here we are defining a method called _draw_overlays that takes an image (img), exercise metrics (metrics), and the exercise type (ex_type) as input. This method is responsible for overlaying exercise-specific feedback on the video frame based on the detected exercise type. It checks the exercise type and calls the corresponding overlay drawing method for squats, push-ups, biceps curls, shoulder presses, or lunges. Each of these methods will handle the specific feedback and visual cues relevant to that exercise, such as rep count, angles, and form feedback.
    def _draw_overlays(self, img, metrics, ex_type):
        if ex_type == "Squats":
            self._draw_squats_overlays(img, metrics)
        elif ex_type == "Push-ups":
            self._draw_pushup_overlays(img, metrics)
        elif ex_type == "Biceps Curls (Dumbbell)":
            self._draw_curl_overlays(img, metrics)
        elif ex_type == "Shoulder Press":
            self._draw_press_overlays(img, metrics)
        elif ex_type == "Lunges":
            self._draw_lunge_overlays(img, metrics)



    def _draw_squats_overlays(self, img, metrics):
        # Get image height (h) and ignore width (_)
        # Used to position text near the bottom of the frame
        h, _ = img.shape[:2]

    
        # Overlay squat depth status on the video frame
        # Example: "DEPTH: GOOD" or "DEPTH: TOO SHALLOW"
        cv2.putText(
            img,
            f"DEPTH: {metrics['depth_status']}",  # Text showing squat depth feedback
            (20, h - 20),                         # Position: 20px from left, 20px above bottom
            cv2.FONT_HERSHEY_SIMPLEX,             # Font style
            1,                                    # Font size scale
            (0, 255, 0),                          # Text color (green in BGR)
            2,                                    # Thickness of the text
        )


    def _draw_pushup_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"BODY: {metrics['body_alignment']} | HIP: {metrics['hip_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )


    def _draw_curl_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"SWING: {metrics['swing_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )


    def _draw_press_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"EXT: {metrics['extension_status']} | BACK: {metrics['back_arch_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )


    def _draw_lunge_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"BALANCE: {metrics['balance_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )



    # recv(self, frame): The primary method we override to grab incoming video frames as av.VideoFrame, convert or modify them (often via OpenCV or NumPy), and return a processed av.VideoFrame.
    # We will actually get the video frames in this method only.
    # It is actually a method of the VideoProcessorBase class that we are overriding in our VideoProcessorClass. This method is called for each incoming video frame, allowing us to process the frame, detect pose landmarks, analyze the exercise, and return a modified frame with overlays.
    def recv(self, frame):
        # Convert the incoming video frame (av.VideoFrame) to a NumPy array
        # Flip the frame horizontally (mirror effect) so it looks natural like a webcam
        # Format "bgr24" → standard OpenCV color format (Blue, Green, Red channels)
        image = np.asarray(
            # Here we are converting the incoming video frame (frame) from the av.VideoFrame format to a NumPy array that OpenCV can work with. We first convert the frame to a BGR24 format (standard color format for OpenCV), then flip it horizontally using cv2.flip to create a mirror effect, which is more natural for users when they see themselves on screen. Finally, we wrap it in np.asarray to ensure it’s a proper NumPy array of type uint8, which is the expected format for image processing in OpenCV.
            # Here this 1 in cv2.flip(frame.to_ndarray(format="bgr24"), 1) indicates that we want to flip the image around the y-axis (horizontal flip). This creates a mirror effect, which is often preferred in webcam applications because it feels more natural to users when they see themselves on screen.
            cv2.flip(frame.to_ndarray(format="bgr24"), 1),
            dtype=np.uint8    # Ensures the image data is in the correct format for OpenCV processing (unsigned 8-bit integers for pixel values).
        )

        # Wrap the NumPy image into a MediaPipe Image object
        # MediaPipe expects SRGB format, so we specify that
        # Convert the color space from RGB to BGR for consistency with OpenCV
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,   # MediaPipe expects images in the SRGB color space for accurate color representation.
            # Here we are converting the color space of the image from RGB to BGR using cv2.cvtColor. This is necessary because OpenCV uses BGR format by default, while MediaPipe expects images in RGB format. By converting the color space, we ensure that the colors are interpreted correctly when passed to the MediaPipe PoseLandmarker for pose detection.
            data=cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        )

        # Increment the frame timestamp by 30 milliseconds for each frame processed. This simulates a frame rate of ~33 FPS (1000 ms / 30 ms ≈ 33.3 FPS). MediaPipe uses this timestamp to maintain temporal consistency when running in VIDEO mode.
        self._frame_timestamps_ms += 30
        # So here we are incrementing the frame timestamp by 30 milliseconds for each frame processed. This simulates a frame rate of approximately 33 frames per second (FPS), as 1000 milliseconds divided by 30 milliseconds equals about 33.3 FPS. MediaPipe uses this timestamp to maintain temporal consistency when running in VIDEO mode, allowing it to track poses across frames more accurately.

        # Detect pose landmarks in the current video frame using the MediaPipe PoseLandmarker
        # The detect_for_video method processes the frame and returns pose landmarks if a person is detected
        result = self._landmarker.detect_for_video(mp_image, self._frame_timestamps_ms)

        if result.pose_landmarks:
            # If pose landmarks are detected, extract the first set of landmarks (for the primary person in the frame)
            # Here we are extracting the first set of pose landmarks from the result returned by MediaPipe. The result.pose_landmarks is a list of detected poses, and we take the first one (result.pose_landmarks[0]) to analyze the primary person in the frame. These landmarks contain the 3D coordinates (x, y, z) and visibility scores for key body joints, which will be used for exercise analysis and feedback.
            landmarks = result.pose_landmarks[0]

            # Draw the detected skeleton on the video frame using the extracted landmarks
            self._draw_skeleton(image, landmarks)

            # Get the current exercise type being tracked (e.g., "Squats", "Push-ups")
            ex_type = self.get_exercise()

            # Retrieve the corresponding exercise detector based on the current exercise type
            # Each detector contains logic to analyze the user's form, count repetitions, and provide feedback based on the detected pose landmarks.
            # Here we are retrieving the appropriate exercise detector from the _detectors dictionary based on the
            detector = self._detectors.get(ex_type)

            if detector:
                # Process the detected landmarks using the selected exercise detector
                # The process method analyzes the landmarks and returns metrics such as rep count, angles, and form feedback specific to the exercise being performed. These metrics will be used to provide real-time feedback to the user.
                metrics = detector.process(landmarks)

                metrics["pose_detected"] = True

                # Draw exercise-specific overlays on the video frame based on the detected metrics and exercise type
                self._draw_overlays(image, metrics, ex_type)

                self.set_latest_metrics(metrics)
        else:
            # If no pose landmarks are detected, draw a warning message on the video frame
            self._draw_no_pose_warnings(image)
            
            with self._lock:
                # If no pose is detected, we update the latest metrics to indicate that no pose was detected. This allows the UI or other components to know that the user is not in view or not performing the exercise correctly.
                if self._latest_metrics is not None:   # Check if latest metrics exist before updating 
                    self._latest_metrics["pose_detected"] = False
                else:   # If latest metrics are None, initialize it with pose_detected set to False
                    self._latest_metrics = {"pose_detected": False}


        # Convert the processed NumPy image back to an av.VideoFrame and return it
        # This allows the modified frame (with skeleton, overlays, and warnings) to be sent
        return av.VideoFrame.from_ndarray(image, format="bgr24")
    
