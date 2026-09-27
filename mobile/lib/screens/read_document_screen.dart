// Sahayak AI — Read & Understand Document Screen (Demo 1)
// Demonstrates OCR, notice comprehension, simplification, and localized speech summary.

import 'package:flutter/material.dart';
import '../models/accessibility_twin.dart';
import '../services/api_service.dart';
import '../services/haptics_service.dart';

class ReadDocumentScreen extends StatefulWidget {
  final AccessibilityTwin twin;

  const ReadDocumentScreen({super.key, required this.twin});

  @override
  State<ReadDocumentScreen> createState() => _ReadDocumentScreenState();
}

class _ReadDocumentScreenState extends State<ReadDocumentScreen> {
  bool _isAnalyzing = false;
  Map<String, dynamic>? _docData;

  @override
  void initState() {
    super.initState();
    _analyzeNotice();
  }

  void _analyzeNotice() async {
    setState(() => _isAnalyzing = true);
    HapticsService.tactileClick();

    final data = await ApiService.readDocument(
      'What is important in this notice?',
      widget.twin,
    );

    setState(() {
      _docData = data;
      _isAnalyzing = false;
    });
    HapticsService.successDoublePulse();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isHindi = widget.twin.language == 'Hindi';

    return Scaffold(
      appBar: AppBar(
        title: Text(isHindi ? 'दस्तावेज़ समझें' : 'Understand Document'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Voice Query Banner
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: theme.colorScheme.primary.withOpacity(0.12),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: theme.colorScheme.primary.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  Icon(Icons.mic, color: theme.colorScheme.primary),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      isHindi ? '"इस नोटिस में क्या ज़रूरी है?"' : '"What is important in this notice?"',
                      style: theme.textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),

            if (_isAnalyzing) ...[
              const SizedBox(height: 40),
              const Center(child: CircularProgressIndicator()),
              const SizedBox(height: 16),
              Center(
                child: Text(
                  isHindi ? 'OCR व दस्तावेज़ का विश्लेषण जारी है...' : 'Running OCR & barrier analysis...',
                  style: theme.textTheme.bodyMedium,
                ),
              ),
            ] else if (_docData != null) ...[
              // Document Title Card
              Card(
                elevation: 3,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.article, color: theme.colorScheme.primary),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              _docData!['title'] ?? 'Notice',
                              style: theme.textTheme.headlineMedium?.copyWith(fontSize: 18),
                            ),
                          ),
                        ],
                      ),
                      const Divider(height: 24),

                      // Deadline Banner
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                          color: Colors.redAccent.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.redAccent.withOpacity(0.4)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.event, color: Colors.redAccent, size: 20),
                            const SizedBox(width: 8),
                            Text(
                              isHindi ? 'अंतिम तिथि: 30 सितंबर 2026' : 'Deadline: September 30, 2026',
                              style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.redAccent),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Required Documents
                      Text(
                        isHindi ? 'आवश्यक दस्तावेज़:' : 'Required Documents:',
                        style: theme.textTheme.labelLarge,
                      ),
                      const SizedBox(height: 8),
                      ...?(_docData!['required_documents'] as List<dynamic>?)?.map(
                        (doc) => Padding(
                          padding: const EdgeInsets.only(bottom: 6.0),
                          child: Row(
                            children: [
                              Icon(Icons.check_circle, size: 16, color: theme.colorScheme.secondary),
                              const SizedBox(width: 8),
                              Expanded(child: Text(doc.toString(), style: theme.textTheme.bodyMedium)),
                            ],
                          ),
                        ),
                      ),

                      // Application Fee & Action Required
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                              decoration: BoxDecoration(
                                color: Colors.green.withOpacity(0.12),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.green.withOpacity(0.3)),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(isHindi ? 'आवेदन शुल्क' : 'Application Fee', style: TextStyle(fontSize: 11, color: Colors.green.shade300, fontWeight: FontWeight.bold)),
                                  const SizedBox(height: 2),
                                  Text(_docData!['application_fee']?.toString() ?? 'NIL (Free)', style: const TextStyle(fontWeight: FontWeight.bold)),
                                ],
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                              decoration: BoxDecoration(
                                color: Colors.blue.withOpacity(0.12),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.blue.withOpacity(0.3)),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(isHindi ? 'कार्रवाई (Action)' : 'Action Required', style: TextStyle(fontSize: 11, color: Colors.blue.shade300, fontWeight: FontWeight.bold)),
                                  const SizedBox(height: 2),
                                  Text(isHindi ? 'ऑनलाइन आवेदन' : 'Apply Online', style: const TextStyle(fontWeight: FontWeight.bold)),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 18),

              // Simplified Spoken Summary Box
              Card(
                color: theme.colorScheme.surface,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.record_voice_over, color: theme.colorScheme.primary),
                          const SizedBox(width: 8),
                          Text(
                            isHindi ? 'सरल भाषा में सारांश' : 'Simplified Summary',
                            style: theme.textTheme.labelLarge,
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(
                        _docData!['display_summary'] ?? '',
                        style: theme.textTheme.bodyLarge?.copyWith(height: 1.5),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Next Action Call to Action
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(54),
                  backgroundColor: theme.colorScheme.primary,
                  foregroundColor: theme.colorScheme.onPrimary,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                icon: const Icon(Icons.arrow_forward),
                label: Text(
                  isHindi ? 'आवेदन फ़ॉर्म भरने में मदद चाहिए' : 'Help Me Fill This Application',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                onPressed: () {
                  Navigator.pushReplacementNamed(context, '/complete');
                },
              ),
            ],
          ],
        ),
      ),
    );
  }
}
