// Sahayak AI — Accessible Design System & Themes

import 'package:flutter/material.dart';

class AccessibilityTheme {
  // Standard Material 3 Theme
  static ThemeData standardTheme({bool largeText = false}) {
    final scale = largeText ? 1.3 : 1.0;
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF1E88E5),
        brightness: Brightness.dark,
        primary: const Color(0xFF64B5F6),
        secondary: const Color(0xFF81C784),
        surface: const Color(0xFF121824),
      ),
      scaffoldBackgroundColor: const Color(0xFF0A0E17),
      textTheme: _buildTextTheme(scale, Colors.white, Colors.white70),
    );
  }

  // High-Contrast Theme (WCAG AAA compliant: Pure Black + Vivid Yellow & Cyan)
  static ThemeData highContrastTheme({bool largeText = true}) {
    final scale = largeText ? 1.4 : 1.15;
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: const ColorScheme.dark(
        primary: Color(0xFFFFD600), // Vivid Yellow
        secondary: Color(0xFF00E5FF), // Vivid Cyan
        surface: Color(0xFF000000),
        error: Color(0xFFFF1744),
        onPrimary: Color(0xFF000000),
        onSurface: Color(0xFFFFFFFF),
      ),
      scaffoldBackgroundColor: const Color(0xFF000000),
      cardTheme: const CardTheme(
        color: Color(0xFF1A1A1A),
        elevation: 6,
      ),
      textTheme: _buildTextTheme(scale, const Color(0xFFFFD600), const Color(0xFFFFFFFF)),
    );
  }

  static TextTheme _buildTextTheme(double scale, Color primaryColor, Color secondaryColor) {
    return TextTheme(
      headlineLarge: TextStyle(
        fontSize: 32 * scale,
        fontWeight: FontWeight.bold,
        color: primaryColor,
        letterSpacing: 0.5,
      ),
      headlineMedium: TextStyle(
        fontSize: 24 * scale,
        fontWeight: FontWeight.w700,
        color: primaryColor,
      ),
      bodyLarge: TextStyle(
        fontSize: 18 * scale,
        fontWeight: FontWeight.w500,
        color: secondaryColor,
        height: 1.4,
      ),
      bodyMedium: TextStyle(
        fontSize: 15 * scale,
        color: secondaryColor,
      ),
      labelLarge: TextStyle(
        fontSize: 16 * scale,
        fontWeight: FontWeight.bold,
        color: primaryColor,
      ),
    );
  }
}
