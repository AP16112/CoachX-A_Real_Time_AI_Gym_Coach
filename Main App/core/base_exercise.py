# Here in this file, we will define a base class for exercises. This class will provide common functionality and structure that all specific exercise classes (like Squats, Push-ups, etc.) can inherit from. It will handle the calculation of angles between joints, counting repetitions, and managing the stage of the exercise (e.g., "up" or "down" position).
# So This class is actually an abstract base class (ABC) that defines the interface and shared behavior for all exercise types. It cannot be instantiated directly, but other exercise classes will extend it and implement the abstract methods.


import math 

# abc stands for Abstract Base Classes. It’s a Python module that provides the infrastructure for defining abstract classes.
# Abstract classes are templates for other classes — they define methods that must be implemented by subclasses, but don’t provide full implementations themselves.
from abc import ABC, abstractmethod
# ABC is a helper base class provided by the abc module. When you inherit from ABC, your class becomes an abstract base class.
# Abstract base classes cannot be instantiated directly — they’re meant to be subclassed.

# abstractmethod is a decorator used inside an abstract base class. It marks a method as abstract, meaning subclasses must override/implement it.
# If a subclass doesn’t implement all abstract methods, Python will raise an error when you try to instantiate it.



# This defines a class called BaseExercise. It inherits from ABC (Abstract Base Class) from the abc module.
#That means BaseExercise is an abstract class — it’s meant to serve as a template for other exercise classes (like PushUp, Squat, etc.). You cannot instantiate BaseExercise directly if it contains abstract methods (though right now it doesn’t yet).
class BaseExercise(ABC):
    def __init__(self):
        self.reps = 0
        self.stage = None    #  Tracks the current stage/phase of the exercise (e.g., “up” vs “down” in a push‑up, or “standing” vs “squatting”).



    # Here this method calculates the angle formed by three points (a, b, c) in 2D space. It’s commonly used in pose estimation to determine joint angles (like elbow or knee angles) based on landmark coordinates.
    # a, b, c are tuples representing 2D coordinates (x, y)
    def calculate_angle(self, a, b, c):
        # Step 1: Create vectors BA and BC
        ax, ay = a[0] - b[0], a[1] - b[1]   # Vector from point B to point A
        cx, cy = c[0] - b[0], c[1] - b[1]   # Vector from point B to point C

        # Step 2: Compute dot product of BA and BC
        dot = ax * cx + ay * cy

        # Step 3: Compute magnitudes of vectors BA and BC
        mag_a = math.sqrt(ax ** 2 + ay ** 2)
        mag_c = math.sqrt(cx ** 2 + cy ** 2)

        # Step 4: Handle edge case (zero-length vector)
        if mag_a * mag_c == 0:
            return 0.0

        # Step 5: Compute cosine of the angle using dot product formula
        # Here we are also clamping the value of cos_angle to be between -1 and 1 to avoid any potential math domain errors when taking the arccosine.
        # cosθ = (A · C) / (|A| * |C|)
        cos_angle = max(-1.0, min(1.0, dot / (mag_a * mag_c)))

        # Step 6: Convert from radians to degrees
        return math.degrees(math.acos(cos_angle))



    # This method retrieves the (x, y) coordinates of a specific landmark from a list of landmarks. Landmarks are typically provided by pose estimation models (like MediaPipe) and represent key points on the human body (e.g., shoulders, elbows, knees).
    # landmarks is a list of landmark objects, each having x and y attributes (normalized coordinates between 0 and 1)
    # idx is the index of the specific landmark you want to retrieve (e.g., 11 for left shoulder, 12 for right shoulder, etc.)
    def get_point(self, landmarks, idx):
        p = landmarks[idx]

        # here we are returning tuple of x and y coordinates of the landmark at index idx.
        return (p.x, p.y)



    # The process method is an abstract method that must be implemented by any subclass of BaseExercise. It defines the interface for processing pose landmarks to analyze the exercise. Each specific exercise class (like Squat, PushUp, etc.) will provide its own implementation of this method to handle the unique logic for counting reps, determining stages, and evaluating form based on the landmarks.
    # landmarks is a list of pose landmarks detected in the current video frame. Each landmark contains normalized x, y coordinates (and sometimes z) representing key points on the body.
    @abstractmethod
    def process(self, landmarks):
        pass


    @abstractmethod
    def reset(self):
        pass




