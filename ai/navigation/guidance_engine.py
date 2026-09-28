"""
Sahayak AI — Navigation Guidance Engine
Generates simple camera-based local navigation instructions.
Does NOT claim GPS or map-level accuracy — strictly local scene guidance.
"""
from typing import List, Dict, Any, Optional
from shared.schemas.models import NavigationInstruction, SpatialObject, AccessibilityTwin, LanguagePreference
from ai.navigation.obstacle_detector import ObstacleDetector


class GuidanceEngine:
    """
    Produces NavigationInstruction from scene objects.
    Integrates with voice and haptic layers for multimodal output.
    """

    def __init__(self):
        self.obstacle_detector = ObstacleDetector()

    def guide(
        self,
        objects: Optional[List[SpatialObject]] = None,
        target_label: Optional[str] = None,
        twin: Optional[AccessibilityTwin] = None,
    ) -> List[NavigationInstruction]:
        """
        Generate navigation instructions from scene objects.

        Args:
            objects: list of SpatialObjects from scene analysis
            target_label: optional label of the object to navigate toward
            twin: Accessibility Twin for language preference

        Returns:
            list of NavigationInstruction (ordered by priority)
        """
        is_hindi = twin and twin.language == LanguagePreference.HINDI
        objects_list = objects or []
        target = target_label.strip() if target_label else None
        instructions: List[NavigationInstruction] = []

        # 1. Check for obstacles
        obstacles = self.obstacle_detector.detect_obstacles(objects_list)
        for obs in obstacles:
            zone = obs["horizontal_zone"]
            if zone == "center":
                direction = "stop"
                desc = f"Obstacle ahead: {obs['label']}. Stop."
                desc_hi = f"आगे बाधा: {obs['label']}। रुकें।"
            elif zone == "right":
                direction = "slight_left"
                desc = f"{obs['label']} on your right. Move slightly left."
                desc_hi = f"{obs['label']} दाईं ओर है। थोड़ा बाईं ओर जाएं।"
            else:
                direction = "slight_right"
                desc = f"{obs['label']} on your left. Move slightly right."
                desc_hi = f"{obs['label']} बाईं ओर है। थोड़ा दाईं ओर जाएं।"

            instructions.append(NavigationInstruction(
                direction=direction,
                description=desc,
                description_hi=desc_hi,
                urgency="HIGH" if obs["severity"] == "HIGH" else "NORMAL",
                haptic_cue=f"PULSE_{direction.upper().replace('SLIGHT_', '')}",
                obstacle_detected=True,
                obstacle_label=obs["label"],
            ))

        # 2. Guide toward target object if specified
        if target:
            target_objs = [o for o in objects_list if target.lower() in o.label.lower()]
            if target_objs:
                target = target_objs[0]
                zone = target.horizontal_zone
                if zone == "left":
                    direction = "left"
                    desc = f"{target.label} is to your {target.direction}. Turn left."
                    desc_hi = f"{target.label} {target.direction} पर है। बाईं ओर मुड़ें।"
                    haptic = "PULSE_LEFT"
                elif zone == "right":
                    direction = "right"
                    desc = f"{target.label} is to your {target.direction}. Turn right."
                    desc_hi = f"{target.label} {target.direction} पर है। दाईं ओर मुड़ें।"
                    haptic = "PULSE_RIGHT"
                else:
                    direction = "forward"
                    desc = f"{target.label} is directly ahead at {target.direction}."
                    desc_hi = f"{target.label} सीधे आगे {target.direction} पर है।"
                    haptic = "DOUBLE_PULSE_CENTER"
                instructions.append(NavigationInstruction(
                    direction=direction,
                    description=desc,
                    description_hi=desc_hi,
                    urgency="NORMAL",
                    haptic_cue=haptic,
                    obstacle_detected=False,
                ))

        # 3. Default: no obstacles, path clear
        if not instructions:
            instructions.append(NavigationInstruction(
                direction="forward",
                description="Path appears clear. Move forward carefully.",
                description_hi="रास्ता साफ दिखता है। सावधानी से आगे बढ़ें।",
                urgency="NORMAL",
                haptic_cue="LIGHT_PULSE",
                obstacle_detected=False,
            ))

        return instructions
