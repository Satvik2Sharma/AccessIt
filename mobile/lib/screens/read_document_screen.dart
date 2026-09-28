// Sahayak AI — Read & Understand Document Screen (Padhe / Read)
// Real device camera viewfinder, snapshot capture, OCR processing,
// document barrier remediation, and localized speech synthesis.

import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../models/accessibility_twin.dart';
import '../services/api_service.dart';
import '../services/haptics_service.dart';
import '../services/camera_service.dart';

class ReadDocumentScreen extends StatefulWidget {
  final AccessibilityTwin twin;

  const ReadDocumentScreen({super.key, required this.twin});

  @override
  State<ReadDocumentScreen> createState() => _ReadDocumentScreenState();
}

class _ReadDocumentScreenState extends State<ReadDocumentScreen> with WidgetsBindingObserver {
  final MobileCameraService _cameraService = MobileCameraService();
  final FlutterTts _tts = FlutterTts();

  bool _isAnalyzing = false;
  Map<String, dynamic>? _docData;
  String _statusText = 'Opening camera...';

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
    setState(() {
      _statusText = isHindi ? 'कैमरा शुरू हो रहा है...' : 'Initializing camera...';
    });

    final ok = await _cameraService.initialize(preferredLens: CameraLensDirection.back);
    if (!mounted) return;

    if (ok) {
      setState(() {
        _statusText = isHindi
            ? 'दस्तावेज़ को कैमरे के सामने रखें और बटन दबाएं।'
            : 'Align document inside frame and tap Capture.';
      });
    } else {
      String err;
      if (_cameraService.state == CameraState.permissionDenied) {
        err = isHindi
            ? 'कैमरा अनुमति अस्वीकृत। कृपया डिवाइस सेटिंग्स में अनुमति दें।'
            : 'Camera permission denied. Please grant camera permission in device settings.';
      } else if (_cameraService.state == CameraState.unavailable) {
        err = isHindi
            ? 'डिवाइस पर कोई कैमरा उपलब्ध नहीं है।'
            : 'No camera hardware found on this device.';
      } else {
        err = _cameraService.errorMessage ?? (isHindi ? 'कैमरा त्रुटि।' : 'Camera initialization failed.');
      }
      setState(() {
        _statusText = err;
      });
      _speak(err);
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
    _cameraService.dispose();
    _tts.stop();
    super.dispose();
  }