# Logic used for calculate angles function :-
# here we will use Vector dot product formula to calculate the angle between two vectors. The angle between two vectors can be calculated using the dot product formula:
# cosθ = (A · B) / (|A| * |B|)  where:
# A · B is the dot product of vectors A and B.  
# |A| and |B| are the magnitudes (lengths) of vectors A and B.
# θ is the angle between the two vectors in radians. To convert it to degrees, we use: degrees = radians * (180 / π).

# e.g Hip (A) = (0.5, 0.5), Knee (B) = (0.5, 0.7), Ankle (C) = (0.5, 0.9)

# Step 1: Create vectors BA and BC
# Vector BA = A - B = (0.5 - 0.5, 0.5 - 0.7) = (0, -0.2)
# Here ax = 0, ay = -0.2
# Vector BC = C - B = (0.5 - 0.5, 0.9 - 0.7) = (0, 0.2)
# Here cx = 0, cy = 0.2

# Dot product of BA and BC:
# BA · BC = (0 * 0) + (-0.2 * 0.2) = 0 - 0.04 = -0.04

# Magnitudes of BA and BC:
# |BA| = sqrt(0^2 + (-0.2)^2) = sqrt(0 + 0.04) = 0.2
# |BC| = sqrt(0^2 + (0.2)^2) =  sqrt(0 + 0.04) = 0.2

# Cosine of the angle:
# cosθ = (BA · BC) / (|BA| * |BC|)  
# cosθ = -0.04 / (0.2 * 0.2) = -0.04 / 0.04 = -1

# Clamp :- so now we will clamp the value of cosθ to be between -1 and 1. In this case, cosθ = -1, which is already within the range.
# cos_angle = max(-1.0, min(1.0, -1)) = -1

# Find Angle using acos function:
# acos is used to find the angle in radians from the cosine value. So θ = acos(cosθ) = acos(-1) = π radians.
# θ = acos(cosθ) = acos(-1) = π radians 
# Now convert radians to degrees:
# degrees = π * (180 / π) = 180 degrees





# Here this landmarks list is a predefined set of 33 key points representing the human body in a normalized coordinate system. Each landmark has an id, name, x, y, z coordinates, and visibility score. These landmarks are typically used in pose estimation models (like MediaPipe) to track body movements and analyze exercises. The list includes points for the face, upper body, hands, lower body, and feet.
# So we will get this landmarks list from mediapipe pose model and then we will use this landmarks list to calculate the angles between different joints and then we will use these angles to count the reps of the exercise.
# e.g 
# landmarks = [
#     # 0–10: Face
#     {"id": 0, "name": "NOSE", "x": 0.50, "y": 0.10, "z": -0.10, "visibility": 0.99},
#     {"id": 1, "name": "LEFT_EYE_INNER", "x": 0.48, "y": 0.09, "z": -0.10, "visibility": 0.98},
#     {"id": 2, "name": "LEFT_EYE", "x": 0.47, "y": 0.09, "z": -0.10, "visibility": 0.98},
#     {"id": 3, "name": "LEFT_EYE_OUTER", "x": 0.46, "y": 0.09, "z": -0.10, "visibility": 0.98},
#     {"id": 4, "name": "RIGHT_EYE_INNER", "x": 0.52, "y": 0.09, "z": -0.10, "visibility": 0.98},
#     {"id": 5, "name": "RIGHT_EYE", "x": 0.53, "y": 0.09, "z": -0.10, "visibility": 0.98},
#     {"id": 6, "name": "RIGHT_EYE_OUTER", "x": 0.54, "y": 0.09, "z": -0.10, "visibility": 0.98},
#     {"id": 7, "name": "LEFT_EAR", "x": 0.44, "y": 0.10, "z": -0.05, "visibility": 0.97},
#     {"id": 8, "name": "RIGHT_EAR", "x": 0.56, "y": 0.10, "z": -0.05, "visibility": 0.97},
#     {"id": 9, "name": "MOUTH_LEFT", "x": 0.48, "y": 0.12, "z": -0.05, "visibility": 0.96},
#     {"id": 10, "name": "MOUTH_RIGHT", "x": 0.52, "y": 0.12, "z": -0.05, "visibility": 0.96},

