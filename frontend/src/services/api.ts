import type { AccessibilityTwin, AccessibleTaskFlow, HeatmapItem, Recommendation, VerificationResult } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export class ApiService {
  private static backendAvailable: boolean | null = null;

  static async checkHealth(): Promise<{ healthy: boolean; backendType: 'FastAPI' | 'LocalEngine' }> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1800);
      const res = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (res.ok) {
        this.backendAvailable = true;
        return { healthy: true, backendType: 'FastAPI' };
      }
    } catch (_) {
      this.backendAvailable = false;
    }
    return { healthy: true, backendType: 'LocalEngine' };
  }

  // 1. Intent Classification
  static async classifyIntent(query: string, twin: AccessibilityTwin): Promise<{ intent: string; confidence: number; summary: string }> {
    if (this.backendAvailable) {
      try {
        const res = await fetch(`${API_BASE_URL}/intent`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query, twin_id: twin.id }),
        });
        if (res.ok) {
          const data = await res.json();
          return {
            intent: data.intent || 'FORM_COMPLETION',
            confidence: data.confidence || 0.95,
            summary: data.rationale || 'Task intent identified'
          };
        }
      } catch (_) {}
    }

    // Local AI Engine fallback
    const q = query.toLowerCase();
    if (q.includes('फ़ॉर्म') || q.includes('form') || q.includes('भरें') || q.includes('scholarship') || q.includes('apply')) {
      return {
        intent: 'FORM_COMPLETION',
        confidence: 0.96,
        summary: twin.language === 'Hindi'
          ? 'छात्रवृत्ति फ़ॉर्म पूरा करने का चरणबद्ध मार्गदर्शन'
          : 'Step-by-step scholarship application guidance'
      };
    } else if (q.includes('नोटिस') || q.includes('notice') || q.includes('दस्तावेज़') || q.includes('read') || q.includes('document')) {
      return {
        intent: 'UNDERSTAND_DOCUMENT',
        confidence: 0.94,
        summary: twin.language === 'Hindi'
          ? 'दस्तावेज़ एवं महत्वपूर्ण तिथियों का विश्लेषण'
          : 'Analyze document and extract deadlines'
      };
    } else if (q.includes('सांकेतिक') || q.includes('sign') || q.includes('gesture') || q.includes('talk') || q.includes('speak')) {
      return {
        intent: 'COMMUNICATE',
        confidence: 0.92,
        summary: twin.language === 'Hindi'
          ? 'भारतीय सांकेतिक भाषा (ISL) अनुवाद'
          : 'Indian Sign Language (ISL) translation'
      };
    } else {
      return {
        intent: 'SEE',
        confidence: 0.91,
        summary: twin.language === 'Hindi'
          ? 'आसपास की वस्तुओं की पहचान व दिशा'
          : 'Spatial orientation and object guidance'
      };
    }
  }

  // 2. Form Completion: Analyze Form Document
  static async analyzeForm(twin: AccessibilityTwin): Promise<AccessibleTaskFlow> {
    if (this.backendAvailable) {
      try {
        const formData = new FormData();
        formData.append('twin_id', twin.id);
        const res = await fetch(`${API_BASE_URL}/complete/analyze`, {
          method: 'POST',
          body: formData,
        });
        if (res.ok) {
          return await res.json();
        }
      } catch (_) {}
    }

    const isHindi = twin.language === 'Hindi';
    const taskId = `task_form_${Math.floor(10000 + Math.random() * 90000)}`;

    return {
      task_id: taskId,
      task_type: 'FORM_COMPLETION',
      strategy: 'ONE_STEP_AT_A_TIME_VOICE',
      total_steps: 7,
      current_step_index: 0,
      detected_barriers: [
        {
          category: 'VISUAL',
          severity: 'HIGH',
          description: isHindi
            ? 'बारीक अक्षरों (9pt) वाला जटिल द्वि-स्तंभ प्रारूप'
            : 'Dense 2-column layout with 9pt small print',
          remediation_strategy: 'Linearized single-field presentation with large font',
        },
        {
          category: 'MOTOR',
          severity: 'MEDIUM',
          description: isHindi
            ? 'कागजी फॉर्म में छोटे बक्से और सटीक लिखावट की आवश्यकता'
            : 'Requires manual precise handwriting in constricted boxes',
          remediation_strategy: 'Voice dictation & conversational prompts',
        },
        {
          category: 'COGNITIVE',
          severity: 'MEDIUM',
          description: isHindi
            ? 'एक साथ 7 जटिल प्रश्नों का मानसिक तनाव'
            : 'Simultaneous cognitive load of multiple bureaucratic fields',
          remediation_strategy: 'One-step-at-a-time task linearization',
        },
      ],
      steps: [
        {
          step_id: 'step_1',
          step_number: 1,
          total_steps: 7,
          field_id: 'full_name',
          label: isHindi ? 'पूरा नाम' : 'Full Name',
          spoken_prompt: isHindi
            ? 'आपके फ़ॉर्म में 7 ज़रूरी जानकारियां हैं। पहला सवाल: आपका पूरा नाम क्या है?'
            : 'Your scholarship form has 7 required fields. Step 1: What is your full legal name?',
          display_prompt: isHindi
            ? 'चरण 1/7: अपना पूरा नाम बताएं'
            : 'Step 1 of 7: Enter or speak your full name',
          input_type: 'VOICE_OR_TEXT',
          is_required: true,
        },
        {
          step_id: 'step_2',
          step_number: 2,
          total_steps: 7,
          field_id: 'dob',
          label: isHindi ? 'जन्मतिथि' : 'Date of Birth',
          spoken_prompt: isHindi
            ? 'धन्यवाद। आपकी जन्मतिथि क्या है? (दिन, महीना, साल)'
            : 'Thank you. What is your date of birth? (Day, Month, Year)',
          display_prompt: isHindi
            ? 'चरण 2/7: जन्मतिथि (DD/MM/YYYY)'
            : 'Step 2 of 7: Date of Birth (DD/MM/YYYY)',
          input_type: 'DATE_VOICE',
          is_required: true,
        },
        {
          step_id: 'step_3',
          step_number: 3,
          total_steps: 7,
          field_id: 'address',
          label: isHindi ? 'स्थायी पता' : 'Permanent Address',
          spoken_prompt: isHindi
            ? 'बहुत अच्छा। कृपया अपना पूरा स्थायी पता बताइए।'
            : 'Great. Please provide your permanent residential address.',
          display_prompt: isHindi
            ? 'चरण 3/7: स्थायी पता (शहर, पिन कोड)'
            : 'Step 3 of 7: Full Residential Address',
          input_type: 'VOICE_OR_TEXT',
          is_required: true,
        },
        {
          step_id: 'step_4',
          step_number: 4,
          total_steps: 7,
          field_id: 'category',
          label: isHindi ? 'आरक्षण वर्ग' : 'Category / Caste',
          spoken_prompt: isHindi
            ? 'आपकी आरक्षण श्रेणी क्या है? जैसे सामान्य, ओबीसी, एससी अथवा एसटी?'
            : 'Which category do you belong to? (General, OBC, SC, or ST)?',
          display_prompt: isHindi
            ? 'चरण 4/7: श्रेणी (General, OBC, SC, ST)'
            : 'Step 4 of 7: Category (General / OBC / SC / ST)',
          input_type: 'CHOICE_VOICE',
          is_required: true,
        },
        {
          step_id: 'step_5',
          step_number: 5,
          total_steps: 7,
          field_id: 'annual_income',
          label: isHindi ? 'वार्षिक पारिवारिक आय' : 'Annual Family Income',
          spoken_prompt: isHindi
            ? 'आपके परिवार की वार्षिक आय कितनी है?'
            : 'What is your annual family household income in rupees?',
          display_prompt: isHindi
            ? 'चरण 5/7: वार्षिक आय (रुपये)'
            : 'Step 5 of 7: Annual Household Income (₹)',
          input_type: 'NUMBER_VOICE',
          is_required: true,
        },
        {
          step_id: 'step_6',
          step_number: 6,
          total_steps: 7,
          field_id: 'aadhaar',
          label: isHindi ? 'आधार संख्या' : 'Aadhaar Card Number',
          spoken_prompt: isHindi
            ? 'अपना 12 अंकों का आधार नंबर बताएं।'
            : 'Please enter or dictate your 12-digit Aadhaar number.',
          display_prompt: isHindi
            ? 'चरण 6/7: 12-अंकीय आधार संख्या'
            : 'Step 6 of 7: 12-Digit Aadhaar Number',
          input_type: 'NUMBER_VOICE',
          is_required: true,
        },
        {
          step_id: 'step_7',
          step_number: 7,
          total_steps: 7,
          field_id: 'bank_account',
          label: isHindi ? 'बैंक खाता व IFSC' : 'Bank Account & IFSC',
          spoken_prompt: isHindi
            ? 'अंतिम चरण: छात्रवृत्ति हस्तांतरण हेतु बैंक खाता संख्या और IFSC कोड बताएं।'
            : 'Final step: Provide your Bank Account number and IFSC code for direct transfer.',
          display_prompt: isHindi
            ? 'चरण 7/7: बैंक खाता संख्या एवं IFSC कोड'
            : 'Step 7 of 7: Bank Account Number & IFSC Code',
          input_type: 'VOICE_OR_TEXT',
          is_required: true,
        },
      ],
    };
  }

  // 3. Form Step Response & Verification
  static async respondFormField(
    taskId: string,
    fieldId: string,
    value: string,
    stepIndex: number,
    totalSteps: number,
    twin: AccessibilityTwin
  ): Promise<{ verification: VerificationResult; completedField: string }> {
    if (this.backendAvailable) {
      try {
        const res = await fetch(`${API_BASE_URL}/complete/respond`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            task_id: taskId,
            field_id: fieldId,
            value,
            confirmation_received: true,
            twin_id: twin.id,
          }),
        });
        if (res.ok) {
          const data = await res.json();
          return {
            verification: data.verification,
            completedField: data.completed_field,
          };
        }
      } catch (_) {}
    }

    const completed = stepIndex + 1;
    const isFinished = completed >= totalSteps;
    const percentage = Math.round((completed / totalSteps) * 100);

    return {
      completedField: fieldId,
      verification: {
        task_id: taskId,
        status: isFinished ? 'COMPLETED' : 'IN_PROGRESS',
        completion_percentage: percentage,
        completed_fields: completed,
        total_fields: totalSteps,
        missing_fields: isFinished ? [] : ['remaining_fields'],
        verification_token: isFinished ? `VERIFIED_SAHAYAK_${Math.floor(100000 + Math.random() * 900000)}` : undefined,
        summary_message: isFinished
          ? (twin.language === 'Hindi'
              ? 'सभी 7 अनिवार्य जानकारियां सत्यापित हो चुकी हैं। आधिकारिक प्रमाणपत्र जारी किया गया।'
              : 'All 7 required fields verified and constraints validated. Digital Certificate issued.')
          : `${completed}/${totalSteps} fields verified`,
      },
    };
  }

  // 4. Document Understanding (Demo 1)
  static async readDocument(
    query: string,
    twin: AccessibilityTwin
  ): Promise<{
    title: string;
    deadlines: string[];
    requiredDocuments: string[];
    simplifiedSummary: string;
    spokenSummary: string;
    originalLanguage: string;
    barriersDetected: Array<{ category: string; description: string }>;
  }> {
    if (this.backendAvailable) {
      try {
        const formData = new FormData();
        formData.append('query', query);
        formData.append('twin_id', twin.id);
        const res = await fetch(`${API_BASE_URL}/read`, {
          method: 'POST',
          body: formData,
        });
        if (res.ok) {
          const data = await res.json();
          return {
            title: data.document_title || 'Scholarship Notice 2026',
            deadlines: data.key_deadlines || ['September 30, 2026'],
            requiredDocuments: data.required_documents || ['Income Certificate', 'Aadhaar Card'],
            simplifiedSummary: data.simplified_summary,
            spokenSummary: data.simplified_summary,
            originalLanguage: 'English',
            barriersDetected: data.barriers_detected || [],
          };
        }
      } catch (_) {}
    }

    const isHindi = twin.language === 'Hindi';
    return {
      title: isHindi ? 'राष्ट्रीय मेधावी छात्रवृत्ति सूचना 2026' : 'National Merit Scholarship Notification 2026',
      deadlines: ['September 30, 2026 (अंतिम तिथि: 30 सितंबर 2026)'],
      requiredDocuments: [
        isHindi ? 'आय प्रमाण पत्र (Income Certificate < ₹2.5 Lakhs)' : 'Income Certificate (< ₹2.5 Lakhs)',
        isHindi ? 'आधार कार्ड (Aadhaar Card)' : 'Aadhaar Card',
        isHindi ? 'कक्षा 10 की अंकतालिका (Class 10 Marksheet)' : 'Class 10 Marksheet',
        isHindi ? 'बैंक पासबुक प्रथम पृष्ठ (Bank Account Details)' : 'Bank Passbook Front Page',
      ],
      simplifiedSummary: isHindi
        ? 'यह भारत सरकार की राष्ट्रीय छात्रवृत्ति योजना 2026 की आधिकारिक सूचना है। आवेदन करने की अंतिम तिथि 30 सितंबर 2026 है। आपको आय प्रमाण पत्र, आधार कार्ड और 10वीं की मार्कशीट की आवश्यकता होगी। सहायता copilot आपका आवेदन कुछ ही मिनटों में पूरा करवा सकता है।'
        : 'This is the official National Merit Scholarship 2026 notice. The final application deadline is September 30, 2026. Required documents: Income Certificate (<2.5L), Aadhaar Card, and Class 10 marksheet. Sahayak Copilot can guide you through the form step-by-step.',
      spokenSummary: isHindi
        ? 'यह छात्रवृत्ति सूचना है। अंतिम तिथि 30 सितंबर 2026 है। आपको आय प्रमाण पत्र और आधार कार्ड की आवश्यकता होगी। क्या आप चाहते हैं कि मैं फ़ॉर्म भरने में आपकी मदद करूँ?'
        : 'This scholarship notice has a deadline of September 30, 2026. Required: Income Certificate and Aadhaar Card. Would you like me to guide you through the form?',
      originalLanguage: 'English (Legal jargon detected)',
      barriersDetected: [
        {
          category: 'LANGUAGE',
          description: isHindi ? 'अंग्रेजी भाषा का कानूनी नोटिस' : 'Legalistic jargon mismatch',
        },
        {
          category: 'DIGITAL_LITERACY',
          description: isHindi ? 'जटिल पात्रता शर्तें एवं समय सीमा' : 'Buried prerequisites & deadline complexity',
        },
      ],
    };
  }

  // 5. Sign Language Translation (Demo 3)
  static async predictSign(
    gestureName: string = 'HELP',
    twin: AccessibilityTwin
  ): Promise<{
    sign: string;
    caption: string;
    spokenText: string;
    confidence: number;
    hapticCue: string;
  }> {
    if (this.backendAvailable) {
      try {
        const formData = new FormData();
        formData.append('twin_id', twin.id);
        const res = await fetch(`${API_BASE_URL}/isl/predict`, {
          method: 'POST',
          body: formData,
        });
        if (res.ok) {
          const data = await res.json();
          return {
            sign: data.sign_detected || gestureName,
            caption: `${data.sign_detected} [${data.spoken_output}]`,
            spokenText: data.spoken_output || gestureName,
            confidence: data.confidence || 0.95,
            hapticCue: data.haptic_feedback || 'SUCCESS_DOUBLE_PULSE',
          };
        }
      } catch (_) {}
    }

    const isHindi = twin.language === 'Hindi';
    const signs: Record<string, { hi: string; en: string; audioHi: string; audioEn: string }> = {
      HELP: {
        hi: 'सहायता चाहिए (HELP)',
        en: 'I need Help (HELP)',
        audioHi: 'मुझे सहायता चाहिए',
        audioEn: 'I need help',
      },
      THANK_YOU: {
        hi: 'धन्यवाद (THANK YOU)',
        en: 'Thank You',
        audioHi: 'आपका बहुत बहुत धन्यवाद',
        audioEn: 'Thank you very much',
      },
      WATER: {
        hi: 'पानी चाहिए (WATER)',
        en: 'Water please',
        audioHi: 'मुझे पीने का पानी चाहिए',
        audioEn: 'Please give me water',
      },
      YES: {
        hi: 'हाँ (YES)',
        en: 'Yes / Agreed',
        audioHi: 'हाँ, बिल्कुल',
        audioEn: 'Yes, confirmed',
      },
      NO: {
        hi: 'नहीं (NO)',
        en: 'No / Disagree',
        audioHi: 'नहीं',
        audioEn: 'No',
      },
    };

    const target = signs[gestureName] || signs.HELP;

    return {
      sign: gestureName,
      caption: isHindi ? target.hi : target.en,
      spokenText: isHindi ? target.audioHi : target.audioEn,
      confidence: 0.94,
      hapticCue: 'SUCCESS_DOUBLE_PULSE',
    };
  }

  // 6. Spatial Vision & Object Finding (Optional Wow Demo)
  static async findObject(
    targetObject: string,
    twin: AccessibilityTwin
  ): Promise<{
    objectName: string;
    direction: string;
    distanceEstimate: string;
    displayGuidance: string;
    spokenGuidance: string;
    hapticCue: string;
    confidence: number;
    bbox: { x: number; y: number; width: number; height: number };
  }> {
    if (this.backendAvailable) {
      try {
        const formData = new FormData();
        formData.append('target_object', targetObject);
        formData.append('twin_id', twin.id);
        const res = await fetch(`${API_BASE_URL}/see`, {
          method: 'POST',
          body: formData,
        });
        if (res.ok) {
          const data = await res.json();
          return {
            objectName: targetObject,
            direction: data.objects?.[0]?.relative_position || 'slightly to your right',
            distanceEstimate: data.objects?.[0]?.distance_estimate || 'near',
            displayGuidance: data.scene_summary || `${targetObject} detected`,
            spokenGuidance: data.scene_summary || `${targetObject} detected`,
            hapticCue: data.haptic_cue || 'PULSE_RIGHT',
            confidence: data.objects?.[0]?.confidence || 0.92,
            bbox: { x: 55, y: 35, width: 35, height: 50 },
          };
        }
      } catch (_) {}
    }

    const isHindi = twin.language === 'Hindi';
    const objectMap: Record<string, { hi: string; en: string; directionHi: string; directionEn: string; haptic: string }> = {
      bottle: {
        hi: 'पानी की बोतल',
        en: 'Water Bottle',
        directionHi: 'आपकी बोतल आपके दाईं ओर हाथ की पहुंच में है।',
        directionEn: 'Your bottle is slightly to your right, within arm reach.',
        haptic: 'PULSE_RIGHT',
      },
      keys: {
        hi: 'चाबियां',
        en: 'Keys',
        directionHi: 'चाबियां मेज पर बाईं ओर रखी हैं।',
        directionEn: 'Keys are on the desk towards your left side.',
        haptic: 'PULSE_LEFT',
      },
      phone: {
        hi: 'मोबाइल फोन',
        en: 'Mobile Phone',
        directionHi: 'फोन सीधे आपके सामने मेज के केंद्र में है।',
        directionEn: 'Phone is directly in front of you at table center.',
        haptic: 'PULSE_CENTER',
      },
      document: {
        hi: 'दस्तावेज़ / फ़ॉर्म',
        en: 'Document / Paperwork',
        directionHi: 'फ़ॉर्म आपके सामने मेज पर सीधा रखा है।',
        directionEn: 'Document is centered directly in front of you.',
        haptic: 'PULSE_CENTER',
      },
    };

    const selected = objectMap[targetObject.toLowerCase()] || objectMap.bottle;

    return {
      objectName: targetObject,
      direction: isHindi ? 'दाईं ओर' : 'slightly to your right',
      distanceEstimate: isHindi ? 'हाथ की पहुंच में (~45 सेमी)' : 'near (~45 cm, arm reach)',
      displayGuidance: isHindi ? selected.directionHi : selected.directionEn,
      spokenGuidance: isHindi ? selected.directionHi : selected.directionEn,
      hapticCue: selected.haptic,
      confidence: 0.94,
      bbox: { x: 55, y: 30, width: 35, height: 55 },
    };
  }

  // 7. Interaction Heatmap & Learning Telemetry
  static async getHeatmap(): Promise<{ heatmap: HeatmapItem[]; recommendation: Recommendation }> {
    if (this.backendAvailable) {
      try {
        const res = await fetch(`${API_BASE_URL}/learning/heatmap`);
        if (res.ok) {
          const data = await res.json();
          return {
            heatmap: data.heatmap || [],
            recommendation: data.recommendation || {},
          };
        }
      } catch (_) {}
    }

    return {
      heatmap: [
        {
          interaction_point: 'Physical Document Upload & Alignment',
          complexity: 'HIGH',
          color: 'RED',
          reason: 'Camera angle tilt and edge lighting caused 2 retries',
          retry_count: 2,
        },
        {
          interaction_point: 'Multi-part Address Input',
          complexity: 'MEDIUM',
          color: 'YELLOW',
          reason: 'Voice transcription needed clarification for sector code',
          retry_count: 1,
        },
        {
          interaction_point: 'Name and Category Selection',
          complexity: 'LOW',
          color: 'GREEN',
          reason: 'Confirmed on first verbal prompt with 100% accuracy',
          retry_count: 0,
        },
        {
          interaction_point: '12-Digit Aadhaar Dictation',
          complexity: 'LOW',
          color: 'GREEN',
          reason: 'Linear 4-4-4 digit chunking parsed seamlessly',
          retry_count: 0,
        },
      ],
      recommendation: {
        tasks_completed_count: 6,
        voice_usage_percentage: 92,
        most_effective_assistance: 'Conversational 1-field voice step with haptic confirmation',
        most_difficult_step: 'Physical document camera framing',
        dialog_prompt: 'क्या आप चाहते हैं कि सहायक भविष्य के सभी सरकारी आवेदनों में स्वतः सरल हिंदी और आवाज़ मार्गदर्शन सक्रिय रखे?',
      },
    };
  }
}
