// Sahayak AI — Accessibility Twin Dart Model
// Mirrors the backend Pydantic schema for functional interaction preferences.

class AccessibilityTwin {
  final String id;
  String language; // "Hindi", "English"
  String secondaryLanguage;
  bool largeText;
  bool highContrast;
  bool screenReader;
  bool captions;
  bool voiceInput;
  bool oneStepAtATime;
  bool simplifiedLanguage;
  bool hapticFeedback;
  String preferredInput; // "voice", "touch", "hybrid"
  String preferredOutput; // "voice", "text", "voice_and_text"

  AccessibilityTwin({
    this.id = 'default_user',
    this.language = 'Hindi',
    this.secondaryLanguage = 'English',
    this.largeText = true,
    this.highContrast = false,
    this.screenReader = false,
    this.captions = true,
    this.voiceInput = true,
    this.oneStepAtATime = true,
    this.simplifiedLanguage = true,
    this.hapticFeedback = true,
    this.preferredInput = 'voice',
    this.preferredOutput = 'voice_and_text',
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'language': language,
        'secondary_language': secondaryLanguage,
        'visual': {
          'large_text': largeText,
          'high_contrast': highContrast,
          'screen_reader': screenReader,
        },
        'hearing': {
          'captions': captions,
          'visual_alerts': true,
        },
        'motor': {
          'voice_input': voiceInput,
          'large_touch_targets': true,
        },
        'comprehension': {
          'simplified_language': simplifiedLanguage,
          'one_step_at_a_time': oneStepAtATime,
          'read_instructions_aloud': true,
        },
        'haptics': {
          'enabled': hapticFeedback,
          'intensity': 'strong',
        },
        'preferred_input': preferredInput,
        'preferred_output': preferredOutput,
      };

  factory AccessibilityTwin.fromJson(Map<String, dynamic> json) {
    final visual = json['visual'] ?? {};
    final motor = json['motor'] ?? {};
    final comprehension = json['comprehension'] ?? {};
    final haptics = json['haptics'] ?? {};
    final hearing = json['hearing'] ?? {};

    return AccessibilityTwin(
      id: json['id'] ?? 'default_user',
      language: json['language'] ?? 'Hindi',
      secondaryLanguage: json['secondary_language'] ?? 'English',
      largeText: visual['large_text'] ?? true,
      highContrast: visual['high_contrast'] ?? false,
      screenReader: visual['screen_reader'] ?? false,
      captions: hearing['captions'] ?? true,
      voiceInput: motor['voice_input'] ?? true,
      oneStepAtATime: comprehension['one_step_at_a_time'] ?? true,
      simplifiedLanguage: comprehension['simplified_language'] ?? true,
      hapticFeedback: haptics['enabled'] ?? true,
      preferredInput: json['preferred_input'] ?? 'voice',
      preferredOutput: json['preferred_output'] ?? 'voice_and_text',
    );
  }
}
