// Sahayak AI — Sign Communication Screen (Demo 3)
// Indian Sign Language (ISL) recognition, MediaPipe hand tracking, and speech output.

import 'package:flutter/material.dart';
import '../models/accessibility_twin.dart';
import '../services/api_service.dart';
import '../services/haptics_service.dart';

class SignTalkScreen extends StatefulWidget {
  final AccessibilityTwin twin;

  const SignTalkScreen({super.key, required this.twin});

  @override
  State<SignTalkScreen> createState() => _SignTalkScreenState();
}

class _SignTalkScreenState extends State<SignTalkScreen> {
  String _detectedSign = 'Waiting for gesture...';
  String _hindiMeaning = 'इशारे की प्रतीक्षा...';
  bool _hasDetected = false;

  void _triggerRecognition() async {
    HapticsService.tactileClick();
    setState(() {
      _detectedSign = 'Tracking hand landmarks...';
    });

    final res = await ApiService.predictSign(widget.twin);

    setState(() {
      _detectedSign = res['sign'] ?? 'HELP';
      _hindiMeaning = res['caption'] ?? 'HELP [सहायता]';
      _hasDetected = true;
    });

    HapticsService.successDoublePulse();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isHindi = widget.twin.language == 'Hindi';

    return Scaffold(
      appBar: AppBar(
        title: Text(isHindi ? 'सांकेतिक भाषा (ISL)' : 'Sign Interpreter (ISL)'),
      ),
      body: Column(
        children: [
          // Simulated Camera Viewport with Hand Landmark Visualizer
          Expanded(
            flex: 3,
            child: Stack(
              alignment: Alignment.center,
              children: [
                Container(
                  color: Colors.black,
                  width: double.infinity,
                  height: double.infinity,
                  child: const Center(
                    child: Icon(
                      Icons.videocam_outlined,
                      size: 72,
                      color: Colors.white24,
                    ),
                  ),
                ),
                // Camera status banner with pulsing red dot
                Positioned(
                  top: 16,
                  left: 16,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.black87,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.redAccent),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircleAvatar(radius: 5, backgroundColor: Colors.redAccent),
                        SizedBox(width: 8),
                        Text(
                          'MEDIAPIPE 3D ACTIVE',
                          style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ),
                ),
                // Hand Landmark Target Grid
                Container(
                  width: 200,
                  height: 240,
                  decoration: BoxDecoration(
                    border: Border.all(color: theme.colorScheme.primary.withOpacity(0.6), width: 2),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Center(
                    child: Icon(
                      Icons.pan_tool_outlined,
                      size: 80,
                      color: theme.colorScheme.primary.withOpacity(0.5),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Output & Recognition Panel
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.all(20),
              color: theme.colorScheme.surface,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Column(
                    children: [
                      Text(
                        isHindi ? 'पहचाना गया संकेत (Sign Detected)' : 'Sign Language Recognition',
                        style: theme.textTheme.labelLarge,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _detectedSign,
                        style: theme.textTheme.headlineLarge?.copyWith(
                          color: _hasDetected ? theme.colorScheme.primary : null,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (_hasDetected) ...[
                        const SizedBox(height: 6),
                        Text(
                          _hindiMeaning,
                          style: theme.textTheme.headlineMedium?.copyWith(
                            fontSize: 18,
                            color: Colors.amberAccent,
                          ),
                        ),
                      ],
                    ],
                  ),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size.fromHeight(54),
                      backgroundColor: theme.colorScheme.primary,
                      foregroundColor: theme.colorScheme.onPrimary,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    ),
                    icon: const Icon(Icons.touch_app, size: 28),
                    label: Text(
                      isHindi ? 'संकेत पहचानें (Simulate Sign: HELP)' : 'Recognize Sign (HELP)',
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    onPressed: _triggerRecognition,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
