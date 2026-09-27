// Sahayak AI — Task and Verification Models

class TaskStep {
  final String stepId;
  final int stepNumber;
  final int totalSteps;
  final String fieldId;
  final String label;
  final String spokenPrompt;
  final String displayPrompt;
  final String inputType;
  final bool isRequired;
  String? currentValue;
  bool isConfirmed;

  TaskStep({
    required this.stepId,
    required this.stepNumber,
    required this.totalSteps,
    required this.fieldId,
    required this.label,
    required this.spokenPrompt,
    required this.displayPrompt,
    this.inputType = 'VOICE_OR_TEXT',
    this.isRequired = true,
    this.currentValue,
    this.isConfirmed = false,
  });

  factory TaskStep.fromJson(Map<String, dynamic> json) {
    return TaskStep(
      stepId: json['step_id'] ?? '',
      stepNumber: json['step_number'] ?? 1,
      totalSteps: json['total_steps'] ?? 1,
      fieldId: json['field_id'] ?? '',
      label: json['label'] ?? '',
      spokenPrompt: json['spoken_prompt'] ?? '',
      displayPrompt: json['display_prompt'] ?? '',
      inputType: json['input_type'] ?? 'VOICE_OR_TEXT',
      isRequired: json['is_required'] ?? true,
      currentValue: json['current_value'],
      isConfirmed: json['is_confirmed'] ?? false,
    );
  }
}

class AccessibleTaskFlow {
  final String taskId;
  final String taskType;
  final String strategy;
  final int totalSteps;
  final int currentStepIndex;
  final List<TaskStep> steps;

  AccessibleTaskFlow({
    required this.taskId,
    required this.taskType,
    required this.strategy,
    required this.totalSteps,
    required this.currentStepIndex,
    required this.steps,
  });

  factory AccessibleTaskFlow.fromJson(Map<String, dynamic> json) {
    final rawSteps = json['steps'] as List<dynamic>? ?? [];
    return AccessibleTaskFlow(
      taskId: json['task_id'] ?? '',
      taskType: json['task_type'] ?? 'FORM_COMPLETION',
      strategy: json['strategy'] ?? 'ONE_STEP_AT_A_TIME_VOICE',
      totalSteps: json['total_steps'] ?? rawSteps.length,
      currentStepIndex: json['current_step_index'] ?? 0,
      steps: rawSteps.map((s) => TaskStep.fromJson(s as Map<String, dynamic>)).toList(),
    );
  }
}

class VerificationResult {
  final String taskId;
  final String status; // IN_PROGRESS, COMPLETED, BLOCKED
  final double completionPercentage;
  final int completedFields;
  final int totalFields;
  final String? verificationToken;
  final String summaryMessage;

  VerificationResult({
    required this.taskId,
    required this.status,
    required this.completionPercentage,
    required this.completedFields,
    required this.totalFields,
    this.verificationToken,
    required this.summaryMessage,
  });

  factory VerificationResult.fromJson(Map<String, dynamic> json) {
    return VerificationResult(
      taskId: json['task_id'] ?? '',
      status: json['status'] ?? 'IN_PROGRESS',
      completionPercentage: (json['completion_percentage'] as num?)?.toDouble() ?? 0.0,
      completedFields: json['completed_fields'] ?? 0,
      totalFields: json['total_fields'] ?? 0,
      verificationToken: json['verification_token'],
      summaryMessage: json['summary_message'] ?? '',
    );
  }
}

class HeatmapItem {
  final String interactionPoint;
  final String complexity; // LOW, MEDIUM, HIGH
  final String color; // GREEN, YELLOW, RED
  final String reason;
  final int retryCount;

  HeatmapItem({
    required this.interactionPoint,
    required this.complexity,
    required this.color,
    required this.reason,
    required this.retryCount,
  });

  factory HeatmapItem.fromJson(Map<String, dynamic> json) {
    return HeatmapItem(
      interactionPoint: json['interaction_point'] ?? '',
      complexity: json['complexity'] ?? 'LOW',
      color: json['color'] ?? 'GREEN',
      reason: json['reason'] ?? '',
      retryCount: json['retry_count'] ?? 0,
    );
  }
}
