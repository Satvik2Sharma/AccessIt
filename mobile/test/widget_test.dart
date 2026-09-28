// Flutter widget smoke and authentication navigation tests for Adapt-X

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahayak_ai/main.dart';
import 'package:sahayak_ai/screens/login_screen.dart';
import 'package:sahayak_ai/screens/home_screen.dart';
import 'package:sahayak_ai/models/accessibility_twin.dart';

void main() {
  testWidgets('Adapt-X loads splash screen and displays branding', (WidgetTester tester) async {
    await tester.pumpWidget(const SahayakApp());

    // Verify Adapt-X branding exists on initial splash screen
    expect(find.text('ADAPT-X'), findsOneWidget);
    expect(find.text('Intent-Aware Personal Accessibility Copilot'), findsOneWidget);

    // Advance clock past the splash delay to settle
    await tester.pump(const Duration(milliseconds: 1000));
    await tester.pumpAndSettle();
  });

  testWidgets('LoginScreen renders inputs and judge quick-start personas', (WidgetTester tester) async {
    final twin = AccessibilityTwin(language: 'English');

    await tester.pumpWidget(MaterialApp(
      home: LoginScreen(
        twin: twin,
        onAuthenticated: (_) {},
      ),
    ));

    expect(find.text('Sign In'), findsOneWidget);
    expect(find.text('Create Account'), findsOneWidget);
    expect(find.text('SECURE SIGN IN'), findsOneWidget);
    expect(find.text('JUDGE 1-CLICK PERSONAS'), findsOneWidget);
    expect(find.text('Low Vision & Glare'), findsOneWidget);
    expect(find.text('Motor & Tremor Assistance'), findsOneWidget);
  });

  testWidgets('HomeScreen renders when authenticated', (WidgetTester tester) async {
    final twin = AccessibilityTwin(language: 'Hindi');

    await tester.pumpWidget(MaterialApp(
      home: HomeScreen(
        twin: twin,
        onToggleTheme: () {},
        onUpdateTwin: (_) {},
      ),
    ));

    expect(find.text('सहायक AI'), findsOneWidget);
    expect(find.text('फ़ॉर्म भरें'), findsOneWidget);
    expect(find.text('पढ़ें'), findsOneWidget);
  });
}
