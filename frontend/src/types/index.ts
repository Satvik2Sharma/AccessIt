export type LanguagePreference = 'Hindi' | 'English' | 'Tamil' | 'Telugu' | 'Bengali' | 'Marathi';
export type InputModality = 'voice' | 'touch' | 'hybrid' | 'sign';
export type OutputModality = 'voice' | 'text' | 'voice_and_text' | 'haptic';

export interface VisualPreferences {
  largeText: boolean;
  highContrast: boolean;
  screenReader: boolean;
  magnificationLevel: number;
}

export interface HearingPreferences {
  captions: boolean;
  visualAlerts: boolean;
  signLanguage: boolean;
}

export interface MotorPreferences {
  voiceInput: boolean;
  largeTouchTargets: boolean;
  reduceScrolling: boolean;
  dwellTimeMs: number;
}

export interface ComprehensionPreferences {
  simplifiedLanguage: boolean;
  oneStepAtATime: boolean;
  readInstructionsAloud: boolean;
  showTaskProgress: boolean;
}

export interface HapticPreferences {
  enabled: boolean;
  intensity: 'light' | 'medium' | 'strong';
  tactileConfirmation: boolean;
}

export interface AccessibilityTwin {
  id: string;
  language: LanguagePreference;
  secondaryLanguage?: LanguagePreference;
  visual: VisualPreferences;
  hearing: HearingPreferences;
  motor: MotorPreferences;
  comprehension: ComprehensionPreferences;
  haptics: HapticPreferences;
  preferredInput: InputModality;
  preferredOutput: OutputModality;
}

export type TaskType = 
  | 'FORM_COMPLETION' 
  | 'UNDERSTAND_DOCUMENT' 
  | 'COMMUNICATE' 
  | 'SEE' 
  | 'READ' 
  | 'FIND_OBJECT';

export interface Barrier {
  category: 'VISUAL' | 'HEARING' | 'MOTOR' | 'COGNITIVE' | 'LANGUAGE' | 'DIGITAL_LITERACY' | 'INTERACTION_COMPLEXITY';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'BLOCKER';
  description: string;
  remediation_strategy: string;
}

export interface TaskStep {
  step_id: string;
  step_number: number;
  total_steps: number;
  field_id: string;
  label: string;
  spoken_prompt: string;
  display_prompt: string;
  input_type: string;
  is_required: boolean;
  current_value?: string;
  is_confirmed?: boolean;
}

export interface AccessibleTaskFlow {
  task_id: string;
  task_type: TaskType;
  strategy: string;
  total_steps: number;
  current_step_index: number;
  steps: TaskStep[];
  detected_barriers: Barrier[];
}

export interface VerificationResult {
  task_id: string;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'BLOCKED' | 'FAILED' | 'NEEDS_CONFIRMATION';
  completion_percentage: number;
  completed_fields: number;
  total_fields: number;
  missing_fields: string[];
  verification_token?: string;
  summary_message: string;
}

export interface HeatmapItem {
  interaction_point: string;
  complexity: 'LOW' | 'MEDIUM' | 'HIGH';
  color: 'GREEN' | 'YELLOW' | 'RED';
  reason: string;
  retry_count: number;
}

export interface Recommendation {
  tasks_completed_count: number;
  voice_usage_percentage: number;
  most_effective_assistance: string;
  most_difficult_step: string;
  dialog_prompt?: string;
  suggested_updates?: Partial<AccessibilityTwin>;
}
