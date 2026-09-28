// Sahayak AI — Real Camera Spatial Vision & Object Finding Screen
// Live camera stream, real-time bounding HUD, directional guidance, and haptics.

import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../models/accessibility_twin.dart';
import '../models/camera_analysis.dart';
import '../services/api_service.dart';
import '../services/haptics_service.dart';
import '../services/camera_service.dart';

class SeeScreen extends StatefulWidget {
  final AccessibilityTwin twin;

  const SeeScreen({super.key, required this.twin});

  @override
  State<SeeScreen> createState() => _SeeScreenState();
}

class _SeeScreenState extends State<SeeScreen> with WidgetsBindingObserver {
  final MobileCameraService _cameraService = MobileCameraService();
  final FlutterTts _tts = FlutterTts();

  String _selectedObject = 'bottle';
  String _guidanceText = 'Initializing camera...';
  bool _isAnalyzing = false;
  bool _isLiveScanActive = false;
  CameraDetectedObject? _primaryObject;


  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initTts();
    _initCamera();
  }

  Future<void> _initTts() async {
    final isHindi = widget.twin.language == 'Hindi';
    try {
      await _tts.setLanguage(isHindi ? 'hi-IN' : 'en-US');
      await _tts.setSpeechRate(0.5);
    } catch (_) {}
  }

  Future<void> _speak(String text) async {
    try {
      await _tts.speak(text);
    } catch (_) {}
  }

  Future<void> _initCamera() async {
    final isHindi = widget.twin.language == 'Hindi';
    final ok = await _cameraService.initialize(preferredLens: CameraLensDirection.back);
    if (!mounted) return;

    if (ok) {
      setState(() {
        _guidanceText = isHindi
            ? 'कैमरा तैयार है। लक्ष्य वस्तु चुनें या स्कैन करें।'
            : 'Camera ready. Select an object or tap scan.';
      });
      // Start initial scan with real camera frame
      _scanFrame();
    } else {
      String msg;
      if (_cameraService.state == CameraState.permissionDenied) {
        msg = isHindi
            ? 'कैमरा अनुमति अस्वीकृत। कृपया डिवाइस सेटिंग्स में अनुमति दें।'
            : 'Camera permission denied. Please grant camera access in device settings.';
      } else if (_cameraService.state == CameraState.unavailable) {
        msg = isHindi
            ? 'डिवाइस पर कोई कैमरा उपलब्ध नहीं है।'
            : 'No camera hardware found on this device.';
      } else {
        msg = _cameraService.errorMessage ?? (isHindi ? 'कैमरा प्रारंभ विफल।' : 'Camera initialization failed.');
      }
      setState(() {
        _guidanceText = msg;
        _primaryObject = null;
      });
      _speak(msg);
    }
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (!_cameraService.isReady) return;
    if (state == AppLifecycleState.inactive) {
      _cameraService.pause();
    } else if (state == AppLifecycleState.resumed) {
      _cameraService.resume();
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _cameraService.stopAnalysisLoop();
    _cameraService.dispose();
    _tts.stop();
    super.dispose();
  }

  void _toggleLiveScan() {
    HapticsService.tactileClick();
    setState(() {
      _isLiveScanActive = !_isLiveScanActive;
    });

    if (_isLiveScanActive) {
      _cameraService.startAnalysisLoop(
        fps: 1.0,
        onFrame: (Uint8List bytes) async {
          await _processFrame(bytes);
        },
      );
    } else {
      _cameraService.stopAnalysisLoop();
    }
  }

  Future<void> _scanFrame() async {
    if (_isAnalyzing) return;
    HapticsService.tactileClick();

    if (_cameraService.isReady) {
      final bytes = await _cameraService.captureFrameBytes();
      if (bytes != null && bytes.isNotEmpty) {
        await _processFrame(bytes);
        return;
      }
    }

    if (!mounted) return;
    final isHindi = widget.twin.language == 'Hindi';
    final err = _cameraService.errorMessage ?? (isHindi ? 'कैमरा तैयार नहीं है।' : 'Camera hardware is not ready.');
    setState(() {
      _guidanceText = err;
      _primaryObject = null;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(err),
        backgroundColor: Colors.red.shade800,
      ),
    );
  }

  Future<void> _processFrame(Uint8List frameBytes) async {
    if (!mounted || _isAnalyzing) return;
    setState(() => _isAnalyzing = true);

    final res = await ApiService.analyzeCameraFrame(
      imageBytes: frameBytes,
      twin: widget.twin,
      mode: 'SEE',
      targetObject: _selectedObject,
      query: 'Where is $_selectedObject',
    );

    if (!mounted) return;
    final isHindi = widget.twin.language == 'Hindi';

    CameraDetectedObject? match;
    if (res.objects.isNotEmpty) {
      // Find object matching selected label or top object
      match = res.objects.firstWhere(
        (o) => o.label.toLowerCase().contains(_selectedObject.toLowerCase()),
        orElse: () => res.objects.first,
      );
    }

    setState(() {
      _primaryObject = match;
      if (match != null) {
        _guidanceText = res.guidance.isNotEmpty
            ? res.guidance
            : (isHindi ? '${match.label} ${match.clockDirection} पर है।' : '${match.label} detected at ${match.clockDirection}.');
      } else {
        _guidanceText = res.guidance.isNotEmpty
            ? res.guidance
            : (isHindi ? 'कैमरे में कोई वस्तु नहीं मिली। कृपया कैमरा आगे बढ़ाएं।' : 'No objects detected in camera view. Move camera closer.');
      }
      _isAnalyzing = false;
    });

    final cue = res.hapticCue ?? (match?.relativeDirection.contains('right') == true ? 'PULSE_RIGHT' : 'PULSE_LEFT');
    HapticsService.directionalBuzz(cue);
    _speak(_guidanceText);
  }

  void _findObjectSimulated(String objectName) async {
    // Explicit demo fallback only — labelled clearly as simulated
    setState(() {
      _selectedObject = objectName;
      _guidanceText = 'Demo simulation: Locating $objectName...';
      _isAnalyzing = true;
    });
    HapticsService.tactileClick();

    final res = await ApiService.findObject(objectName, widget.twin);
    if (!mounted) return;

    setState(() {
      _guidanceText = '[DEMO] ${res['display_guidance'] ?? '$objectName found'}';
      _isAnalyzing = false;
      _primaryObject = CameraDetectedObject(
        label: objectName,
        confidence: 0.94,
        clockDirection: "2 o'clock",
        relativeDirection: 'slightly to your right',
        proximity: 'near',
        elevation: 'level',
        bbox: [380.0, 120.0, 520.0, 420.0],
      );
    });

    final haptic = res['haptic_cue'] ?? 'PULSE_RIGHT';
    HapticsService.directionalBuzz(haptic);
    _speak(_guidanceText);
  }

  void _selectObject(String obj) {
    setState(() {
      _selectedObject = obj;
    });
    if (_cameraService.isReady) {
      _scanFrame();
    }
  }

  Future<void> _toggleLens() async {
    HapticsService.tactileClick();
    await _cameraService.toggleLens();
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isHindi = widget.twin.language == 'Hindi';
    final hasCamera = _cameraService.isReady && _cameraService.controller != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isHindi ? 'वस्तु ढूंढें (Real Camera See)' : 'Spatial Vision (Real Camera)'),
        actions: [
          if (_cameraService.hasMultipleCameras)
            IconButton(
              icon: const Icon(Icons.flip_camera_ios),
              tooltip: 'Switch Camera',
              onPressed: _toggleLens,
            ),
        ],
      ),
      body: Column(
        children: [
          // Live Camera Viewport with Spatial HUD Overlay
          Expanded(
            flex: 3,
            child: Stack(
              alignment: Alignment.center,
              children: [
                if (hasCamera)
                  SizedBox.expand(
                    child: FittedBox(
                      fit: BoxFit.cover,
                      child: SizedBox(
                        width: _cameraService.controller!.value.previewSize?.height ?? 1280,
                        height: _cameraService.controller!.value.previewSize?.width ?? 720,
                        child: CameraPreview(_cameraService.controller!),
                      ),
                    ),
                  )
                else
                  Container(
                    color: Colors.black,
                    width: double.infinity,
                    height: double.infinity,
                    padding: const EdgeInsets.all(24),
                    child: Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            _cameraService.state == CameraState.permissionDenied
                                ? Icons.no_photography_outlined
                                : (_cameraService.state == CameraState.initializing
                                    ? Icons.hourglass_top
                                    : Icons.videocam_off_outlined),
                            size: 56,
                            color: Colors.amberAccent,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            _cameraService.errorMessage ?? (isHindi ? 'कैमरा उपलब्ध नहीं है' : 'Camera Hardware Unavailable'),
                            style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: theme.colorScheme.primary,
                              foregroundColor: theme.colorScheme.onPrimary,
                            ),
                            icon: const Icon(Icons.refresh),
                            label: Text(isHindi ? 'कैमरा पुनः प्रारंभ करें' : 'Retry Camera'),
                            onPressed: _initCamera,
                          ),
                          const SizedBox(height: 8),
                          TextButton(
                            onPressed: () => _findObjectSimulated(_selectedObject),
                            child: Text(
                              isHindi ? 'ऑफ़लाइन डेमो चलाएं (परीक्षण)' : 'Run Offline Demo (Simulated)',
                              style: const TextStyle(color: Colors.white60, fontSize: 12),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                // Spatial HUD: Clock and Direction Indicator Header
                Positioned(
                  top: 14,
                  left: 14,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.75),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.white24),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          hasCamera ? Icons.lens : Icons.wifi_tethering,
                          size: 10,
                          color: hasCamera ? Colors.greenAccent : Colors.amberAccent,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          hasCamera
                              ? (_cameraService.currentLensDirection == CameraLensDirection.front ? 'FRONT CAM' : 'REAR CAM')
                              : 'CAMERA OFFLINE',
                          style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                        if (_isLiveScanActive) ...[
                          const SizedBox(width: 8),
                          const CircleAvatar(radius: 4, backgroundColor: Colors.redAccent),
                          const SizedBox(width: 4),
                          const Text('LIVE 1FPS', style: TextStyle(color: Colors.redAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                        ],
                      ],
                    ),
                  ),
                ),

                // Dynamic Object Bounding Target
                if (_primaryObject != null)
                  LayoutBuilder(
                    builder: (context, constraints) {
                      final box = _primaryObject!.bbox;
                      double left = constraints.maxWidth * 0.25;
                      double top = constraints.maxHeight * 0.20;
                      double width = constraints.maxWidth * 0.50;
                      double height = constraints.maxHeight * 0.50;

                      if (box != null && box.length == 4) {
                        if (box[0] <= 1.0 && box[2] <= 1.0) {
                          left = box[0] * constraints.maxWidth;
                          top = box[1] * constraints.maxHeight;
                          width = (box[2] - box[0]) * constraints.maxWidth;
                          height = (box[3] - box[1]) * constraints.maxHeight;
                        } else {
                          left = (box[0] / 640.0) * constraints.maxWidth;
                          top = (box[1] / 480.0) * constraints.maxHeight;
                          width = ((box[2] - box[0]) / 640.0) * constraints.maxWidth;
                          height = ((box[3] - box[1]) / 480.0) * constraints.maxHeight;
                        }
                      }

                      return Positioned(
                        left: left.clamp(10.0, constraints.maxWidth - 100),
                        top: top.clamp(10.0, constraints.maxHeight - 80),
                        width: width.clamp(80.0, constraints.maxWidth - 20),
                        height: height.clamp(60.0, constraints.maxHeight - 20),
                        child: Container(
                          decoration: BoxDecoration(
                            border: Border.all(color: Colors.greenAccent, width: 2.5),
                            borderRadius: BorderRadius.circular(8),
                            color: Colors.greenAccent.withOpacity(0.12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                color: Colors.greenAccent,
                                child: Text(
                                  '${_primaryObject!.label.toUpperCase()} [${_primaryObject!.clockDirection}]',
                                  style: const TextStyle(color: Colors.black, fontSize: 10, fontWeight: FontWeight.bold),
                                ),
                              ),
                              const Spacer(),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                color: Colors.black87,
                                child: Text(
                                  '${_primaryObject!.proximity.toUpperCase()} • ${_primaryObject!.relativeDirection}',
                                  style: const TextStyle(color: Colors.white, fontSize: 9),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),

                // Center Reticle
                IgnorePointer(
                  child: Container(
                    width: 70,
                    height: 70,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.white30, width: 1.5),
                      shape: BoxShape.circle,
                    ),
                    child: const Center(
                      child: Icon(Icons.add, color: Colors.white38, size: 24),
                    ),
                  ),
                ),

                // Analyzing Spinner
                if (_isAnalyzing)
                  Positioned(
                    bottom: 16,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.black87,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: theme.colorScheme.primary),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const SizedBox(
                            width: 14,
                            height: 14,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            isHindi ? 'AI विश्लेषण जारी...' : 'Analyzing Frame...',
                            style: const TextStyle(color: Colors.white, fontSize: 12),
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
              padding: const EdgeInsets.all(16),
              color: theme.colorScheme.surface,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Spatial Guidance Text Card
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: theme.colorScheme.primary.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.directions, color: theme.colorScheme.primary, size: 28),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            _guidanceText,
                            style: theme.textTheme.headlineMedium?.copyWith(fontSize: 15),
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
                      _targetButton('Person (व्यक्ति)', 'person', theme),
                      _targetButton('Chair (कुर्सी)', 'chair', theme),
                    ],
                  ),

                  // Action Buttons: Manual Snapshot & Live Stream Toggle
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          icon: Icon(_isLiveScanActive ? Icons.stop_circle_outlined : Icons.play_circle_outline),
                          label: Text(_isLiveScanActive
                              ? (isHindi ? 'रोकें' : 'Stop Live')
                              : (isHindi ? 'लाइव 1FPS' : 'Live 1FPS')),
                          onPressed: _toggleLiveScan,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: theme.colorScheme.primary,
                            foregroundColor: theme.colorScheme.onPrimary,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          icon: const Icon(Icons.camera_alt),
                          label: Text(isHindi ? 'फ्रेम स्कैन करें' : 'Scan Frame'),
                          onPressed: _scanFrame,
                        ),
                      ),
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
    final isSelected = _selectedObject == obj;
    return InkWell(
      onTap: () => _selectObject(obj),
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? theme.colorScheme.primary : theme.colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(20),

        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: isSelected ? theme.colorScheme.onPrimary : Colors.white,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}
