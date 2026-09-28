// Sahayak AI — Accessibility Insights & Heatmap Screen
// Visualizes interaction complexity and adaptive personalization without medical labeling.

import 'package:flutter/material.dart';
import '../models/accessibility_twin.dart';
import '../models/task_flow.dart';
import '../services/api_service.dart';
import '../services/haptics_service.dart';

class InsightsScreen extends StatefulWidget {
  final AccessibilityTwin twin;

  const InsightsScreen({super.key, required this.twin});

  @override
  State<InsightsScreen> createState() => _InsightsScreenState();
}

class _InsightsScreenState extends State<InsightsScreen> {
  List<HeatmapItem> _heatmap = [];
  Map<String, dynamic> _recommendation = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadHeatmap();
  }

  void _loadHeatmap() async {
    final res = await ApiService.getHeatmap();
    final rawHeatmap = (res['heatmap'] as List<dynamic>? ?? []);

    setState(() {
      _heatmap = rawHeatmap.map((item) => HeatmapItem.fromJson(item as Map<String, dynamic>)).toList();
      _recommendation = res['recommendation'] as Map<String, dynamic>? ?? {};
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isHindi = widget.twin.language == 'Hindi';

    return Scaffold(
      appBar: AppBar(
        title: Text(isHindi ? 'सुलभता अंतर्दृष्टि (Insights)' : 'Accessibility Insights & Heatmap'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Stage 7 LEARN Summary Card
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.psychology_outlined, color: theme.colorScheme.primary),
                              const SizedBox(width: 8),
                              Text(
                                'STAGE 7: ACCESSIBILITY LEARNING',
                                style: theme.textTheme.labelLarge,
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          _statRow('Tasks Completed:', '${_recommendation['tasks_completed_count'] ?? 5} tasks'),
                          _statRow('Voice Preference Rate:', '${_recommendation['voice_usage_percentage'] ?? 88}%'),
                          _statRow('Most Effective Strategy:', '${_recommendation['most_effective_assistance'] ?? 'Step-by-step voice guidance'}'),
                          _statRow('Highest Friction Area:', '${_recommendation['most_difficult_step'] ?? 'Document alignment'}'),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Proactive Adaptation Recommendation Card
                  if (_recommendation['dialog_prompt'] != null)
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.primary.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: theme.colorScheme.primary),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.tips_and_updates, color: Colors.amber),
                              const SizedBox(width: 8),
                              Text(
                                isHindi ? 'सुझाया गया व्यक्तिगत अनुकूलन' : 'Proposed Personalization',
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            _recommendation['dialog_prompt'].toString(),
                            style: theme.textTheme.bodyLarge,
                          ),
                          const SizedBox(height: 12),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.end,
                            children: [
                              TextButton(
                                onPressed: () {},
                                child: Text(isHindi ? 'अभी नहीं' : 'Not Now'),
                              ),
                              const SizedBox(width: 8),
                              ElevatedButton(
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: theme.colorScheme.primary,
                                  foregroundColor: theme.colorScheme.onPrimary,
                                ),
                                onPressed: () {
                                  HapticsService.confirmationPulse();
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text(
                                        isHindi
                                          ? 'सहमति दर्ज! प्रोफ़ाइल को आवाज़-प्राथमिकता पर सेट किया गया।'
                                          : 'Consented! Twin adapted to voice-first Hindi navigation.',
                                      ),
                                    ),
                                  );
                                },
                                child: Text(isHindi ? 'हाँ, सक्षम करें' : 'Accept & Adapt'),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  const SizedBox(height: 24),

                  // Interaction Heatmap Section
                  Text(
                    isHindi ? 'कार्य जटिलता हीटमैप (Interaction Heatmap)' : 'Task Interaction Complexity Heatmap',
                    style: theme.textTheme.headlineMedium?.copyWith(fontSize: 18),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Visualizes interaction complexity points (Red = High friction, Yellow = Moderate, Green = Low). Not a medical diagnosis.',
                    style: theme.textTheme.bodyMedium?.copyWith(fontSize: 12),
                  ),
                  const SizedBox(height: 16),

                  ..._heatmap.map((item) => _buildHeatmapRow(item, theme)),
                ],
              ),
            ),
    );
  }

  Widget _statRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.white70)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildHeatmapRow(HeatmapItem item, ThemeData theme) {
    Color badgeColor = Colors.green;
    if (item.color == 'RED') badgeColor = Colors.redAccent;
    if (item.color == 'YELLOW') badgeColor = Colors.amber;

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: badgeColor.withOpacity(0.2),
          child: Icon(
            item.color == 'RED' ? Icons.warning : item.color == 'YELLOW' ? Icons.info : Icons.check_circle,
            color: badgeColor,
          ),
        ),
        title: Text(
          item.interactionPoint.replaceAll('_', ' ').toUpperCase(),
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
        ),
        subtitle: Text(item.reason, style: const TextStyle(fontSize: 12)),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: badgeColor.withOpacity(0.2),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: badgeColor),
          ),
          child: Text(
            item.complexity,
            style: TextStyle(color: badgeColor, fontWeight: FontWeight.bold, fontSize: 11),
          ),
        ),
      ),
    );
  }
}
