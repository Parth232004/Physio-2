# realtime_feedback.py
# Generates real-time corrective text feedback per frame based on movement validation
# Now includes phase-aware feedback (raise/hold/lower) for temporal intelligence

from physio_exercises import (
    EXERCISES,
    get_shoulder_abduction_angle,
    get_elbow_flexion_angle,
    get_shoulder_rotation_angle
)

# Phase thresholds for different exercises
PHASE_THRESHOLDS = {
    "arm_raise": {
        "raise_complete": 120,  # Angle considered "raised"
        "lower_complete": 30,   # Angle considered "lowered"
    },
    "elbow_flexion": {
        "raise_complete": 120,  # Angle considered "flexed"
        "lower_complete": 30,   # Angle considered "extended"
    },
    "shoulder_rotation": {
        "raise_complete": 60,   # Rotation considered "rotated"
        "lower_complete": 10,   # Rotation considered "neutral"
    }
}

class PhaseDetector:
    """
    Detects the current phase of an exercise movement.
    Phases: RAISE, HOLD, LOWER, NEUTRAL
    """
    
    def __init__(self, exercise_name):
        self.exercise_name = exercise_name
        self.thresholds = PHASE_THRESHOLDS.get(exercise_name, {})
        self.current_phase = "NEUTRAL"
        self.phase_start_frame = 0
        self.hold_frames = 0
        self.last_angle = 0
        
    def detect_phase(self, angle_value, frame_count):
        """
        Detect the current phase based on angle value.
        
        :param angle_value: Current angle value
        :param frame_count: Current frame number
        :return: Current phase string
        """
        if not self.thresholds:
            return "NEUTRAL"
        
        raise_complete = self.thresholds.get("raise_complete", 120)
        lower_complete = self.thresholds.get("lower_complete", 30)
        
        prev_phase = self.current_phase
        
        # Phase detection logic
        if angle_value >= raise_complete:
            if prev_phase not in ["RAISE", "HOLD"]:
                self.current_phase = "RAISE"
                self.phase_start_frame = frame_count
                self.hold_frames = 0
            else:
                self.current_phase = "HOLD"
                self.hold_frames += 1
        elif angle_value <= lower_complete:
            self.current_phase = "LOWER"
            self.phase_start_frame = frame_count
            self.hold_frames = 0
        elif angle_value > lower_complete and angle_value < raise_complete:
            if prev_phase == "LOWER":
                self.current_phase = "RAISE"
                self.phase_start_frame = frame_count
            elif prev_phase in ["RAISE", "HOLD"]:
                self.current_phase = "HOLD"
                self.hold_frames += 1
        
        return self.current_phase
    
    def get_phase_info(self):
        """Get current phase information."""
        return {
            "phase": self.current_phase,
            "hold_frames": self.hold_frames,
            "phase_duration": self.hold_frames  # Frames in current phase
        }


def get_angle_feedback(angle_name, angle_value, min_angle, max_angle):
    """
    Generate feedback for a specific angle based on deviation from safe range.

    :param angle_name: Name of the angle
    :param angle_value: Current angle value
    :param min_angle: Minimum safe angle
    :param max_angle: Maximum safe angle
    :return: Feedback string or None if safe
    """
    if min_angle <= angle_value <= max_angle:
        return None

    deviation = 0
    direction = ""
    if angle_value < min_angle:
        deviation = min_angle - angle_value
        if "shoulder_abduction" in angle_name:
            direction = "Raise arm higher"
        elif "elbow_flexion" in angle_name:
            direction = "Bend elbow more"
        elif "shoulder_internal_rotation" in angle_name:
            direction = "Rotate shoulder internally more"
        elif "shoulder_external_rotation" in angle_name:
            direction = "Rotate shoulder externally more"
    else:
        deviation = angle_value - max_angle
        if "shoulder_abduction" in angle_name:
            direction = "Lower arm"
        elif "elbow_flexion" in angle_name:
            direction = "Straighten elbow"
        elif "shoulder_internal_rotation" in angle_name:
            direction = "Reduce internal rotation"
        elif "shoulder_external_rotation" in angle_name:
            direction = "Reduce external rotation"

    # Severity based on deviation
    if deviation > 30:
        severity = "significantly"
    elif deviation > 15:
        severity = ""
    else:
        severity = "slightly"

    feedback = f"{severity} {direction}".strip()
    return feedback


