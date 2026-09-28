// Sahayak AI — Real-Time Sign Communication Screen (ISL)
// Live front-camera stream, MediaPipe 3D gesture tracking, continuous 1FPS recognition,
// temporal debouncing, speech synthesis, and haptics.

import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../models/accessibility_twin.dart';
import '../services/api_service.dart';
import '../services/haptics_service.dart';
import '../services/camera_service.dart';

class SignTalkScreen extends StatefulWidget {
  final AccessibilityTwin twin;

  const SignTalkScreen({super.key, required this.twin});

  @override
  State<SignTalkScreen> createState() => _SignTalkScreenState();
}

class _SignTalkScreenState extends State<SignTalkScreen> with WidgetsBindingObserver {
  final MobileCameraService _cameraService = MobileCameraService();
  final FlutterTts _tts = FlutterTts();

  String _detectedSign = 'Waiting for gesture...';
  String _caption = 'इशारे की प्रतीक्षा...';
  double _confidence = 0.0;
  bool _hasDetected = false;
  bool _isAnalyzing = false;
  bool _isLiveActive = false;

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
    // Front camera is optimal for signing
    final ok = await _cameraService.initialize(preferredLens: CameraLensDirection.front);
    if (!mounted) return;

    if (ok) {
      setState(() {
        _detectedSign = isHindi ? 'कैमरा चालू है' : 'Camera active';
        _caption = isHindi
            ? 'कृपया हाथ को कैमरे के सामने लाएं'
            : 'Hold hand inside target frame to sign';
      });
      // Start 1FPS live analysis loop automatically
      _startLiveSignStream();
    } else {
      setState(() {
        _detectedSign = isHindi ? 'सिम्युलेटेड मोड' : 'Simulated Mode';
        _caption = isHindi
            ? 'कैमरा उपलब्ध नहीं (बटन दबाकर संकेत पहचानें)'
            : 'Camera unavailable (Use button to recognize sign)';
      });
    }
  }

  void _startLiveSignStream() {
    setState(() => _isLiveActive = true);
    _cameraService.startAnalysisLoop(
      fps: 1.0,
      onFrame: (Uint8List bytes) async {
        await _processSignFrame(bytes);
      },
    );
  }

  void _toggleLive() {
    HapticsService.tactileClick();
    setState(() {
      _isLiveActive = !_isLiveActive;
    });

    if (_isLiveActive) {
      _startLiveSignStream();
    } else {
      _cameraService.stopAnalysisLoop();
    }
  }

  Future<void> _processSignFrame(Uint8List frameBytes) async {
    if (!mounted || _isAnalyzing) return;
    setState(() => _isAnalyzing = true);

    try {
      final res = await ApiService.predictSign(widget.twin, imageBytes: frameBytes);
      if (!mounted) return;

      final sign = res['sign'] ?? 'UNKNOWN';
      final caption = res['caption'] ?? res['hindi_translation'] ?? sign;
      final conf = ((res['confidence'] ?? 0.0) as num).toDouble();
      final spoken = res['spoken_output'] ?? sign;

      if (sign == 'NO_HAND_DETECTED') {
        setState(() {
          _detectedSign = 'No hand detected';
          _caption = widget.twin.language == 'Hindi'
              ? 'कृपया हाथ को कैमरे के सामने लाएं'
              : 'Move your hand into the camera frame.';
          _confidence = 0.0;
          _hasDetected = false;
          _isAnalyzing = false;
        });
        return;
      }

      if (sign == 'UNCERTAIN') {
        setState(() {
          _detectedSign = 'Uncertain gesture';
          _caption = widget.twin.language == 'Hindi'
              ? 'संकेत स्पष्ट नहीं है, हाथ स्थिर रखें'
              : 'Gesture unclear, hold hand steady.';
          _confidence = conf;
          _isAnalyzing = false;
        });
        return;
      }

      final isNewSign = _detectedSign != sign;
      setState(() {
        _detectedSign = sign;
        _caption = caption;
        _confidence = conf;
        _hasDetected = true;
        _isAnalyzing = false;
      });

      if (isNewSign && conf >= 0.5) {
        HapticsService.successDoublePulse();
        _speak(spoken);
      }
    } catch (_) {
      if (mounted) setState(() => _isAnalyzing = false);
    }
  }

  void _triggerManualRecognition() async {
    HapticsService.tactileClick();
    setState(() {
      _isAnalyzing = true;
      _detectedSign = 'Processing gesture...';
    });

    if (_cameraService.isReady) {
      final bytes = await _cameraService.captureFrameBytes();
      if (bytes != null) {
        await _processSignFrame(bytes);
        return;
      }
    }

    // Fallback simulation
    final res = await ApiService.predictSign(widget.twin);
    if (!mounted) return;

    setState(() {
      _detectedSign = res['sign'] ?? 'HELP';
      _caption = res['caption'] ?? 'HELP [सहायता]';
      _confidence = ((res['confidence'] ?? 0.95) as num).toDouble();
      _hasDetected = true;
      _isAnalyzing = false;
    });

    HapticsService.successDoublePulse();
    _speak(res['spoken_output'] ?? 'Help');
  }

  Future<void> _toggleLens() async {
    HapticsService.tactileClick();
    await _cameraService.toggleLens();
    if (mounted) setState(() {});
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

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isHindi = widget.twin.language == 'Hindi';
    final hasCamera = _cameraService.isReady && _cameraService.controller != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isHindi ? 'सांकेतिक भाषा (ISL Live)' : 'Sign Interpreter (ISL Live)'),
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
          // Camera Viewport with Hand Landmark Visualizer Overlay
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
                    child: Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            _cameraService.state == CameraState.initializing
                                ? Icons.hourglass_top
                                : Icons.videocam_off_outlined,
                            size: 64,
                            color: Colors.white24,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            _cameraService.errorMessage ?? 'Simulated Viewport Active',
                            style: const TextStyle(color: Colors.white54, fontSize: 13),
                          ),
                        ],
                      ),
                    ),
                  ),

                // Top Status Badge
                Positioned(
                  top: 14,
                  left: 14,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.black87,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: _isLiveActive ? Colors.greenAccent : Colors.redAccent,
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircleAvatar(
                          radius: 5,
                          backgroundColor: _isLiveActive ? Colors.greenAccent : Colors.redAccent,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          hasCamera
                              ? (_cameraService.currentLensDirection == CameraLensDirection.front ? 'FRONT CAM ACTIVE' : 'REAR CAM ACTIVE')
                              : 'SIMULATED MODE',
                          style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                        if (_isLiveActive) ...[
                          const SizedBox(width: 6),
                          const Text('• 1FPS', style: TextStyle(color: Colors.white70, fontSize: 10)),
                        ],
                      ],
                    ),
                  ),
                ),

                // Hand Landmark Target Box
                IgnorePointer(
                  child: Container(
                    width: 220,
                    height: 260,
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: _hasDetected
                            ? Colors.greenAccent
                            : theme.colorScheme.primary.withOpacity(0.6),
                        width: 2.5,
                      ),
                      borderRadius: BorderRadius.circular(20),
                      color: _hasDetected
                          ? Colors.greenAccent.withOpacity(0.08)
                          : Colors.transparent,
                    ),
                    child: Center(
                      child: Icon(
                        Icons.pan_tool_outlined,
                        size: 72,
                        color: _hasDetected
                            ? Colors.greenAccent.withOpacity(0.6)
                            : theme.colorScheme.primary.withOpacity(0.35),
                      ),
                    ),
                  ),
                ),

                // Live analyzing indicator
                if (_isAnalyzing)
                  Positioned(
                    bottom: 14,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.black87,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const SizedBox(
                            width: 12,
                            height: 12,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            isHindi ? 'संकेत विश्लेषण...' : 'Analyzing Gesture...',
                            style: const TextStyle(color: Colors.white, fontSize: 11),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),

          // Output & Recognition Panel
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.all(16),
              color: theme.colorScheme.surface,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Sign Name & Confidence Card
                  Container(
                    padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 14),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              isHindi ? 'पहचाना गया संकेत' : 'Detected Sign',
                              style: theme.textTheme.labelMedium,
                            ),
                            if (_confidence > 0)
                              Text(
                                '${(_confidence * 100).toInt()}% conf',
                                style: const TextStyle(color: Colors.greenAccent, fontSize: 12, fontWeight: FontWeight.bold),
                              ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(
                          _detectedSign,
                          style: theme.textTheme.headlineMedium?.copyWith(
                            color: _hasDetected ? theme.colorScheme.primary : null,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _caption,
                          style: TextStyle(
                            fontSize: 14,
                            color: _hasDetected ? Colors.amberAccent : Colors.white70,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),

                  // Actions: Toggle Live & Manual Trigger
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          icon: Icon(_isLiveActive ? Icons.pause_circle_outline : Icons.play_circle_outline),
                          label: Text(_isLiveActive
                              ? (isHindi ? 'लाइव रोकें' : 'Pause Live')
                              : (isHindi ? 'लाइव 1FPS' : 'Live 1FPS')),
                          onPressed: _toggleLive,
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
                          icon: const Icon(Icons.touch_app),
                          label: Text(isHindi ? 'संकेत जांचें' : 'Recognize Sign'),
                          onPressed: _triggerManualRecognition,
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
}
