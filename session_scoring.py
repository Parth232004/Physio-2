# session_scoring.py
# Tracks per-exercise session scores based on consistency and completion quality
# Now includes runtime safety violation escalation with clear alerts

import statistics
from datetime import datetime

class SafetyViolation:
    """Represents a safety violation during a session."""
    
    def __init__(self, angle_name, angle_value, min_safe, max_safe, severity, frame_count):
        self.timestamp = datetime.now()
        self.angle_name = angle_name
        self.angle_value = angle_value
        self.min_safe = min_safe
        self.max_safe = max_safe
        self.severity = severity  # "low", "medium", "high", "critical"
        self.frame_count = frame_count
        self.escalated = False
        self.escalation_level = 0
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.angle_name}: {self.angle_value:.1f}° (safe: {self.min_safe}-{self.max_safe}°)"
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "angle_name": self.angle_name,
            "angle_value": round(self.angle_value, 2),
            "min_safe": self.min_safe,
            "max_safe": self.max_safe,
            "severity": self.severity,
            "frame_count": self.frame_count,
            "escalated": self.escalated,
            "escalation_level": self.escalation_level
        }


class SessionScorer:
    """
    Tracks session scores and provides runtime safety escalation.
    """
    
    def __init__(self, exercise_name, safety_escalation_thresholds=None):
        """
        Initialize scorer for a specific exercise.

        :param exercise_name: Name of the exercise
        :param safety_escalation_thresholds: Dict defining when to escalate warnings
        """
        self.exercise_name = exercise_name
        self.frames = []  # List of dicts with angle data and validation
        self.safety_violations = []  # List of SafetyViolation objects
        self.violation_counts = {}  # Track violations per angle
        self.current_warning_level = 0  # 0=none, 1=caution, 2=warning, 3=critical
        self.frame_count = 0
        
        # Default escalation thresholds (consecutive frames before escalation)
        self.escalation_thresholds = safety_escalation_thresholds or {
            "low": 10,      # 10 frames of minor deviation
            "medium": 5,    # 5 frames of moderate deviation
            "high": 3,      # 3 frames of significant deviation
            "critical": 1   # Immediate escalation
        }
        
        # Initialize violation tracking
        self.violation_tracking = {
            "low": {},
            "medium": {},
            "high": {},
            "critical": {}
        }
    
    def add_frame(self, angles, validations, angle_ranges):
        """
        Add a frame's data and check for safety violations.

        :param angles: Dict of angle names to values
        :param validations: Dict of angle names to bool (safe or not)
        :param angle_ranges: Dict of angle names to (min, max) safe ranges
        """
        self.frame_count += 1
        frame_data = {
            "frame": self.frame_count,
            "angles": angles.copy(),
            "validations": validations.copy(),
            "timestamp": datetime.now()
        }
        self.frames.append(frame_data)
        
        # Check for safety violations
        self._check_safety_violations(angles, validations, angle_ranges)
    
    def _check_safety_violations(self, angles, validations, angle_ranges):
        """
        Check for safety violations and escalate if needed.
        
        :param angles: Current angle values
        :param validations: Dict of angle names to bool (safe or not)
        :param angle_ranges: Dict of angle names to (min, max) safe ranges
        """
        for angle_name, is_safe in validations.items():
            if angle_name not in angle_ranges:
                continue
                
            if not is_safe:
                angle_value = angles.get(angle_name, 0)
                min_safe, max_safe = angle_ranges[angle_name]
                deviation = min(abs(angle_value - min_safe), abs(angle_value - max_safe))
                
                # Determine severity
                if deviation > 30:
                    severity = "high"
                elif deviation > 15:
                    severity = "medium"
                else:
                    severity = "low"
                
                # Track consecutive violations
                if angle_name not in self.violation_tracking[severity]:
                    self.violation_tracking[severity][angle_name] = 0
                self.violation_tracking[severity][angle_name] += 1
                
                # Reset lower severity counters
                for sev in ["medium", "low"]:
                    if angle_name in self.violation_tracking[sev]:
                        self.violation_tracking[sev][angle_name] = 0
                
                # Check if we need to escalate
                threshold = self.escalation_thresholds.get(severity, 5)
                if self.violation_tracking[severity][angle_name] >= threshold:
                    self._escalate_violation(angle_name, angle_value, min_safe, max_safe, severity)
    
    def _escalate_violation(self, angle_name, angle_value, min_safe, max_safe, severity):
        """
        Create and escalate a safety violation.
        
        :param angle_name: Name of the angle
        :param angle_value: Current angle value
        :param min_safe: Minimum safe angle
        :param max_safe: Maximum safe angle
        :param severity: Severity level
        """
        violation = SafetyViolation(angle_name, angle_value, min_safe, max_safe, severity, self.frame_count)
        
        # Escalate based on severity
        if severity == "critical":
            self.current_warning_level = 4
            violation.escalation_level = 4
        elif severity == "high":
            violation.escalation_level = max(violation.escalation_level, 3)
            self.current_warning_level = max(self.current_warning_level, 3)
        elif severity == "medium":
            violation.escalation_level = max(violation.escalation_level, 2)
            self.current_warning_level = max(self.current_warning_level, 2)
        elif severity == "low":
            violation.escalation_level = max(violation.escalation_level, 1)
            self.current_warning_level = max(self.current_warning_level, 1)
        
        violation.escalated = True
        self.safety_violations.append(violation)
        
        # Track total violations per angle
        if angle_name not in self.violation_counts:
            self.violation_counts[angle_name] = 0
        self.violation_counts[angle_name] += 1
    
    def get_safety_status(self):
        """
        Get current safety status for runtime display.
        
        :return: Dict with safety information
        """
        status = {
            "warning_level": self.current_warning_level,
            "warning_text": self._get_warning_text(),
            "recent_violations": [],
            "is_safe": self.current_warning_level < 2
        }
        
        # Get recent violations (last 5)
        recent = [v.to_dict() for v in self.safety_violations[-5:]]
        status["recent_violations"] = recent
        
        return status
    
    def _get_warning_text(self):
        """Get warning text based on current warning level."""
        level = self.current_warning_level
        if level == 0:
            return "SAFE"
        elif level == 1:
            return "CAUTION: Minor deviation detected"
        elif level == 2:
            return "WARNING: Moderate deviation - adjust position"
        elif level == 3:
            return "HIGH WARNING: Significant deviation - slow down"
        elif level == 4:
            return "CRITICAL: Stop exercise immediately"
        return "UNKNOWN"
    
    def get_violation_summary(self):
        """
        Get a summary of all safety violations.
        
        :return: Dict with violation statistics
        """
        summary = {
            "total_violations": len(self.safety_violations),
            "by_severity": {
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0
            },
            "by_angle": dict(self.violation_counts),
            "highest_warning_level": self.current_warning_level,
            "escalation_events": sum(1 for v in self.safety_violations if v.escalated)
        }
        
        for violation in self.safety_violations:
            summary["by_severity"][violation.severity] += 1
        
        return summary
    
    def calculate_score(self):
        """
        Calculate the session score based on consistency and completion quality.

        :return: Score from 0-100
        """
        if not self.frames:
            return 0

        total_frames = len(self.frames)
        safe_frames = sum(1 for frame in self.frames if all(frame["validations"].values()))

        # Completion quality: percentage of frames with all angles safe
        completion_quality = (safe_frames / total_frames) * 100

        # Safety penalty: reduce score based on violations
        violation_penalty = min(30, len(self.safety_violations) * 2)

        # Consistency: average deviation from safe ranges
        angle_names = list(self.frames[0]["angles"].keys())
        consistencies = {}
        for angle_name in angle_names:
            values = [frame["angles"][angle_name] for frame in self.frames]
            if len(values) > 1:
                variance = statistics.variance(values)
                # Lower variance = higher consistency
                consistency = max(0, 100 - variance)  # Arbitrary scaling
            else:
                consistency = 100
            consistencies[angle_name] = consistency

        average_consistency = statistics.mean(consistencies.values()) if consistencies else 100

        # Overall score: weighted average with safety penalty
        score = (completion_quality * 0.5) + (average_consistency * 0.3) + (100 - violation_penalty) * 0.2

        return round(max(0, min(100, score)), 2)

    def get_summary(self):
        """
        Get a summary of the session.

        :return: Dict with score and stats
        """
        score = self.calculate_score()
        total_frames = len(self.frames)
        safe_frames = sum(1 for frame in self.frames if all(frame["validations"].values()))

        return {
            "exercise": self.exercise_name,
            "total_frames": total_frames,
            "safe_frames": safe_frames,
            "score": score,
            "safety": self.get_violation_summary()
        }


# Example usage
if __name__ == "__main__":
    scorer = SessionScorer("arm_raise")
    # Simulate adding frames with violations
    # In real use, integrate with video processing
    print("Session scoring module ready with safety escalation.")