def get_phase_feedback(exercise_name, phase_info, angle_value):
    """
    Generate phase-specific feedback.
    
    :param exercise_name: Name of the exercise
    :param phase_info: Dict with phase information
    :param angle_value: Current angle value
    :return: Feedback string or None
    """
    phase = phase_info.get("phase", "NEUTRAL")
    hold_frames = phase_info.get("hold_frames", 0)
    
    if exercise_name == "arm_raise":
        if phase == "RAISE" and hold_frames < 5:
            return "Continue raising arm"
        elif phase == "HOLD" and hold_frames < 30:
            return f"Hold position ({hold_frames} frames)"
        elif phase == "HOLD" and hold_frames >= 30:
            return "Good hold! Begin lowering"
        elif phase == "LOWER" and angle_value > 50:
            return "Continue lowering slowly"
        elif phase == "LOWER" and angle_value <= 50:
            return "Return to neutral"
            
    elif exercise_name == "elbow_flexion":
        if phase == "RAISE" and hold_frames < 5:
            return "Continue bending elbow"
        elif phase == "HOLD" and hold_frames < 30:
            return f"Hold bend ({hold_frames} frames)"
        elif phase == "HOLD" and hold_frames >= 30:
            return "Good hold! Begin straightening"
        elif phase == "LOWER" and angle_value > 50:
            return "Continue straightening"
            
    elif exercise_name == "shoulder_rotation":
        if phase == "RAISE" and hold_frames < 5:
            return "Continue rotating"
        elif phase == "HOLD" and hold_frames < 30:
            return f"Hold rotation ({hold_frames} frames)"
        elif phase == "HOLD" and hold_frames >= 30:
            return "Good hold! Return to neutral"
    
    return None


def generate_feedback(exercise_name, landmarks, phase_info=None):
    """
    Generate real-time feedback for the selected exercise based on current landmarks.
    Now includes phase-aware feedback.

    :param exercise_name: Name of the exercise
    :param landmarks: MediaPipe pose landmarks
    :param phase_info: Optional phase information for phase-aware feedback
    :return: List of feedback strings
    """
    exercise = EXERCISES.get(exercise_name.lower())
    if not exercise:
        return ["Invalid exercise"]

    feedbacks = []
    angle_ranges = exercise.angle_ranges

    # Get primary angle for phase detection
    primary_angle = None
    if "shoulder_abduction" in angle_ranges:
        primary_angle = get_shoulder_abduction_angle(landmarks)
    elif "elbow_flexion" in angle_ranges:
        primary_angle = get_elbow_flexion_angle(landmarks)

    # Generate angle-based feedback
    if "shoulder_abduction" in angle_ranges:
        angle = get_shoulder_abduction_angle(landmarks)
        feedback = get_angle_feedback("shoulder_abduction", angle, *angle_ranges["shoulder_abduction"])
        if feedback:
            feedbacks.append(feedback)

    if "elbow_flexion" in angle_ranges:
        angle = get_elbow_flexion_angle(landmarks)
        feedback = get_angle_feedback("elbow_flexion", angle, *angle_ranges["elbow_flexion"])
        if feedback:
            feedbacks.append(feedback)

    if "shoulder_internal_rotation" in angle_ranges or "shoulder_external_rotation" in angle_ranges:
        rotation_angles = get_shoulder_rotation_angle(landmarks)
        if "shoulder_internal_rotation" in angle_ranges:
            feedback = get_angle_feedback("shoulder_internal_rotation", rotation_angles["internal"], *angle_ranges["shoulder_internal_rotation"])
            if feedback:
                feedbacks.append(feedback)
        if "shoulder_external_rotation" in angle_ranges:
            feedback = get_angle_feedback("shoulder_external_rotation", rotation_angles["external"], *angle_ranges["shoulder_external_rotation"])
            if feedback:
                feedbacks.append(feedback)

    # Generate phase-aware feedback if phase info provided
    if phase_info and primary_angle is not None:
        phase_feedback = get_phase_feedback(exercise_name, phase_info, primary_angle)
        if phase_feedback:
            feedbacks.insert(0, f"[{phase_info.get('phase', 'NEUTRAL')}] {phase_feedback}")

    if not feedbacks:
        feedbacks.append("Good form")

    return feedbacks


if __name__ == "__main__":
    # Demo
    print("Real-time feedback module ready with phase awareness.")
    print("Phases: RAISE, HOLD, LOWER, NEUTRAL")
    # In real use, call generate_feedback with exercise_name and landmarks
