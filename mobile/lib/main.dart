// Adapt-X (Sahayak AI) — Mobile Application Entry Point
// Intent-Aware Personal Accessibility Copilot

import 'package:flutter/material.dart';
import 'models/accessibility_twin.dart';
import 'theme/accessibility_theme.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';
import 'screens/complete_form_screen.dart';
import 'screens/read_document_screen.dart';
import 'screens/sign_talk_screen.dart';
import 'screens/see_screen.dart';
import 'screens/insights_screen.dart';
import 'screens/profile_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const SahayakApp());
}

class SahayakApp extends StatefulWidget {
  const SahayakApp({super.key});

  @override
  State<SahayakApp> createState() => _SahayakAppState();
}

class _SahayakAppState extends State<SahayakApp> {
  // Active Accessibility Twin profile
  AccessibilityTwin _twin = AccessibilityTwin(
    language: 'Hindi',
    largeText: true,
    highContrast: false,
    voiceInput: true,
    oneStepAtATime: true,
    simplifiedLanguage: true,
    hapticFeedback: true,
  );

  void _toggleTheme() {
    setState(() {
      _twin.highContrast = !_twin.highContrast;
    });
  }

  void _updateTwin(AccessibilityTwin newTwin) {
    setState(() {
      _twin = newTwin;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Adapt-X',
      debugShowCheckedModeBanner: false,
      theme: _twin.highContrast
          ? AccessibilityTheme.highContrastTheme(largeText: _twin.largeText)
          : AccessibilityTheme.standardTheme(largeText: _twin.largeText),
      initialRoute: '/splash',
      routes: {
        '/splash': (context) => SplashScreen(
              twin: _twin,
              onAuthenticated: _updateTwin,
            ),
        '/login': (context) => LoginScreen(
              twin: _twin,
              onAuthenticated: _updateTwin,
            ),
        '/home': (context) => HomeScreen(
              twin: _twin,
              onToggleTheme: _toggleTheme,
              onUpdateTwin: _updateTwin,
            ),
        '/complete': (context) => CompleteFormScreen(twin: _twin),
        '/read': (context) => ReadDocumentScreen(twin: _twin),
        '/talk': (context) => SignTalkScreen(twin: _twin),
        '/see': (context) => SeeScreen(twin: _twin),
        '/insights': (context) => InsightsScreen(twin: _twin),
        '/profile': (context) => ProfileScreen(
              twin: _twin,
              onSave: _updateTwin,
            ),
      },
    );
  }
}
