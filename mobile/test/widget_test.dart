// Basic Flutter smoke test for SahayakApp

import 'package:flutter_test/flutter_test.dart';
import 'package:sahayak_ai/main.dart';

void main() {
  testWidgets('SahayakApp loads home screen smoke test', (WidgetTester tester) async {
    // Build SahayakApp and trigger a frame.
    await tester.pumpWidget(const SahayakApp());

    // Verify header title exists (Hindi: सहायक AI)
    expect(find.text('सहायक AI'), findsOneWidget);
    expect(find.text('फ़ॉर्म भरें'), findsOneWidget);
    expect(find.text('पढ़ें'), findsOneWidget);
  });
}
