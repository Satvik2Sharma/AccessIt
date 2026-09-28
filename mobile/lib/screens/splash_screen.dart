// Adapt-X — Splash & Session Bootstrap Screen

import 'package:flutter/material.dart';
import '../models/accessibility_twin.dart';
import '../services/api_service.dart';

class SplashScreen extends StatefulWidget {
  final AccessibilityTwin twin;
  final Function(AccessibilityTwin) onAuthenticated;

  const SplashScreen({
    super.key,
    required this.twin,
    required this.onAuthenticated,
  });

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _bootstrapSession();
  }

  void _bootstrapSession() async {
    await Future.delayed(const Duration(milliseconds: 900));

    if (!mounted) return;

    if (ApiService.isAuthenticated) {
      final res = await ApiService.getMe();
      if (!mounted) return;
      if (res['success'] == true && res['data'] != null) {
        final twinData = res['data']['twin'];
        if (twinData != null) {
          final newTwin = AccessibilityTwin(
            id: twinData['id'] ?? widget.twin.id,
            language: twinData['language'] ?? widget.twin.language,
            largeText: twinData['visual']?['large_text'] ?? widget.twin.largeText,
            highContrast: twinData['visual']?['high_contrast'] ?? widget.twin.highContrast,
            voiceInput: twinData['motor']?['voice_input'] ?? widget.twin.voiceInput,
            oneStepAtATime: twinData['comprehension']?['one_step_at_a_time'] ?? widget.twin.oneStepAtATime,
            simplifiedLanguage: twinData['comprehension']?['simplified_language'] ?? widget.twin.simplifiedLanguage,
            hapticFeedback: twinData['haptics']?['enabled'] ?? widget.twin.hapticFeedback,
          );
          widget.onAuthenticated(newTwin);
        }
        Navigator.pushReplacementNamed(context, '/home');
        return;
      }
    }

    // Default to Login screen
    Navigator.pushReplacementNamed(context, '/login');
  }

  @override
  Widget build(BuildContext context) {
    final isHC = widget.twin.highContrast;
    final primaryColor = isHC ? const Color(0xFFFFD600) : const Color(0xFF64B5F6);

    return Scaffold(
      backgroundColor: isHC ? Colors.black : const Color(0xFF0A0E17),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [

            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: primaryColor.withOpacity(0.15),
                shape: BoxShape.circle,
                border: Border.all(color: primaryColor, width: isHC ? 3 : 2),
              ),
              child: Icon(Icons.accessibility_new_rounded, size: 64, color: primaryColor),
            ),
            const SizedBox(height: 24),
            Text(
              'ADAPT-X',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.w900,
                letterSpacing: 3.0,
                color: primaryColor,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Intent-Aware Personal Accessibility Copilot',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w500,
                color: isHC ? Colors.white : Colors.white70,
              ),
            ),
            const SizedBox(height: 36),
            SizedBox(
              width: 32,
              height: 32,
              child: CircularProgressIndicator(
                strokeWidth: 3,
                color: primaryColor,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
