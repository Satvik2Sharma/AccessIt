// Sahayak AI — Complete Form Screen (Bhare / Complete Form)
// Genuine voice-driven and accessible form completion flow.
// Responds directly to speech input and voice navigation commands ("Next", "Aage badho", "Previous").

import 'package:flutter/material.dart';
import '../models/accessibility_twin.dart';
import '../models/task_flow.dart';
import '../services/api_service.dart';
import '../services/haptics_service.dart';
import '../services/voice_service.dart';

class CompleteFormScreen extends StatefulWidget {
  final AccessibilityTwin twin;

  const CompleteFormScreen({super.key, required this.twin});

  @override
  State<CompleteFormScreen> createState() => _CompleteFormScreenState();
}

class _CompleteFormScreenState extends State<CompleteFormScreen> {
  final MobileVoiceService _voiceService = MobileVoiceService();

  bool _isLoading = true;
  bool _isListening = false;
  String _listeningTranscript = '';
  AccessibleTaskFlow? _flow;
  int _currentStep = 0;
  final TextEditingController _inputController = TextEditingController();
  final Map<String, String> _answers = {};
  VerificationResult? _verification;

  // Demo sample values available on explicit request for testing
  final List<String> _sampleAnswers = [
    'Satvik Sharma',
    '15/08/2003',
    'Sector 62, Noida, Uttar Pradesh',
    'General',
    '180000',
    '9824 5510 1289',
    'SBI0004921 / 20394812839',
  ];

  @override
  void initState() {
    super.initState();
    _initVoiceAndLoadForm();
  }

  Future<void> _initVoiceAndLoadForm() async {
    final isHindi = widget.twin.language == 'Hindi';
    await _voiceService.initialize(language: isHindi ? 'hi-IN' : 'en-US');
    await _loadForm();
  }

  Future<void> _loadForm() async {
    setState(() => _isLoading = true);
    final flow = await ApiService.analyzeForm(widget.twin);
    if (!mounted) return;

    setState(() {
      _flow = flow;
      _isLoading = false;
      _currentStep = 0;
      _inputController.clear();
    });

    if (_flow != null && _flow!.steps.isNotEmpty) {
      _speakCurrentStep();
    }
  }

  void _speakCurrentStep() {
    if (_flow == null || _currentStep >= _flow!.steps.length) return;
    final step = _flow!.steps[_currentStep];
    final isHindi = widget.twin.language == 'Hindi';
    _voiceService.speak(step.spokenPrompt, language: isHindi ? 'hi-IN' : 'en-US');
  }

  Future<void> _toggleVoiceListening() async {
    if (_isListening) {
      await _voiceService.stopListening();
      if (mounted) {
        setState(() => _isListening = false);
      }
      return;
    }

    setState(() {
      _isListening = true;
      _listeningTranscript = '';
    });
    HapticsService.tactileClick();

    final isHindi = widget.twin.language == 'Hindi';
    await _voiceService.startListening(
      localeId: isHindi ? 'hi_IN' : 'en_US',
      onResult: (text) {
        if (!mounted) return;
        setState(() {
          _listeningTranscript = text;
        });
        _handleVoiceCommandOrInput(text);
      },
      onComplete: () {
        if (mounted) {
          setState(() => _isListening = false);
        }
      },
    );
  }