#     # 11–16: Upper body
#     {"id": 11, "name": "LEFT_SHOULDER", "x": 0.40, "y": 0.25, "z": -0.20, "visibility": 0.99},
#     {"id": 12, "name": "RIGHT_SHOULDER", "x": 0.60, "y": 0.25, "z": -0.20, "visibility": 0.99},
#     {"id": 13, "name": "LEFT_ELBOW", "x": 0.35, "y": 0.40, "z": -0.15, "visibility": 0.98},
#     {"id": 14, "name": "RIGHT_ELBOW", "x": 0.65, "y": 0.40, "z": -0.15, "visibility": 0.98},
#     {"id": 15, "name": "LEFT_WRIST", "x": 0.30, "y": 0.55, "z": -0.10, "visibility": 0.97},
#     {"id": 16, "name": "RIGHT_WRIST", "x": 0.70, "y": 0.55, "z": -0.10, "visibility": 0.97},

#     # 17–22: Hands
#     {"id": 17, "name": "LEFT_PINKY", "x": 0.28, "y": 0.58, "z": -0.10, "visibility": 0.95},
#     {"id": 18, "name": "RIGHT_PINKY", "x": 0.72, "y": 0.58, "z": -0.10, "visibility": 0.95},
#     {"id": 19, "name": "LEFT_INDEX", "x": 0.29, "y": 0.57, "z": -0.10, "visibility": 0.95},
#     {"id": 20, "name": "RIGHT_INDEX", "x": 0.71, "y": 0.57, "z": -0.10, "visibility": 0.95},
#     {"id": 21, "name": "LEFT_THUMB", "x": 0.31, "y": 0.56, "z": -0.10, "visibility": 0.95},
#     {"id": 22, "name": "RIGHT_THUMB", "x": 0.69, "y": 0.56, "z": -0.10, "visibility": 0.95},

#     # 23–28: Lower body (MOST IMPORTANT for squats)
#     {"id": 23, "name": "LEFT_HIP", "x": 0.45, "y": 0.55, "z": -0.30, "visibility": 0.99},
#     {"id": 24, "name": "RIGHT_HIP", "x": 0.55, "y": 0.55, "z": -0.30, "visibility": 0.99},
#     {"id": 25, "name": "LEFT_KNEE", "x": 0.46, "y": 0.70, "z": -0.25, "visibility": 0.98},
#     {"id": 26, "name": "RIGHT_KNEE", "x": 0.54, "y": 0.70, "z": -0.25, "visibility": 0.98},
#     {"id": 27, "name": "LEFT_ANKLE", "x": 0.47, "y": 0.90, "z": -0.20, "visibility": 0.97},
#     {"id": 28, "name": "RIGHT_ANKLE", "x": 0.53, "y": 0.90, "z": -0.20, "visibility": 0.97},

#     # 29–32: Feet
#     {"id": 29, "name": "LEFT_HEEL", "x": 0.46, "y": 0.95, "z": -0.20, "visibility": 0.96},
#     {"id": 30, "name": "RIGHT_HEEL", "x": 0.54, "y": 0.95, "z": -0.20, "visibility": 0.96},
#     {"id": 31, "name": "LEFT_FOOT_INDEX", "x": 0.48, "y": 0.98, "z": -0.15, "visibility": 0.95},
#     {"id": 32, "name": "RIGHT_FOOT_INDEX", "x": 0.52, "y": 0.98, "z": -0.15, "visibility": 0.95},
# ]
