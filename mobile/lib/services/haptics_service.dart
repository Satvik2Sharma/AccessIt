// Sahayak AI — Haptic Feedback Service
// Adapted from SightBuddy tactile feedback patterns.

import 'package:flutter/services.dart';

class HapticsService {
  static void tactileClick() {
    HapticFeedback.lightImpact();
  }

  static void confirmationPulse() {
    HapticFeedback.mediumImpact();
  }

  static void successDoublePulse() {
    HapticFeedback.heavyImpact();
    Future.delayed(const Duration(milliseconds: 150), () {
      HapticFeedback.heavyImpact();
    });
  }

  static void errorPulse() {
    HapticFeedback.heavyImpact();
    Future.delayed(const Duration(milliseconds: 100), () {
      HapticFeedback.mediumImpact();
    });
  }

  static void directionalBuzz(String direction) {
    if (direction.contains('RIGHT')) {
      HapticFeedback.mediumImpact();
    } else if (direction.contains('LEFT')) {
      HapticFeedback.lightImpact();
    } else {
      HapticFeedback.heavyImpact();
    }
  }
}
