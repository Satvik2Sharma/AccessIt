// Sahayak AI — Accessibility Twin Profile & Onboarding Screen
// Allows user to configure functional interaction preferences without clinical labeling.

import 'package:flutter/material.dart';
import '../models/accessibility_twin.dart';
import '../services/haptics_service.dart';

class ProfileScreen extends StatefulWidget {
  final AccessibilityTwin twin;
  final Function(AccessibilityTwin) onSave;

  const ProfileScreen({super.key, required this.twin, required this.onSave});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  late String _language;
  late bool _voiceInput;
  late bool _largeText;
  late bool _highContrast;
  late bool _oneStepAtATime;
  late bool _simplifiedLanguage;
  late bool _haptics;

  @override
  void initState() {
    super.initState();
    _language = widget.twin.language;
    _voiceInput = widget.twin.voiceInput;
    _largeText = widget.twin.largeText;
    _highContrast = widget.twin.highContrast;
    _oneStepAtATime = widget.twin.oneStepAtATime;
    _simplifiedLanguage = widget.twin.simplifiedLanguage;
    _haptics = widget.twin.hapticFeedback;
  }

  void _saveProfile() {
    HapticsService.confirmationPulse();
    final updated = AccessibilityTwin(
      id: widget.twin.id,
      language: _language,
      largeText: _largeText,
      highContrast: _highContrast,
      voiceInput: _voiceInput,
      oneStepAtATime: _oneStepAtATime,
      simplifiedLanguage: _simplifiedLanguage,
      hapticFeedback: _haptics,
      preferredInput: _voiceInput ? 'voice' : 'touch',
      preferredOutput: 'voice_and_text',
    );
    widget.onSave(updated);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Accessibility Twin updated successfully!')),
    );
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isHindi = _language == 'Hindi';

    return Scaffold(
      appBar: AppBar(
        title: Text(isHindi ? 'सुलभता प्रोफ़ाइल (Twin)' : 'Your Accessibility Twin'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              isHindi ? 'अपनी बातचीत की प्राथमिकताएं चुनें' : 'Configure Interaction Preferences',
              style: theme.textTheme.headlineMedium?.copyWith(fontSize: 20),
            ),
            const SizedBox(height: 6),
            Text(
              'Your Accessibility Twin describes how you prefer to interact. It is not a medical diagnosis.',
              style: theme.textTheme.bodyMedium?.copyWith(fontSize: 13),
            ),
            const SizedBox(height: 20),

            // Preferred Language
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(isHindi ? 'प्राथमिक भाषा (Language)' : 'Primary Language', style: theme.textTheme.labelLarge),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        _langChoice('Hindi (हिंदी)', 'Hindi', theme),
                        const SizedBox(width: 12),
                        _langChoice('English', 'English', theme),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 14),

            // Interaction Modality Switches
            Card(
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text('Voice-First Input (आवाज़ प्राथमिकता)'),
                    subtitle: const Text('Interact by speaking instead of typing'),
                    value: _voiceInput,
                    onChanged: (val) {
                      HapticsService.tactileClick();
                      setState(() => _voiceInput = val);
                    },
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('One Step at a Time (एक समय में एक सवाल)'),
                    subtitle: const Text('Flatten multi-field forms into single questions'),
                    value: _oneStepAtATime,
                    onChanged: (val) {
                      HapticsService.tactileClick();
                      setState(() => _oneStepAtATime = val);
                    },
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('Simplified Language (सरल भाषा)'),
                    subtitle: const Text('Replace bureaucratic terms with plain words'),
                    value: _simplifiedLanguage,
                    onChanged: (val) {
                      HapticsService.tactileClick();
                      setState(() => _simplifiedLanguage = val);
                    },
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('Large Typography (बड़ा टेक्स्ट)'),
                    subtitle: const Text('Scale text up for higher readability'),
                    value: _largeText,
                    onChanged: (val) {
                      HapticsService.tactileClick();
                      setState(() => _largeText = val);
                    },
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('High Contrast (उच्च कंट्रास्ट)'),
                    subtitle: const Text('Vivid yellow on deep black for maximum clarity'),
                    value: _highContrast,
                    onChanged: (val) {
                      HapticsService.tactileClick();
                      setState(() => _highContrast = val);
                    },
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('Tactile Haptic Feedback (हैप्टिक कंपन)'),
                    subtitle: const Text('Vibrations for clicks and directional cues'),
                    value: _haptics,
                    onChanged: (val) {
                      HapticsService.tactileClick();
                      setState(() => _haptics = val);
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Save Button
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                minimumSize: const Size.fromHeight(54),
                backgroundColor: theme.colorScheme.primary,
                foregroundColor: theme.colorScheme.onPrimary,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              onPressed: _saveProfile,
              child: Text(
                isHindi ? 'सुलभता प्रोफ़ाइल सहेजें' : 'Save Accessibility Twin',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _langChoice(String label, String value, ThemeData theme) {
    final isSelected = _language == value;
    return Expanded(
      child: OutlinedButton(
        style: OutlinedButton.styleFrom(
          backgroundColor: isSelected ? theme.colorScheme.primary.withOpacity(0.2) : Colors.transparent,
          side: BorderSide(
            color: isSelected ? theme.colorScheme.primary : Colors.white24,
            width: isSelected ? 2 : 1,
          ),
          padding: const EdgeInsets.symmetric(vertical: 14),
        ),
        onPressed: () {
          HapticsService.tactileClick();
          setState(() => _language = value);
        },
        child: Text(
          label,
          style: TextStyle(
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            color: isSelected ? theme.colorScheme.primary : Colors.white,
          ),
        ),
      ),
    );
  }
}
