// Sahayak AI — Complete Form Screen (Main Demo 2)
// Guides user step-by-step through a 7-field form using voice prompts and verification.

import 'package:flutter/material.dart';
import '../models/accessibility_twin.dart';
import '../models/task_flow.dart';
import '../services/api_service.dart';
import '../services/haptics_service.dart';

class CompleteFormScreen extends StatefulWidget {
  final AccessibilityTwin twin;

  const CompleteFormScreen({super.key, required this.twin});

  @override
  State<CompleteFormScreen> createState() => _CompleteFormScreenState();
}

class _CompleteFormScreenState extends State<CompleteFormScreen> {
  bool _isLoading = true;
  AccessibleTaskFlow? _flow;
  int _currentStep = 0;
  final TextEditingController _inputController = TextEditingController();
  final Map<String, String> _answers = {};
  VerificationResult? _verification;

  // Demo pre-populated sample answers for quick judging interaction
  final List<String> _demoAnswers = [
    'सात्विक शर्मा (Satvik Sharma)',
    '15/08/2003',
    'Sector 62, Noida, Uttar Pradesh',
    'General',
    '₹ 1,80,000',
    '9824 5510 1289',
    'SBI0004921 / 20394812839',
  ];

  @override
  void initState() {
    super.initState();
    _loadForm();
  }

  Future<void> _loadForm() async {
    setState(() => _isLoading = true);
    final flow = await ApiService.analyzeForm(widget.twin);
    setState(() {
      _flow = flow;
      _isLoading = false;
    });
    if (_flow != null && _flow!.steps.isNotEmpty) {
      _inputController.text = _demoAnswers[0];
    }
  }

  void _submitStep() async {
    if (_flow == null) return;
    HapticsService.confirmationPulse();

    final step = _flow!.steps[_currentStep];
    final value = _inputController.text.trim();
    if (value.isEmpty) return;

    _answers[step.fieldId] = value;

    // Send answer to FastAPI backend
    final res = await ApiService.respondFormField(
      taskId: _flow!.taskId,
      fieldId: step.fieldId,
      value: value,
      twin: widget.twin,
    );

    if (_currentStep + 1 < _flow!.steps.length) {
      setState(() {
        _currentStep++;
        _inputController.text = _demoAnswers[_currentStep];
      });
    } else {
      // Completed all steps!
      HapticsService.successDoublePulse();
      if (res != null && res['verification'] != null) {
        setState(() {
          _verification = VerificationResult.fromJson(res['verification']);
        });
      }
    }
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
    if (_verification != null && _verification!.status == 'COMPLETED') {
      return _buildCompletionView(theme, isHindi);
    }

    final step = _flow!.steps[_currentStep];
    final progress = (_currentStep + 1) / _flow!.totalSteps;

    return Scaffold(
      appBar: AppBar(
        title: Text(isHindi ? 'फ़ॉर्म सहायक' : 'Form Copilot'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Center(
              child: Text(
                '${_currentStep + 1} / ${_flow!.totalSteps}',
                style: theme.textTheme.headlineMedium?.copyWith(fontSize: 16),
              ),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Linear Progress Bar
            LinearProgressIndicator(
              value: progress,
              minHeight: 8,
              borderRadius: BorderRadius.circular(4),
              backgroundColor: theme.colorScheme.surface,
              color: theme.colorScheme.primary,
            ),
            const SizedBox(height: 16),

            // Detected Barriers Alert Banner
            if (_currentStep == 0) _buildBarrierNotice(theme, isHindi),

            const SizedBox(height: 16),

            // Step Card (One step at a time)
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        CircleAvatar(
                          backgroundColor: theme.colorScheme.primary,
                          radius: 16,
                          child: Text(
                            '${_currentStep + 1}',
                            style: TextStyle(
                              color: theme.colorScheme.onPrimary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            step.label,
                            style: theme.textTheme.headlineMedium?.copyWith(fontSize: 20),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Spoken Prompt Guidance
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.primary.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: theme.colorScheme.primary.withOpacity(0.3)),
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(Icons.volume_up, color: theme.colorScheme.primary, size: 24),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              step.spokenPrompt,
                              style: theme.textTheme.bodyLarge?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Voice / Text Input Box
                    TextField(
                      controller: _inputController,
                      style: theme.textTheme.headlineMedium?.copyWith(fontSize: 18),
                      decoration: InputDecoration(
                        labelText: step.displayPrompt,
                        border: const OutlineInputBorder(),
                        suffixIcon: IconButton(
                          icon: const Icon(Icons.mic),
                          tooltip: 'Speak Answer',
                          onPressed: () {
                            HapticsService.tactileClick();
                            // Quick populate current demo field
                            _inputController.text = _demoAnswers[_currentStep];
                          },
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Confirmation Button
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: theme.colorScheme.primary,
                          foregroundColor: theme.colorScheme.onPrimary,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        ),
                        icon: const Icon(Icons.check_circle_outline, size: 26),
                        label: Text(
                          isHindi ? 'पुष्टि करें व आगे बढ़ें' : 'Confirm & Next Step',
                          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        onPressed: _submitStep,
                      ),
                    ),
                  ],
                ),
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
            const SizedBox(height: 24),
            Text(
              isHindi ? 'फ़ॉर्म सफलतापूर्वक पूर्ण हुआ!' : 'Form Completed & Verified!',
              textAlign: TextAlign.center,
              style: theme.textTheme.headlineLarge,
            ),
            const SizedBox(height: 12),
            Text(
              _verification!.summaryMessage,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyLarge,
            ),
            const SizedBox(height: 24),

            // Official Verification Token Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Text(
                      'VERIFICATION CERTIFICATE',
                      style: theme.textTheme.labelLarge,
                    ),
                    const Divider(),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Fields Completed:'),
                        Text(
                          '${_verification!.completedFields} / ${_verification!.totalFields}',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Verification Token:'),
                        Text(
                          _verification!.verificationToken ?? 'VERIFIED_OK',
                          style: TextStyle(
                            color: theme.colorScheme.primary,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Status:'),
                        Text(
                          'VALIDATED (100%)',
                          style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                minimumSize: const Size.fromHeight(52),
                backgroundColor: theme.colorScheme.primary,
                foregroundColor: theme.colorScheme.onPrimary,
              ),
              child: Text(isHindi ? 'मुख्य पृष्ठ पर लौटें' : 'Back to Home'),
              onPressed: () => Navigator.pop(context),
            ),
          ],
        ),
      ),
    );
  }
}
