// Sahayak AI — Spatial Vision & Object Finding Screen (Optional Wow Feature)
// Directional object finder and tactile guidance without false millimeter depth claims.

import 'package:flutter/material.dart';
import '../models/accessibility_twin.dart';
import '../services/api_service.dart';
import '../services/haptics_service.dart';

class SeeScreen extends StatefulWidget {
  final AccessibilityTwin twin;

  const SeeScreen({super.key, required this.twin});

  @override
  State<SeeScreen> createState() => _SeeScreenState();
}

class _SeeScreenState extends State<SeeScreen> {
  String _selectedObject = 'bottle';
  String _guidanceText = 'Select an object to locate';

  void _findObject(String objectName) async {
    setState(() {
      _selectedObject = objectName;
      _guidanceText = 'Locating $objectName in scene...';
    });
    HapticsService.tactileClick();

    final res = await ApiService.findObject(objectName, widget.twin);

    setState(() {
      _guidanceText = res['display_guidance'] ?? '$objectName found';
    });

    final haptic = res['haptic_cue'] ?? 'PULSE_RIGHT';
    HapticsService.directionalBuzz(haptic);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isHindi = widget.twin.language == 'Hindi';

    return Scaffold(
      appBar: AppBar(
        title: Text(isHindi ? 'वस्तु ढूंढें (See)' : 'Find Object (Spatial See)'),
      ),
      body: Column(
        children: [
          // Camera Viewport Simulation with Spatial Bounding Target
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
                    child: Icon(Icons.center_focus_strong, size: 80, color: Colors.white24),
                  ),
                ),
                // Simulated Right-Aligned Bounding Box (Bottle on right)
                Positioned(
                  right: 40,
                  top: 100,
                  child: Container(
                    width: 110,
                    height: 180,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.greenAccent, width: 2.5),
                      borderRadius: BorderRadius.circular(10),
                      color: Colors.greenAccent.withOpacity(0.1),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          color: Colors.greenAccent,
                          child: Text(
                            _selectedObject.toUpperCase(),
                            style: const TextStyle(color: Colors.black, fontSize: 10, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Control & Guidance Drawer
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.all(20),
              color: theme.colorScheme.surface,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  // Spatial Guidance Text Card
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: theme.colorScheme.primary.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.directions, color: theme.colorScheme.primary, size: 30),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            _guidanceText,
                            style: theme.textTheme.headlineMedium?.copyWith(fontSize: 16),
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Quick Object Finding Chips
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _targetButton('Bottle (बोतल)', 'bottle', theme),
                      _targetButton('Keys (चाबी)', 'keys', theme),
                      _targetButton('Phone (फोन)', 'phone', theme),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _targetButton(String label, String obj, ThemeData theme) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: _selectedObject == obj ? theme.colorScheme.primary : theme.colorScheme.surface,
        foregroundColor: _selectedObject == obj ? theme.colorScheme.onPrimary : null,
      ),
      onPressed: () => _findObject(obj),
      child: Text(label),
    );
  }
}