  void _handleVoiceCommandOrInput(String raw) {
    if (raw.trim().isEmpty) return;
    final lower = raw.toLowerCase().trim();

    // 1. Navigation commands: Next / Proceed / Aage badho / Confirm / Submit
    const nextTriggers = [
      'next', 'proceed', 'continue', 'aage badho', 'aage', 'agla',
      'आगे बढ़ो', 'आगे', 'अगला', 'बढ़ो', 'submit', 'confirm', 'पुष्टि'
    ];
    for (final trigger in nextTriggers) {
      if (lower == trigger || lower.endsWith(' $trigger') || lower.startsWith('$trigger ')) {
        _voiceService.stopListening();
        if (mounted) setState(() => _isListening = false);
        HapticsService.confirmationPulse();
        _submitStep();
        return;
      }
    }

    // 2. Navigation commands: Previous / Back / Peeche / Pichla
    const prevTriggers = [
      'previous', 'back', 'peeche', 'pichla', 'पीछे', 'पिछला', 'वापस'
    ];
    for (final trigger in prevTriggers) {
      if (lower == trigger || lower.endsWith(' $trigger') || lower.startsWith('$trigger ')) {
        _voiceService.stopListening();
        if (mounted) setState(() => _isListening = false);
        HapticsService.tactileClick();
        _goToPreviousStep();
        return;
      }
    }

    // 3. User spoken answer for the current field!
    setState(() {
      _inputController.text = raw.trim();
    });

    final isHindi = widget.twin.language == 'Hindi';
    final step = _flow!.steps[_currentStep];
    final promptFeedback = isHindi
        ? '${step.label} दर्ज हुआ: "$raw"। आगे बढ़ने के लिए "आगे बढ़ो" कहें।'
        : '${step.label} recorded as "$raw". Say "Next" or "Aage badho" to continue.';
    _voiceService.speak(promptFeedback, language: isHindi ? 'hi-IN' : 'en-US');
  }

  void _goToPreviousStep() {
    if (_flow == null || _currentStep <= 0) return;
    setState(() {
      _currentStep--;
      final prevStep = _flow!.steps[_currentStep];
      _inputController.text = _answers[prevStep.fieldId] ?? '';
    });
    _speakCurrentStep();
  }

  void _fillSampleAnswer() {
    if (_flow == null) return;
    HapticsService.tactileClick();
    final sample = _sampleAnswers.length > _currentStep ? _sampleAnswers[_currentStep] : '';
    setState(() {
      _inputController.text = sample;
    });
    final isHindi = widget.twin.language == 'Hindi';
    final step = _flow!.steps[_currentStep];
    final feedback = isHindi
        ? '${step.label} भरा गया: "$sample"। आगे बढ़ने के लिए "आगे बढ़ो" कहें या बटन दबाएं।'
        : '${step.label} pre-filled. Say "Next" or tap Confirm to proceed.';
    _voiceService.speak(feedback, language: isHindi ? 'hi-IN' : 'en-US');
  }

