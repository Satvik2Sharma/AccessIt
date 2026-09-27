"""
Sahayak AI — Accessible Task Flow Compiler
Transforms underlying complex tasks into accessible, personalized interaction flows
tailored to the user's Accessibility Twin and detected barriers.
"""

from typing import List, Dict, Any
from shared.schemas.models import (
    AccessibilityTwin,
    TaskType,
    Barrier,
    AccessibleTaskFlow,
    TaskStep,
    LanguagePreference,
)


class AccessibleTaskFlowCompiler:
    def __init__(self):
        # Master field catalog for scholarship application form (Hackathon Main Demo)
        self._standard_form_fields = [
            {
                "field_id": "full_name",
                "label": "Full Name",
                "en_prompt": "Your form has 7 required fields. Step 1: What is your full name?",
                "hi_prompt": "आपके फ़ॉर्म में 7 ज़रूरी जानकारियां हैं। पहला सवाल: आपका पूरा नाम क्या है?",
                "en_display": "Step 1 of 7: Speak or enter your full name",
                "hi_display": "चरण 1/7: अपना पूरा नाम बताएं",
                "type": "VOICE_OR_TEXT",
            },
            {
                "field_id": "dob",
                "label": "Date of Birth",
                "en_prompt": "Thank you. Step 2: What is your date of birth?",
                "hi_prompt": "धन्यवाद। दूसरा सवाल: आपकी जन्मतिथि क्या है?",
                "en_display": "Step 2 of 7: What is your date of birth?",
                "hi_display": "चरण 2/7: जन्मतिथि बताएं (दिन, महीना, साल)",
                "type": "VOICE_OR_TEXT",
            },
            {
                "field_id": "address",
                "label": "Residential Address",
                "en_prompt": "Got it. Step 3: What is your permanent residential address?",
                "hi_prompt": "समझ गया। तीसरा सवाल: आपका स्थायी निवास पता क्या है?",
                "en_display": "Step 3 of 7: What is your permanent address?",
                "hi_display": "चरण 3/7: स्थायी निवास पता बताएं",
                "type": "VOICE_OR_TEXT",
            },
            {
                "field_id": "category",
                "label": "Reservation Category",
                "en_prompt": "Step 4: What is your category? General, OBC, SC, or ST?",
                "hi_prompt": "चौथा सवाल: आपकी श्रेणी क्या है? सामान्य, ओबीसी, एससी, या एसटी?",
                "en_display": "Step 4 of 7: Select or speak Category (General, OBC, SC, ST)",
                "hi_display": "चरण 4/7: श्रेणी बताएं (सामान्य, ओबीसी, एससी, एसटी)",
                "type": "CHOICE_OR_VOICE",
            },
            {
                "field_id": "annual_income",
                "label": "Annual Family Income",
                "en_prompt": "Step 5: What is your total annual family income?",
                "hi_prompt": "पाँचवा सवाल: आपकी वार्षिक पारिवारिक आय कितनी है?",
                "en_display": "Step 5 of 7: Enter annual family income in Rupees",
                "hi_display": "चरण 5/7: वार्षिक पारिवारिक आय बताएं",
                "type": "NUMERIC_OR_VOICE",
            },
            {
                "field_id": "aadhaar",
                "label": "Aadhaar Number",
                "en_prompt": "Step 6: Please provide your 12-digit Aadhaar number.",
                "hi_prompt": "छठा सवाल: अपना 12 अंकों का आधार नंबर बताएं।",
                "en_display": "Step 6 of 7: 12-digit Aadhaar number",
                "hi_display": "चरण 6/7: आधार नंबर (12 अंक)",
                "type": "NUMERIC_OR_VOICE",
            },
            {
                "field_id": "bank_account",
                "label": "Bank Account & IFSC",
                "en_prompt": "Final step 7: What is your bank account number and IFSC code for scholarship transfer?",
                "hi_prompt": "अंतिम सवाल: छात्रवृत्ति राशि के लिए अपना बैंक खाता नंबर और IFSC कोड बताएं।",
                "en_display": "Step 7 of 7: Bank Account & IFSC Code",
                "hi_display": "चरण 7/7: बैंक खाता नंबर और IFSC कोड",
                "type": "VOICE_OR_TEXT",
            },
        ]

    def compile_form_flow(
        self,
        task_id: str,
        twin: AccessibilityTwin,
        barriers: List[Barrier]
    ) -> AccessibleTaskFlow:
        """
        Compiles the form into a personalized AccessibleTaskFlow.
        """
        is_hindi = twin.language == LanguagePreference.HINDI
        total = len(self._standard_form_fields)
        steps: List[TaskStep] = []

        for idx, item in enumerate(self._standard_form_fields):
            spoken = item["hi_prompt"] if is_hindi else item["en_prompt"]
            display = item["hi_display"] if is_hindi else item["en_display"]

            if twin.comprehension.simplified_language:
                # Ensure simplified wording
                pass

            steps.append(
                TaskStep(
                    step_id=f"step_{idx+1}",
                    step_number=idx + 1,
                    total_steps=total,
                    field_id=item["field_id"],
                    label=item["label"],
                    spoken_prompt=spoken,
                    display_prompt=display,
                    input_type=item["type"],
                    is_required=True,
                )
            )

        strategy = "ONE_STEP_AT_A_TIME_VOICE" if twin.comprehension.one_step_at_a_time else "LINEAR_FORM"

        return AccessibleTaskFlow(
            task_id=task_id,
            task_type=TaskType.FORM_COMPLETION,
            strategy=strategy,
            total_steps=total,
            current_step_index=0,
            steps=steps,
            detected_barriers=barriers,
        )
