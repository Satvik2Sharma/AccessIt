// Sahayak AI — Home Screen
// Central interface showcasing the 7-stage pipeline and Accessibility Twin summary.

import 'package:flutter/material.dart';
import '../models/accessibility_twin.dart';
import '../services/haptics_service.dart';
import '../services/api_service.dart';
import '../services/voice_service.dart';


class HomeScreen extends StatefulWidget {
  final AccessibilityTwin twin;
  final VoidCallback onToggleTheme;
  final Function(AccessibilityTwin) onUpdateTwin;

  const HomeScreen({
    super.key,
    required this.twin,
    required this.onToggleTheme,
    required this.onUpdateTwin,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final MobileVoiceService _voiceService = MobileVoiceService();
  bool _isListening = false;
  String _voiceStatus = 'Tap the microphone or choose a mode below';

  @override
  void initState() {
    super.initState();
    _voiceService.initialize(language: widget.twin.language);
  }

  void _triggerVoiceCopilot() async {
    HapticsService.confirmationPulse();
    final isHindi = widget.twin.language == 'Hindi';

    if (_isListening) {
      await _voiceService.stopListening();
      setState(() => _isListening = false);
      return;
    }

    if (_voiceService.isAvailable) {
      setState(() {
        _isListening = true;
        _voiceStatus = isHindi ? 'सुन रहा हूँ... बोलिए...' : 'Listening... speak your request...';
      });

      await _voiceService.startListening(
        onResult: (text) {
          if (!mounted) return;
          setState(() {
            _voiceStatus = text;
          });
        },
        onComplete: () {
          if (!mounted) return;
          _handleQuery(_voiceService.lastWords);
        },
      );
    } else {
      // Prompt text input fallback gracefully
      final text = await MobileVoiceService.showTextFallbackDialog(
        context: context,
        title: isHindi ? 'आदेश लिखें (वॉइस अनुपलब्ध)' : 'Enter Query (Voice fallback)',
        hintText: isHindi ? 'जैसे: फ़ॉर्म भरने में मदद करो' : 'e.g. Help me fill scholarship form',
        isHindi: isHindi,
      );

      if (text != null && text.isNotEmpty) {
        _handleQuery(text);
      }
    }
  }

  void _triggerTextInput() async {
    final isHindi = widget.twin.language == 'Hindi';
    final text = await MobileVoiceService.showTextFallbackDialog(
      context: context,
      title: isHindi ? 'निर्देश टाइप करें' : 'Type Command',
      hintText: isHindi ? 'जैसे: फ़ॉर्म भरने में मदद करो' : 'e.g. Help me fill this form',
      isHindi: isHindi,
    );

    if (text != null && text.isNotEmpty) {
      _handleQuery(text);
    }
  }

  void _handleQuery(String query) async {
    if (query.trim().isEmpty) {
      setState(() => _isListening = false);
      return;
    }

    setState(() {
      _isListening = false;
      _voiceStatus = 'Analyzing: "$query"...';
    });

    final intentData = await ApiService.classifyIntent(query, widget.twin);
    final intent = intentData['intent'] ?? 'FORM_COMPLETION';

    if (!mounted) return;
    setState(() {
      _voiceStatus = 'Understood: $intent';
    });

    await _voiceService.speak(
      widget.twin.language == 'Hindi' ? '$intent खोला जा रहा है' : 'Navigating to $intent',
      language: widget.twin.language,
    );
    if (!mounted) return;


    if (intent == 'FORM_COMPLETION') {
      Navigator.pushNamed(context, '/complete');
    } else if (intent == 'UNDERSTAND_DOCUMENT') {
      Navigator.pushNamed(context, '/read');
    } else if (intent == 'COMMUNICATE') {
      Navigator.pushNamed(context, '/sign_talk');
    } else if (intent == 'SEE') {
      Navigator.pushNamed(context, '/see');
    }

  }


  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isHindi = widget.twin.language == 'Hindi';

    return Scaffold(
      appBar: AppBar(
        title: Text(
          isHindi ? 'सहायक AI' : 'SAHAYAK AI',
          style: theme.textTheme.headlineMedium?.copyWith(letterSpacing: 1.2),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(widget.twin.highContrast ? Icons.contrast : Icons.contrast_outlined),
            tooltip: 'Toggle High Contrast',
            onPressed: () {
              HapticsService.tactileClick();
              widget.onToggleTheme();
            },
          ),
          IconButton(
            icon: const Icon(Icons.insights),
            tooltip: 'Accessibility Heatmap',
            onPressed: () => Navigator.pushNamed(context, '/insights'),
          ),
          IconButton(
            icon: const Icon(Icons.person),
            tooltip: 'Accessibility Twin',
            onPressed: () => Navigator.pushNamed(context, '/profile'),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Sign Out',
            onPressed: () async {
              HapticsService.tactileClick();
              await ApiService.logout();
              if (context.mounted) {
                Navigator.pushReplacementNamed(context, '/login');
              }
            },
          ),
        ],
      ),

      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Accessibility Twin Summary Badge
            _buildTwinSummaryCard(theme),
            const SizedBox(height: 24),

            // Prompt Question
            Text(
              isHindi ? 'मैं आपकी क्या मदद करूँ?' : 'How can I help you?',
              textAlign: TextAlign.center,
              style: theme.textTheme.headlineLarge,
            ),
            const SizedBox(height: 8),
            Text(
              _voiceStatus,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyLarge?.copyWith(
                color: _isListening ? theme.colorScheme.primary : null,
                fontWeight: _isListening ? FontWeight.bold : FontWeight.normal,
              ),
            ),
            const SizedBox(height: 24),

            // Large Voice Copilot Button
            Center(
              child: GestureDetector(
                onTap: _triggerVoiceCopilot,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  width: _isListening ? 140 : 120,
                  height: _isListening ? 140 : 120,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _isListening ? Colors.redAccent : theme.colorScheme.primary,
                    boxShadow: [
                      BoxShadow(
                        color: (_isListening ? Colors.redAccent : theme.colorScheme.primary).withOpacity(0.4),
                        blurRadius: 20,
                        spreadRadius: 4,
                      )
                    ],
                  ),
                  child: Icon(
                    _isListening ? Icons.mic : Icons.mic_none,
                    size: 54,
                    color: theme.colorScheme.onPrimary,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),
            Center(
              child: TextButton.icon(
                icon: const Icon(Icons.keyboard, size: 20),
                label: Text(isHindi ? 'या टाइप करके निर्देश दें' : 'Or type text command'),
                onPressed: _triggerTextInput,
              ),
            ),
            const SizedBox(height: 20),


            // Primary Capability Cards (SEE, READ, TALK, COMPLETE)
            _buildModeGrid(theme, isHindi),
          ],
        ),
      ),
    );
  }

  Widget _buildTwinSummaryCard(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.auto_awesome, color: theme.colorScheme.primary, size: 20),
                const SizedBox(width: 8),
                Text(
                  'ACCESSIBILITY TWIN ACTIVE',
                  style: theme.textTheme.labelLarge?.copyWith(fontSize: 13),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: [
                _chip(widget.twin.language, theme),
                if (widget.twin.voiceInput) _chip('Voice Preferred', theme),
                if (widget.twin.largeText) _chip('Large Text', theme),
                if (widget.twin.highContrast) _chip('High Contrast', theme),
                if (widget.twin.oneStepAtATime) _chip('Step-by-Step', theme),
                if (widget.twin.simplifiedLanguage) _chip('Simplified', theme),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _chip(String label, ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: theme.colorScheme.primary.withOpacity(0.15),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: theme.colorScheme.primary.withOpacity(0.4)),
      ),
      child: Text(
        label,
        style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: theme.colorScheme.primary),
      ),
    );
  }

  Widget _buildModeGrid(ThemeData theme, bool isHindi) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _buildActionCard(
                icon: Icons.assignment_turned_in,
                title: isHindi ? 'फ़ॉर्म भरें' : 'COMPLETE',
                subtitle: isHindi ? 'स्टेप-बाय-स्टेप आवेदन' : 'Complete a task or form',
                isHighlight: true,
                onTap: () => Navigator.pushNamed(context, '/complete'),
                theme: theme,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: _buildActionCard(
                icon: Icons.menu_book,
                title: isHindi ? 'पढ़ें' : 'READ',
                subtitle: isHindi ? 'नोटिस और दस्तावेज़ समझें' : 'Understand documents & notices',
                onTap: () => Navigator.pushNamed(context, '/read'),
                theme: theme,
              ),
            ),
          ],
        ),
        const SizedBox(height: 14),
        Row(
          children: [
            Expanded(
              child: _buildActionCard(
                icon: Icons.record_voice_over,
                title: isHindi ? 'बातचीत' : 'TALK',
                subtitle: isHindi ? 'सांकेतिक भाषा (ISL)' : 'Sign Language & Captions',
                onTap: () => Navigator.pushNamed(context, '/talk'),
                theme: theme,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: _buildActionCard(
                icon: Icons.explore,
                title: isHindi ? 'देखें' : 'SEE',
                subtitle: isHindi ? 'वस्तु ढूंढें व दिशा मार्गदर्शन' : 'Find objects & spatial view',
                onTap: () => Navigator.pushNamed(context, '/see'),
                theme: theme,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildActionCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    required ThemeData theme,
    bool isHighlight = false,
  }) {
    return Card(
      elevation: isHighlight ? 4 : 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: isHighlight ? theme.colorScheme.primary : Colors.transparent,
          width: 2,
        ),
      ),
      child: InkWell(
        onTap: () {
          HapticsService.tactileClick();
          onTap();
        },
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon, size: 36, color: theme.colorScheme.primary),
              const SizedBox(height: 12),
              Text(
                title,
                style: theme.textTheme.headlineMedium?.copyWith(fontSize: 18),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: theme.textTheme.bodyMedium?.copyWith(fontSize: 12),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
