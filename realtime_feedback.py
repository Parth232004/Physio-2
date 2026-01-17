# realtime_feedback.py
# Generates real-time corrective text feedback per frame based on movement validation

from physio_exercises import (
    EXERCISES,
    get_shoulder_abduction_angle,
    get_elbow_flexion_angle,
    get_shoulder_rotation_angle
)

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

def generate_feedback(exercise_name, landmarks):
    """
    Generate real-time feedback for the selected exercise based on current landmarks.

    :param exercise_name: Name of the exercise
    :param landmarks: MediaPipe pose landmarks
    :return: List of feedback strings
    """
    exercise = EXERCISES.get(exercise_name.lower())
    if not exercise:
        return ["Invalid exercise"]

    feedbacks = []
    angle_ranges = exercise.angle_ranges

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

    # Additional feedbacks like "Slow down" or "Hold position" would require tracking over frames
    # For now, only angle-based feedback

    if not feedbacks:
        feedbacks.append("Good form")

    return feedbacks

if __name__ == "__main__":
    # Demo
    print("Real-time feedback module ready.")
    # In real use, call generate_feedback with exercise_name and landmarks