  void _submitStep() async {
    if (_flow == null) return;

    final step = _flow!.steps[_currentStep];
    final value = _inputController.text.trim();
    final isHindi = widget.twin.language == 'Hindi';

    if (value.isEmpty) {
      final prompt = isHindi
          ? 'कृपया उत्तर बोलें या लिखें।'
          : 'Please speak or enter an answer.';
      _voiceService.speak(prompt, language: isHindi ? 'hi-IN' : 'en-US');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(prompt)),
      );
      return;
    }

    // Validate with backend
    final res = await ApiService.respondFormField(
      taskId: _flow!.taskId,
      fieldId: step.fieldId,
      value: value,
      twin: widget.twin,
    );

    if (res != null && res['is_valid'] == false) {
      HapticsService.errorPulse();
      final errMsg = res['validation_error'] ?? (isHindi ? 'अमान्य प्रविष्टि, पुनः प्रयास करें।' : 'Validation failed, please recheck.');
      _voiceService.speak(errMsg, language: isHindi ? 'hi-IN' : 'en-US');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.error_outline, color: Colors.white),
                const SizedBox(width: 8),
                Expanded(child: Text(errMsg)),
              ],
            ),
            backgroundColor: Colors.red.shade800,
            duration: const Duration(seconds: 4),
          ),
        );
      }
      return;
    }

    _answers[step.fieldId] = value;

    if (_currentStep + 1 < _flow!.steps.length) {
      HapticsService.confirmationPulse();
      setState(() {
        _currentStep++;
        final nextStep = _flow!.steps[_currentStep];
        _inputController.text = _answers[nextStep.fieldId] ?? '';
        _listeningTranscript = '';
      });
      _speakCurrentStep();
    } else {
      // Completed all steps!
      HapticsService.successDoublePulse();
      final completionMsg = isHindi
          ? 'बधाई! फ़ॉर्म के सभी 7 चरण सफलतापूर्वक पूर्ण हुए।'
          : 'Congratulations! All 7 form fields verified and completed.';
      _voiceService.speak(completionMsg, language: isHindi ? 'hi-IN' : 'en-US');
      if (res != null && res['verification'] != null) {
        setState(() {
          _verification = VerificationResult.fromJson(res['verification']);
        });
      }
    }
  }

  @override
  void dispose() {
    _voiceService.stopListening();
    _voiceService.stopSpeaking();
    _inputController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isHindi = widget.twin.language == 'Hindi';

    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: Text(isHindi ? 'फ़ॉर्म विश्लेषण...' : 'Analyzing Form...')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_flow == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Error')),
        body: Center(
          child: ElevatedButton(
            onPressed: _loadForm,
            child: const Text('Retry Analysis'),
          ),
        ),
      );
    }

    // Show completion verification screen if finished
    if (_verification != null || _currentStep >= _flow!.steps.length) {
      return _buildCompletionView(theme, isHindi);
    }

    final step = _flow!.steps[_currentStep];

    return Scaffold(
      appBar: AppBar(
        title: Text(isHindi ? 'फ़ॉर्म भरें (Voice Form)' : 'Voice Form Assistant (Bhare)'),
        actions: [
          TextButton.icon(
            icon: const Icon(Icons.bolt, size: 18, color: Colors.amberAccent),
            label: Text(
              isHindi ? 'नमूना' : 'Sample',
              style: const TextStyle(color: Colors.amberAccent, fontSize: 13),
            ),
            onPressed: _fillSampleAnswer,
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Progress Bar & Step Counter
            LinearProgressIndicator(
              value: (_currentStep + 1) / _flow!.steps.length,
              backgroundColor: theme.colorScheme.surfaceContainerHighest,
              color: theme.colorScheme.primary,
              minHeight: 6,
            ),
            Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Step Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        isHindi
                          ? 'चरण ${_currentStep + 1} / ${_flow!.steps.length}'
                          : 'Step ${_currentStep + 1} of ${_flow!.steps.length}',
                        style: theme.textTheme.labelLarge?.copyWith(
                          color: theme.colorScheme.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primaryContainer,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          step.label,
                          style: TextStyle(
                            color: theme.colorScheme.onPrimaryContainer,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),

                  // Barrier Notification
                  _buildBarrierNotice(theme, isHindi),
                  const SizedBox(height: 16),

                  // Prompt Card
                  Card(
                    elevation: 3,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    child: Padding(
                      padding: const EdgeInsets.all(18.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              IconButton(
                                icon: const Icon(Icons.volume_up, size: 28),
                                color: theme.colorScheme.primary,
                                tooltip: 'Listen prompt',
                                onPressed: _speakCurrentStep,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  step.spokenPrompt,
                                  style: theme.textTheme.bodyLarge?.copyWith(
                                    fontWeight: FontWeight.w600,
                                    fontSize: 16,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Active Listening Banner
                  if (_isListening)
                    Container(
                      margin: const EdgeInsets.only(bottom: 16),
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: Colors.redAccent.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.redAccent, width: 1.5),
                      ),
                      child: Row(
                        children: [
                          const CircleAvatar(
                            radius: 8,
                            backgroundColor: Colors.redAccent,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  isHindi ? 'सुन रहा हूँ... बोलें:' : 'Listening... Speak now:',
                                  style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.redAccent, fontSize: 13),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  _listeningTranscript.isNotEmpty
                                      ? '"$_listeningTranscript"'
                                      : (isHindi ? 'अपना उत्तर बोलें या "आगे बढ़ो" कहें' : 'Speak your answer or say "Next" / "Aage badho"'),
                                  style: const TextStyle(color: Colors.white, fontSize: 14),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),

                  // Voice & Text Input Box
                  TextField(
                    controller: _inputController,
                    style: theme.textTheme.headlineMedium?.copyWith(fontSize: 18),
                    decoration: InputDecoration(
                      labelText: step.displayPrompt,
                      border: const OutlineInputBorder(),
                      suffixIcon: IconButton(
                        icon: Icon(
                          _isListening ? Icons.mic : Icons.mic_none,
                          color: _isListening ? Colors.redAccent : theme.colorScheme.primary,
                          size: 28,
                        ),
                        tooltip: isHindi ? 'बोलकर उत्तर दें' : 'Speak Answer',
                        onPressed: _toggleVoiceListening,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Voice Command Guidance Badge
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.tealAccent.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.tealAccent.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.record_voice_over, size: 18, color: Colors.tealAccent),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            isHindi
                                ? 'आवाज़ से आगे बढ़ें: "Next" या "आगे बढ़ो" कहें।'
                                : 'Voice Command: Say "Next" or "Aage badho" to proceed.',
                            style: const TextStyle(fontSize: 12, color: Colors.tealAccent),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Navigation Action Buttons
                  Row(
                    children: [
                      if (_currentStep > 0) ...[
                        Expanded(
                          flex: 1,
                          child: OutlinedButton.icon(
                            style: OutlinedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            icon: const Icon(Icons.arrow_back),
                            label: Text(isHindi ? 'पीछे' : 'Back'),
                            onPressed: _goToPreviousStep,
                          ),
                        ),
                        const SizedBox(width: 10),
                      ],
                      Expanded(
                        flex: 2,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: theme.colorScheme.primary,
                            foregroundColor: theme.colorScheme.onPrimary,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          icon: const Icon(Icons.check_circle_outline, size: 24),
                          label: Text(
                            isHindi ? 'पुष्टि करें व आगे बढ़ें' : 'Confirm & Next',
                            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                          onPressed: _submitStep,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBarrierNotice(ThemeData theme, bool isHindi) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.amber.withOpacity(0.15),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.amber.shade700),
      ),
      child: Row(
        children: [
          const Icon(Icons.shield_outlined, color: Colors.amber, size: 24),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              isHindi
                ? 'बाधा पहचान: 7 फ़ील्ड का जटिल फ़ॉर्म एक-एक करके सुगम आवाज़ में बदला गया।'
                : 'Barrier Remediated: 7-field dense form linearized into step-by-step voice flow.',
              style: theme.textTheme.bodyMedium?.copyWith(color: Colors.amber.shade200, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCompletionView(ThemeData theme, bool isHindi) {
    return Scaffold(
      appBar: AppBar(title: Text(isHindi ? 'सत्यापन संपन्न' : 'Task Verification')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 20),
            Center(
              child: Container(
                width: 90,
                height: 90,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.green,
                ),
                child: const Icon(Icons.verified, size: 54, color: Colors.white),
              ),
            ),
            const SizedBox(height: 20),
            Text(
              isHindi ? 'आवेदन सफलतापूर्वक सत्यापित व पूर्ण!' : 'Application Verified & Complete!',
              textAlign: TextAlign.center,
              style: theme.textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.green,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              isHindi
                ? 'सभी 7 आवश्यक फ़ील्ड नियमों और पात्रता के अनुसार मान्य हैं।'
                : 'All 7 fields validated against official scholarship eligibility criteria.',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 28),

            // Summary Card
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isHindi ? 'दर्ज विवरण सारांश:' : 'Submitted Details Summary:',
                      style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const Divider(height: 18),
                    ..._answers.entries.map(
                      (e) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4.0),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '${e.key}: ',
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                            ),
                            Expanded(
                              child: Text(
                                e.value,
                                style: const TextStyle(fontSize: 13),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 28),

            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                minimumSize: const Size.fromHeight(54),
                backgroundColor: theme.colorScheme.primary,
                foregroundColor: theme.colorScheme.onPrimary,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              icon: const Icon(Icons.home),
              label: Text(
                isHindi ? 'मुख्य स्क्रीन पर वापस जाएं' : 'Return to Home',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              onPressed: () {
                Navigator.pushReplacementNamed(context, '/home');
              },
            ),
          ],
        ),
      ),
    );
  }
}