  Future<void> _captureAndAnalyze() async {
    if (_isAnalyzing) return;
    HapticsService.tactileClick();

    if (!_cameraService.isReady) {
      final isHindi = widget.twin.language == 'Hindi';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_cameraService.errorMessage ?? (isHindi ? 'कैमरा तैयार नहीं है।' : 'Camera is not ready.')),
          backgroundColor: Colors.red.shade800,
        ),
      );
      return;
    }

    final bytes = await _cameraService.captureFrameBytes();
    if (!mounted) return;
    if (bytes == null || bytes.isEmpty) {
      final isHindi = widget.twin.language == 'Hindi';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(isHindi ? 'फ़्रेम कैप्चर विफल हुआ। पुनः प्रयास करें।' : 'Frame capture failed. Please try again.'),
          backgroundColor: Colors.red.shade800,
        ),
      );
      return;
    }

    setState(() {
      _isAnalyzing = true;
    });

    final data = await ApiService.readDocument(
      'What is important in this notice?',
      widget.twin,
      imageBytes: bytes,
    );

    if (!mounted) return;

    setState(() {
      _docData = data;
      _isAnalyzing = false;
    });

    final isHindi = widget.twin.language == 'Hindi';
    final isUnreadable = data['title'] == 'Unrecognized Document' ||
        data['is_error'] == true ||
        (data['display_summary']?.toString().contains('Could not read') ?? false) ||
        (data['summary_en']?.toString().contains('Could not read') ?? false);

    if (isUnreadable) {
      HapticsService.errorPulse();
      final errText = isHindi
          ? 'दस्तावेज़ को पढ़ा नहीं जा सका। कृपया कैमरे को पास लाएँ या रोशनी में पुनः प्रयास करें।'
          : 'Could not read this document. Please move closer / improve lighting / try again.';
      _speak(errText);
    } else {
      HapticsService.successDoublePulse();
      final summary = data['display_summary'] ?? data['spoken_summary'] ?? '';
      if (summary.isNotEmpty) {
        _speak(summary);
      }
    }
  }

  void _resetToCamera() {
    setState(() {
      _docData = null;
    });
  }

  void _testSampleNotice() async {
    // Explicit sample notice testing (labelled clearly as test)
    setState(() => _isAnalyzing = true);
    HapticsService.tactileClick();

    final data = await ApiService.readDocument(
      'What is important in this notice?',
      widget.twin,
      imageBytes: null,
    );

    if (!mounted) return;
    setState(() {
      _docData = data;
      _isAnalyzing = false;
    });
    HapticsService.successDoublePulse();
    final summary = data['display_summary'] ?? '';
    if (summary.isNotEmpty) _speak(summary);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isHindi = widget.twin.language == 'Hindi';
    final hasCamera = _cameraService.isReady && _cameraService.controller != null;

    final isUnreadable = _docData != null &&
        (_docData!['title'] == 'Unrecognized Document' ||
            _docData!['is_error'] == true ||
            (_docData!['display_summary']?.toString().contains('Could not read') ?? false) ||
            (_docData!['summary_en']?.toString().contains('Could not read') ?? false));

    return Scaffold(
      appBar: AppBar(
        title: Text(isHindi ? 'दस्तावेज़ पढ़ें (Padhe / Read)' : 'Read Document (Padhe / Read)'),
        actions: [
          if (_cameraService.hasMultipleCameras)
            IconButton(
              icon: const Icon(Icons.flip_camera_ios),
              tooltip: 'Switch Camera',
              onPressed: () async {
                await _cameraService.toggleLens();
                if (mounted) setState(() {});
              },
            ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Camera Viewfinder or Captured Preview
            if (_docData == null)
              Container(
                height: 340,
                color: Colors.black,
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
                      Padding(
                        padding: const EdgeInsets.all(24.0),
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
                                _statusText,
                                style: const TextStyle(color: Colors.white, fontSize: 13),
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(height: 16),
                              ElevatedButton.icon(
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: theme.colorScheme.primary,
                                  foregroundColor: theme.colorScheme.onPrimary,
                                ),
                                icon: const Icon(Icons.refresh),
                                label: Text(isHindi ? 'कैमरा पुनः शुरू करें' : 'Retry Camera'),
                                onPressed: _initCamera,
                              ),
                              const SizedBox(height: 8),
                              TextButton(
                                onPressed: _testSampleNotice,
                                child: Text(
                                  isHindi ? 'नमूना नोटिस लोड करें (परीक्षण)' : 'Load Sample Notice (Test)',
                                  style: const TextStyle(color: Colors.white60, fontSize: 12),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                    // Document Alignment Frame Overlay
                    if (hasCamera)
                      Container(
                        margin: const EdgeInsets.all(32),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.tealAccent, width: 2),
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),

                    // Live Indicator
                    Positioned(
                      top: 14,
                      left: 14,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                        decoration: BoxDecoration(
                          color: Colors.black87,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: Colors.white24),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              hasCamera ? Icons.lens : Icons.wifi_off,
                              size: 10,
                              color: hasCamera ? Colors.greenAccent : Colors.amberAccent,
                            ),
                            const SizedBox(width: 6),
                            Text(
                              hasCamera ? 'CAMERA ACTIVE' : 'NO CAMERA',
                              style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                    ),

                    if (_isAnalyzing)
                      Container(
                        color: Colors.black54,
                        child: Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const CircularProgressIndicator(color: Colors.tealAccent),
                              const SizedBox(height: 16),
                              Text(
                                isHindi ? 'OCR व दस्तावेज़ विश्लेषण जारी...' : 'Analyzing document with OCR...',
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
              ),

            // Capture Button Banner (when in camera mode)
            if (_docData == null && !_isAnalyzing)
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: theme.colorScheme.primary,
                    foregroundColor: theme.colorScheme.onPrimary,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  icon: const Icon(Icons.camera_alt, size: 28),
                  label: Text(
                    isHindi ? 'नोटिस स्कैन करें व समझें' : 'Capture & Read Notice',
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  onPressed: _captureAndAnalyze,
                ),
              ),

            // Results Section
            if (_isAnalyzing && _docData != null)
              const Padding(
                padding: EdgeInsets.all(40.0),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (isUnreadable)
              Padding(
                padding: const EdgeInsets.all(20.0),
                child: Card(
                  color: Colors.red.shade900.withOpacity(0.3),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                    side: BorderSide(color: Colors.red.shade700),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Icon(Icons.warning_amber_rounded, size: 48, color: Colors.amberAccent),
                        const SizedBox(height: 12),
                        Text(
                          isHindi
                              ? 'दस्तावेज़ को पढ़ा नहीं जा सका। कृपया कैमरे को पास लाएँ या रोशनी में पुनः प्रयास करें।'
                              : 'Could not read this document. Please move closer / improve lighting / try again.',
                          textAlign: TextAlign.center,
                          style: theme.textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.bold, height: 1.4),
                        ),
                        const SizedBox(height: 20),
                        ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: theme.colorScheme.primary,
                            foregroundColor: theme.colorScheme.onPrimary,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          icon: const Icon(Icons.camera_alt),
                          label: Text(
                            isHindi ? 'पुनः स्कैन करें' : 'Retake Photo',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          onPressed: _resetToCamera,
                        ),
                      ],
                    ),
                  ),
                ),
              )
            else if (_docData != null)
              Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Document Title Card
                    Card(
                      elevation: 3,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.article, color: theme.colorScheme.primary, size: 28),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        _docData!['title'] ?? 'Official Notice',
                                        style: theme.textTheme.headlineMedium?.copyWith(fontSize: 18),
                                      ),
                                      if (_docData!['authority'] != null)
                                        Text(
                                          _docData!['authority'],
                                          style: theme.textTheme.bodySmall?.copyWith(color: Colors.white70),
                                        ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const Divider(height: 24),

                            // Dynamic Deadlines
                            if (_docData!['deadlines'] != null && (_docData!['deadlines'] as List).isNotEmpty) ...[
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
                                    Expanded(
                                      child: Text(
                                        isHindi
                                            ? 'अंतिम तिथि: ${(_docData!['deadlines'] as List).join(", ")}'
                                            : 'Deadline: ${(_docData!['deadlines'] as List).join(", ")}',
                                        style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.redAccent),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(height: 16),
                            ],

                            // Required Documents List
                            if (_docData!['required_documents'] != null && (_docData!['required_documents'] as List).isNotEmpty) ...[
                              Text(
                                isHindi ? 'आवश्यक दस्तावेज़:' : 'Required Documents:',
                                style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.bold),
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
                              const SizedBox(height: 12),
                            ],

                            // Application Fee & Action
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
                                        Text(isHindi ? 'आवेदन शुल्क' : 'Application Fee',
                                            style: TextStyle(fontSize: 11, color: Colors.green.shade300, fontWeight: FontWeight.bold)),
                                        const SizedBox(height: 2),
                                        Text(_docData!['application_fee']?.toString() ?? 'NIL (Free)',
                                            style: const TextStyle(fontWeight: FontWeight.bold)),
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
                                        Text(isHindi ? 'कार्रवाई' : 'Action Required',
                                            style: TextStyle(fontSize: 11, color: Colors.blue.shade300, fontWeight: FontWeight.bold)),
                                        const SizedBox(height: 2),
                                        Text(_docData!['action_required']?.toString() ?? 'Complete application',
                                            style: const TextStyle(fontWeight: FontWeight.bold)),
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
                    const SizedBox(height: 16),

                    // Simplified Summary Box
                    Card(
                      color: theme.colorScheme.surface,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
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
                                  style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.bold),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            Text(
                              _docData!['display_summary'] ?? _docData!['spoken_summary'] ?? '',
                              style: theme.textTheme.bodyLarge?.copyWith(height: 1.5),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Action Buttons
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            style: OutlinedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            icon: const Icon(Icons.camera_alt),
                            label: Text(isHindi ? 'अन्य स्कैन करें' : 'Scan Another'),
                            onPressed: _resetToCamera,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              backgroundColor: theme.colorScheme.primary,
                              foregroundColor: theme.colorScheme.onPrimary,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            icon: const Icon(Icons.arrow_forward),
                            label: Text(
                              isHindi ? 'फ़ॉर्म भरें' : 'Fill Form',
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            onPressed: () {
                              Navigator.pushReplacementNamed(context, '/complete');
                            },
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
